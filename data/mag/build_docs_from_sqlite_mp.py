import sqlite3
import json
from datetime import datetime
import gzip
from data import DATA_HOME, ItemsPerSecondBar
import multiprocessing as mp
from itertools import groupby

DATA_FOLDER = DATA_HOME / 'mag'
PROC_COUNT = mp.cpu_count()
PROC_COUNT = 1
paper_field_names = {
    'PaperId': 'id',
    'Doi': 'doi',
    'DocType': 'doc_type',
    'OriginalTitle': 'title',
    'BookTitle': 'booktitle',
    'Year': 'year',
    'Date': 'date',
    'Publisher': 'publisher',
    'Volume': 'volume',
    'Issue': 'issue',
    'FirstPage': 'firstpage',
    'LastPage': 'lastpage',
    'OriginalVenue': 'venue',
    'JournalId': 'JournalId',
    'ConferenceSeriesId': 'ConferenceSeriesId',
    'ConferenceInstanceId': 'ConferenceInstanceId',
}


def make_connection():
    return sqlite3.connect(DATA_FOLDER / 'mag.sqlite3', check_same_thread=False)


def count_papers():
    c = make_connection()
    return c.execute('SELECT Count(*) FROM Papers').fetchone()[0]


def generate_author_affiliations(conn, paperid):
    outer_c = conn.cursor()
    # inner_c = row_conn.cursor()
    authors = []
    affiliations = []
    for author, affiliation in outer_c.execute(
            'select PaperId, OriginalAuthor, OriginalAffiliation from PaperAuthorAffiliations where PaperId=? '
            'order by PaperId, AuthorSequenceNumber', (paperid,)):
        authors.append(author)
        affiliations.append(affiliation)
    return authors, affiliations


def yield_lines_from_gziped_references():
    with gzip.open(DATA_FOLDER / 'PaperReferences_sortk2.txt.gz', 'rt') as file:
        for line in file:
            yield line.split()


def generate_citation_from_gzip():
    gen = yield_lines_from_gziped_references()
    for paperid, group in groupby(gen, lambda x: x[1]):
        yield paperid, list(map(lambda x: x[0], group))



def generate_urls(conn, paperid):
    c = conn.cursor()
    for url in c.execute('select SourceUrl from PaperUrls where PaperId=?', (paperid,)):
        yield url[0]


def generate_references(conn, paperid):
    c = conn.cursor()
    for ref in c.execute('select PaperReferenceId from PaperReferences where PaperId=?', (paperid,)):
        yield ref[0]


def generate_cited_by(conn, paperid):
    c = conn.cursor()
    for citation in c.execute('select PaperId from PaperReferences where PaperReferenceId=?', (paperid,)):
        yield citation[0]


def assemble(inp: mp.JoinableQueue, outp: mp.JoinableQueue):
    conn = make_connection()
    print('assembler started, looping')
    journals = dict(conn.execute('select JournalId, DisplayName from Journals'))
    conference_series = dict(conn.execute('select ConferenceSeriesId, DisplayName from ConferenceSeries'))
    conference_instances = dict(conn.execute('select ConferenceInstanceId, DisplayName from ConferenceInstances'))
    cited_by_gen = generate_citation_from_gzip()
    paper_citation_id, paper_citations = next(cited_by_gen)
    for paper in iter(inp.get, 'STOP'):
        paperid = paper['id']
        paper['author'], paper['affiliations'] = generate_author_affiliations(conn, paperid)
        paper['urls'] = list(generate_urls(conn, paperid))
        paper['references'] = list(generate_references(conn, paperid))
        paper['references_count'] = len(paper['references'])
        # paper['resources'] = list(generate_resources(paperid))
        cii = paper.pop('ConferenceInstanceId')
        if type(cii) is int:
            paper['conferenceinstance'] = conference_instances[cii]
        csi = paper.pop('ConferenceSeriesId')
        if type(csi) is int:
            paper['conferenceseries'] = conference_series[csi]
        ji = paper.pop('JournalId')
        if type(ji) is int:
            paper['journal'] = journals[ji]
        if paper_citation_id == paperid:
            # print('found citation information')
            paper['cited_by'] = list(paper_citations)
            paper['cited_by_count'] = len(paper_citations)
            try:
                paper_citation_id, paper_citations = next(cited_by_gen)
            except StopIteration:
                print('citations were finished')
                paper_citation_id = 0
                paper_citations = []
        strip_empty_fields(paper)
        jsonl = json.dumps(paper, ensure_ascii=False) + '\n'
        outp.put(jsonl)
        inp.task_done()
    print('DONE, joining inp')
    inp.task_done()
    inp.join()
    outp.put('STOP')
    print('REALLY DONE')


def strip_empty_fields(dic: dict):
    empty_keys = []
    for k in dic:
        if (isinstance(dic[k], str) or isinstance(dic[k], list)) and 0 == len(dic[k]):
            empty_keys.append(k)
        elif isinstance(dic[k], dict):
            strip_empty_fields(dic[k])
    for k in empty_keys:
        dic.pop(k)


def make_author_affiliation_proc():
    def generate():
        c = make_connection()
        q = 'select PaperId, OriginalAuthor, OriginalAffiliation from PaperAuthorAffiliations ' \
            'order by PaperId, AuthorSequenceNumber'
        for paperid, group in groupby(c.execute(q), lambda x: x[0]):
            # group yields tuples: (paperid, author, affiliation)
            # this map converts it into three lists: [*paperid, *author, *affiliation]
            _, author, affiliation = list(map(list, zip(*group)))
            yield paperid, author, affiliation

    def feed():
        for aa in generate():
            input_queue.put(aa)
        input_queue.put('STOP')
        input_queue.join()

    input_queue = mp.JoinableQueue(maxsize=10_000)
    feeder = mp.Process(target=feed)
    feeder.start()
    return input_queue, feeder


def make_paper_feed_proc():
    def generate():
        c = make_connection()
        fields = ', '.join(paper_field_names)
        new_names = list(paper_field_names.values())
        for paper in c.execute(f'select {fields} from Papers order by PaperId'):
            yield dict(zip(new_names, paper))

    def feed():  # inp: mp.JoinableQueue
        for paper in generate():
            input_queue.put(paper)
        input_queue.put('STOP')
        input_queue.join()

    input_queue = mp.JoinableQueue(maxsize=10_000)
    feeder = mp.Process(target=feed)
    feeder.start()
    return input_queue, feeder


def yield_parallel():
    output_queue = mp.JoinableQueue(maxsize=10_000)
    assemblers = []
    row_count = count_papers()
    print(f'merging {row_count} rows')
    input_queue, feeder = make_paper_feed_proc()
    for i in range(PROC_COUNT):
        proc = mp.Process(target=assemble, args=(input_queue, output_queue))
        proc.start()
        assemblers.append(proc)

    ips = ItemsPerSecondBar('Merging', max=row_count)
    for jsonl in iter(output_queue.get, 'STOP'):
        yield jsonl
        ips.next()
    ips.finish()


def main():
    start = datetime.now()
    print(f'started on {start}')
    with gzip.open('docs.jsonl.gz', 'wb') as out_file:
        for jsonl in yield_parallel():
            out_file.write(jsonl.encode('utf-8'))
    end = datetime.now()
    delta = end - start
    print(f'finished on {end}, took: {delta}')


if __name__ == '__main__':
    main()

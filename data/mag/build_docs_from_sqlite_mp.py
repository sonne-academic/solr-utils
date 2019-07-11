import sqlite3
import json
from datetime import datetime
import gzip
from data import DATA_HOME, ItemsPerSecondBar
import multiprocessing as mp

DATA_FOLDER = DATA_HOME / 'mag'
# conn = sqlite3.connect(DATA_FOLDER / 'mag.sqlite3', check_same_thread=False)
# row_conn = sqlite3.connect(DATA_FOLDER / 'mag.sqlite3', check_same_thread=False)
# row_conn.row_factory = sqlite3.Row


def make_connection():
    return sqlite3.connect(DATA_FOLDER / 'mag.sqlite3', check_same_thread=False)

PROC_COUNT = mp.cpu_count()*2

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


def generate_papers(max_num=100):
    c = make_connection()
    fields = ', '.join(paper_field_names)
    new_names = list(paper_field_names.values())
    ctr = 0
    for paper in c.execute(f'select {fields} from Papers'):
        if ctr > max_num:
            break
        ctr += 1
        yield dict(zip(new_names, paper))


def generate_author_affiliations(conn, paperid):
    outer_c = conn.cursor()
    # inner_c = row_conn.cursor()
    authors = []
    affiliations = []
    for author, affiliation in outer_c.execute(
            'select OriginalAuthor, OriginalAffiliation from PaperAuthorAffiliations where PaperId=? '
            'order by PaperAuthorAffiliations.AuthorSequenceNumber', (paperid,)):
        authors.append(author)
        affiliations.append(affiliation)
    return authors, affiliations
    # for aa in outer_c.execute(
    #         'select * from PaperAuthorAffiliations '
    #         'where PaperId=? '
    #         'order by PaperAuthorAffiliations.AuthorSequenceNumber', (paperid,)):
    #     aa = dict(aa)
    #     if type(aa['AffiliationId']) is int:
    #         affiliation = inner_c.execute(
    #             'select * from Affiliations where AffiliationId=?',
    #             (aa['AffiliationId'],)).fetchone()
    #         aa['Affiliation'] = dict(affiliation)
    #     else:
    #         aa.pop('AffiliationId')
    #     aa['Author'] = dict(inner_c.execute('select * from Authors where AuthorId=?', (aa['AuthorId'],)).fetchone())
    #     yield aa


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
    c = conn.cursor()
    print('assembler started, looping')
    for paper in iter(inp.get, 'STOP'):
        paperid = paper['id']
        paper['author'], paper['affiliations'] = generate_author_affiliations(conn, paperid)
        paper['urls'] = list(generate_urls(conn, paperid))
        paper['cited_by'] = list(generate_cited_by(conn, paperid))
        paper['cited_by_count'] = len(paper['cited_by'])
        paper['references'] = list(generate_references(conn, paperid))
        paper['references_count'] = len(paper['references'])
        # paper['resources'] = list(generate_resources(paperid))
        cii = paper.pop('ConferenceInstanceId')
        if type(cii) is int:
            paper['conferenceinstance'] = c.execute(
                'select DisplayName from ConferenceInstances '
                'where ConferenceInstanceId=?', (cii,)
            ).fetchone()[0]
        csi = paper.pop('ConferenceSeriesId')
        if type(csi) is int:
            paper['conferenceseries'] = c.execute(
                'select DisplayName from ConferenceSeries '
                'where ConferenceSeriesId=?', (csi,)
            ).fetchone()[0]
        ji = paper.pop('JournalId')
        if type(ji) is int:
            paper['journal'] = c.execute(
                'select DisplayName from Journals where JournalId=?', (ji,)
            ).fetchone()[0]
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


def count_papers():
    c = make_connection()
    return c.execute('SELECT Count(*) FROM Papers').fetchone()[0]


def feed(inp: mp.JoinableQueue, count):
    for paper in generate_papers(max_num=count):
        inp.put(paper)
    # print(f'feeding finished after {idx}')
    for i in range(PROC_COUNT):
        inp.put('STOP')
    # print('fed stops, joining queue')
    inp.join()
    # print('joined input queue')


def yield_parallel():
    input_queue = mp.JoinableQueue(maxsize=10_000)
    output_queue = mp.JoinableQueue(maxsize=10_000)
    assemblers = []
    row_count = count_papers()
    for i in range(PROC_COUNT):
        proc = mp.Process(target=assemble, args=(input_queue,output_queue))
        proc.start()
        assemblers.append(proc)

    feeder = mp.Process(target=feed, args=(input_queue, row_count))
    feeder.start()
    ctr = ItemsPerSecondBar('Merging', max=row_count)
    for jsonl in iter(output_queue.get, 'STOP'):
        yield jsonl
        ctr.next()
    ctr.finish()


def main():
    start = datetime.now()
    row_count = count_papers()
    print(f'merging {row_count} rows')
    print(f'started on {start}')
    with gzip.open('docs.jsonl.gz', 'wb') as out_file:
        for jsonl in yield_parallel():
            out_file.write(jsonl.encode('utf-8'))
    end = datetime.now()
    delta = end - start
    print(f'finished on {end}, took: {delta}')


if __name__ == '__main__':
    main()

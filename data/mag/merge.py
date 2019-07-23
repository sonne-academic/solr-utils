from data import mag, ItemsPerSecondBar
import gzip
import sqlite3
import multiprocessing as mp
from heapq import merge
from itertools import compress, groupby
import json
paper_field_names = (
    # original name         use?  new name
    ('PaperId',               1, 'id'),
    ('Rank',                  0, 'rank'),
    ('Doi',                   1, 'doi'),
    ('DocType',               1, 'doc_type'),
    ('PaperTitle',            0, 'paper_title'),
    ('OriginalTitle',         1, 'title'),
    ('BookTitle',             1, 'booktitle'),
    ('Year',                  1, 'year'),
    ('Date',                  1, 'date'),
    ('Publisher',             1, 'publisher'),
    ('JournalId',             1, 'journalid'),
    ('ConferenceSeriesId',    1, 'conferenceseriesid'),
    ('ConferenceInstanceId',  1, 'conferenceinstanceid'),
    ('Volume',                1, 'volume'),
    ('Issue',                 1, 'issue'),
    ('FirstPage',             1, 'firstpage'),
    ('LastPage',              1, 'lastpage'),
    ('ReferenceCount',        0, 'reference_count'),
    ('CitationCount',         0, 'citation_count'),
    ('EstimatedCitation',     0, 'estimated_citation'),
    ('OriginalVenue',         1, 'venue'),
    ('CreatedDate',           0, 'created_date'),
)


def make_connection():
    return sqlite3.connect(mag.DATA_FOLDER / 'mag.sqlite3', check_same_thread=False)


def make_paper_feed_proc():
    def generate():
        c = make_connection()
        fields = ', '.join(old_names)
        q = f'select {fields} from Papers order by PaperId'
        for paper in c.execute(q):
            result = dict(zip(new_names, paper))
            input_queue.put((int(result['id']), result))
        input_queue.put('STOP')
        # input_queue.join()

    old_names, use_flags, new_names = list(map(list, zip(*paper_field_names)))
    new_names = list(compress(new_names, use_flags))
    old_names = list(compress(old_names, use_flags))
    input_queue = mp.Queue(maxsize=10_000)
    feeder = mp.Process(target=generate)
    feeder.start()
    return input_queue, feeder


def make_citation_feed_proc():
    def yield_lines_from_gziped_references():
        path = mag.DATA_FOLDER / 'PaperReferences_sortk2.txt.gz'
        with gzip.open(path, 'rt') as file:
            for line in file:
                yield line.split()

    def generate():
        gen = yield_lines_from_gziped_references()
        for pid, group in groupby(gen, lambda x: x[1]):
            result = list(map(lambda x: x[0], group))
            input_queue.put((int(pid), {'cited_by': result, 'cited_by_count': len(result)}))
        input_queue.put('STOP')
        # input_queue.join()

    input_queue = mp.Queue(maxsize=10_000)
    feeder = mp.Process(target=generate)
    feeder.start()
    return input_queue, feeder


def make_url_feed_proc():
    def generate():
        c = make_connection()
        q = 'select PaperId, SourceUrl from PaperUrls order by PaperId'
        for pid, group in groupby(c.execute(q), lambda x: x[0]):
            result = list(map(lambda x: x[1], group))
            input_queue.put((int(pid), {'urls': result}))
        input_queue.put('STOP')
        # input_queue.join()

    input_queue = mp.Queue(maxsize=10_000)
    feeder = mp.Process(target=generate)
    feeder.start()
    return input_queue, feeder


def make_references_feed_proc():
    def generate():
        c = make_connection()
        q = 'select PaperId, PaperReferenceId from PaperReferences order by PaperId'
        for pid, group in groupby(c.execute(q), lambda x: x[0]):
            result = list(map(lambda x: x[1], group))
            input_queue.put((int(pid), {'references': result, 'references_count': len(result)}))
        input_queue.put('STOP')
        # input_queue.join()

    input_queue = mp.Queue(maxsize=10_000)
    feeder = mp.Process(target=generate)
    feeder.start()
    return input_queue, feeder


def make_author_affiliation_feed_proc():
    def generate():
        c = make_connection()
        q = 'select PaperId, OriginalAuthor, OriginalAffiliation from PaperAuthorAffiliations ' \
            'order by PaperId, AuthorSequenceNumber'
        for pid, group in groupby(c.execute(q), lambda x: x[0]):
            # group yields tuples: (paperid, author, affiliation)
            # this map converts it into three lists: [*paperid, *author, *affiliation]
            _, author, affiliation = list(map(list, zip(*group)))
            input_queue.put((int(pid), {
                'author': author,
                'affiliation': affiliation
            }))
        input_queue.put('STOP')
        # input_queue.join()

    input_queue = mp.Queue(maxsize=10_000)
    feeder = mp.Process(target=generate)
    feeder.start()
    return input_queue, feeder


def count_papers():
    c = make_connection()
    return c.execute('SELECT Count(*) FROM Papers').fetchone()[0]


def strip_empty_fields(dic: dict):
    empty_keys = []
    for k in dic:
        if (isinstance(dic[k], str) or isinstance(dic[k], list)) and 0 == len(dic[k]):
            empty_keys.append(k)
        elif isinstance(dic[k], dict):
            strip_empty_fields(dic[k])
    for k in empty_keys:
        dic.pop(k)


def merge_paper_data():
    def generate():
        conn = make_connection()

        journals = dict(conn.execute('select JournalId, DisplayName from Journals'))
        conference_series = dict(conn.execute('select ConferenceSeriesId, DisplayName from ConferenceSeries'))
        conference_instances = dict(conn.execute('select ConferenceInstanceId, DisplayName from ConferenceInstances'))
        feeder_creators = [
            make_paper_feed_proc,
            make_author_affiliation_feed_proc,
            make_citation_feed_proc,
            make_references_feed_proc,
            make_url_feed_proc
        ]
        procs = []
        queues = []
        iters = []
        for creator in feeder_creators:
            q, p = creator()
            procs.append(p)
            queues.append(q)
            iters.append(iter(q.get, 'STOP'))

        row_count = count_papers()
        ips = ItemsPerSecondBar('Merging', max=row_count)
        for pid, group in groupby(merge(*iters, key=lambda x: x[0]), key=lambda x: x[0]):
            _, paper = next(group)
            for _, remaining in group:
                paper.update(remaining)

            cii = paper.pop('conferenceinstanceid')
            if type(cii) is int:
                paper['conferenceinstance'] = conference_instances[cii]
            csi = paper.pop('conferenceseriesid')
            if type(csi) is int:
                paper['conferenceseries'] = conference_series[csi]
            ji = paper.pop('journalid')
            if type(ji) is int:
                paper['journal'] = journals[ji]
            strip_empty_fields(paper)
            input_queue.put(paper)
            ips.next()
        for i in range(mp.cpu_count()):
            input_queue.put('STOP')

        ips.finish()
    input_queue = mp.Queue(maxsize=10_000)
    feeder = mp.Process(target=generate)
    feeder.start()
    return input_queue, feeder


def encode(inp_q, out_q):
    for paper in iter(inp_q.get, 'STOP'):
        line = json.dumps(paper, ensure_ascii=False) + '\n'
        out_q.put(line.encode('utf-8'))


def main():
    input_queue, feeder = merge_paper_data()
    # output_queue = mp.Queue(maxsize=10_000)
    # encoder_procs = []
    # for i in range(mp.cpu_count()):
    #     p = mp.Process(target=encode, args=(input_queue, output_queue))
    #     p.start()
    #     encoder_procs.append(p)

    with gzip.open(mag.DATA_FOLDER / 'merged.jsonl.gz', 'wb') as outfile:
        for paper in iter(input_queue.get, 'STOP'):
            line = json.dumps(paper, ensure_ascii=False) + '\n'
            outfile.write(line.encode('utf-8'))


if __name__ == '__main__':
    main()

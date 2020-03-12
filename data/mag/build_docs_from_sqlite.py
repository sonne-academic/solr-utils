import sqlite3
import json
from datetime import datetime
import gzip
from data import DATA_HOME, ItemsPerSecondBar
import collections

DATA_FOLDER = DATA_HOME / 'mag'
conn = sqlite3.connect(DATA_FOLDER / 'mag.sqlite3', check_same_thread=False)
row_conn = sqlite3.connect(DATA_FOLDER / 'mag.sqlite3', check_same_thread=False)
row_conn.row_factory = sqlite3.Row

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


def strip_and_dump_from_gen(generator):
    for data in generator:
        strip_empty_fields(data)
        yield json.dumps(data, ensure_ascii=False)


def row_count(table_name):
    return conn.execute(f'SELECT Count(*) FROM {table_name}').fetchone()[0]


def generate_papers():
    c = row_conn.cursor()
    # row_count = c.execute('SELECT Count(*) FROM Papers').fetchone()[0]
    fields = ', '.join(paper_field_names)
    new_names = list(paper_field_names.values())
    ips = ItemsPerSecondBar('papers', max=row_count('Papers'))
    for paper in c.execute(f'select {fields} from Papers order by PaperId'):
        yield dict(zip(new_names, paper))
        ips.next()
    ips.finish()


def generate_author_affiliation_updates():
    c = conn.cursor()
    authors = []
    affiliations = []
    query = 'select PaperId, OriginalAuthor, OriginalAffiliation ' \
            'from PaperAuthorAffiliations order by PaperId, AuthorSequenceNumber'
    prev_pid = None
    ips = ItemsPerSecondBar('author/affiliations', max=row_count('PaperAuthorAffiliations'))
    for paperid, author, affiliation in c.execute(query):
        if prev_pid is None:
            prev_pid = paperid
        elif prev_pid != paperid:
            yield {'id': prev_pid, 'author': {'set': authors}, 'affiliation': {'set': affiliations}}
            authors = []
            affiliations = []
            prev_pid = paperid
        authors.append(author)
        affiliations.append(affiliation)
        ips.next()
    ips.finish()


def generate_journal_updates():
    c = conn.cursor()
    query = 'select PaperId, J.DisplayName from Papers P inner join Journals J on P.JournalId = J.JournalId'
    ips = ItemsPerSecondBar('journals')
    for paperid, journal in c.execute(query):
        yield {'id': paperid, 'journal': {'set': journal}}
        ips.next()
    ips.finish()


def generate_url_updates():
    c = conn.cursor()
    query = 'select PaperId, SourceUrl from PaperUrls order by PaperId'
    prev_pid = None
    urls = []
    ips = ItemsPerSecondBar('urls', max=row_count('PaperUrls'))
    for paperid, url in c.execute(query):
        if prev_pid is None:
            prev_pid = paperid
        elif prev_pid != paperid:
            yield {'id': prev_pid, 'urls': {'set': urls}}
            urls = []
            prev_pid = paperid
        urls.append(url)
        ips.next()
    ips.finish()


def generate_references_updates():
    c = conn.cursor()
    query = 'select PaperId, PaperReferenceId from PaperReferences order by PaperId'
    prev_pid = None
    refs = []
    ips = ItemsPerSecondBar('references', max=row_count('PaperReferences'))
    for paperid, ref in c.execute(query):
        if prev_pid is None:
            prev_pid = paperid
        elif prev_pid != paperid:
            yield {'id': prev_pid, 'references': {'set': refs}, 'references_count': {'set': len(refs)}}
            refs = []
            prev_pid = paperid
        refs.append(ref)
        ips.next()
    ips.finish()


def generate_cited_by_updates():
    dd = collections.defaultdict(list)
    c = conn.cursor()
    query = 'select PaperReferenceId, PaperId from PaperReferences order by PaperReferenceId'
    # cites = []
    prev_pid = None
    ips = ItemsPerSecondBar('citations', max=row_count('PaperReferences'))
    for paperid, citation in c.execute(query):
        # if prev_pid is None:
        #     prev_pid = paperid
        # elif prev_pid != paperid:
        #     yield {'id': prev_pid, 'cited_by': {'set': cites}, 'cited_by_count': {'set': len(cites)}}
        #     cites = []
        #     prev_pid = paperid
        if len(dd) == 10_000 and paperid not in dd:
            for k, v in dd.items():
                yield {'id': k, 'cited_by': {'set': v}, 'cited_by_count': {'set': len(v)}}
            dd = collections.defaultdict(list)
        dd[paperid].append(citation)
        # cites.append(citation)
        ips.next()
    ips.finish()


UPDATE_GENERATORS = [
    generate_author_affiliation_updates,  # 14.0k/s
    generate_cited_by_updates,            #  1.4k/s
    generate_journal_updates,             #  5,0 k/s
    generate_references_updates,          # 13.0k/s
    generate_url_updates,
]

def generate_resources(paperid):
    c = row_conn.cursor()
    for res in c.execute('select * from PaperResources where PaperId=?', (paperid,)):
        yield dict(res)


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
    c = conn.cursor()
    return c.execute('SELECT Count(*) FROM Papers').fetchone()[0]


def main():
    start = datetime.now()
    row_count = count_papers()
    print(f'merging {row_count} rows')
    print(f'started on {start}')
    for upd_gen in UPDATE_GENERATORS:
        with gzip.open('/dev/null', 'wb') as out_file:
            for i, val in enumerate(upd_gen()):
                if i >= 100_00:
                    print()
                    break
                out_file.write((json.dumps(val, ensure_ascii=False) + '\n').encode('utf-8'))

    # with gzip.open('docs.jsonl.gz', 'wb') as out_file:
    #     for paper in generate_assembled_papers(row_count):
    #         jsonl = json.dumps(paper, ensure_ascii=False) + '\n'
    #         out_file.write(jsonl.encode('utf-8'))

    end = datetime.now()
    delta = end - start
    print(f'finished on {end}, took: {delta}')


if __name__ == '__main__':
    main()

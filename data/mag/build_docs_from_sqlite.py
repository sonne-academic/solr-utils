import sqlite3
import json
from datetime import datetime
import gzip
import progress.bar
from data import DATA_HOME, ItemsPerSecondBar

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

def generate_papers(max_num=100):
    c = row_conn.cursor()
    fields = ', '.join(paper_field_names)
    new_names = list(paper_field_names.values())
    ctr = 0
    for paper in c.execute(f'select {fields} from Papers'):
        if ctr > max_num:
            break
        ctr += 1
        yield dict(zip(new_names, paper))


def generate_author_affiliations(paperid):
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


def generate_urls(paperid):
    c = conn.cursor()
    for url in c.execute('select SourceUrl from PaperUrls where PaperId=?', (paperid,)):
        yield url[0]


def generate_references(paperid):
    c = conn.cursor()
    for ref in c.execute('select PaperReferenceId from PaperReferences where PaperId=?', (paperid,)):
        yield ref[0]


def generate_cited_by(paperid):
    c = conn.cursor()
    for citation in c.execute('select PaperId from PaperReferences where PaperReferenceId=?', (paperid,)):
        yield citation[0]


def generate_resources(paperid):
    c = row_conn.cursor()
    for res in c.execute('select * from PaperResources where PaperId=?', (paperid,)):
        yield dict(res)


def generate_assembled_papers(max_num=100):
    c = conn.cursor()
    ctr = ItemsPerSecondBar('Merging', max=max_num)
    for paper in generate_papers(max_num):
        paperid = paper['id']
        paper['author'], paper['affiliations'] = generate_author_affiliations(paperid)
        paper['urls'] = list(generate_urls(paperid))
        paper['cited_by'] = list(generate_cited_by(paperid))
        paper['cited_by_count'] = len(paper['cited_by'])
        paper['references'] = list(generate_references(paperid))
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
        ctr.next()
        strip_empty_fields(paper)
        jsonl = json.dumps(paper, ensure_ascii=False) + '\n'
        yield jsonl  # .encode('utf-8')
    ctr.finish()


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

    with gzip.open('docs.jsonl.gz', 'wb') as out_file:
        for paper in generate_assembled_papers(row_count):
            jsonl = json.dumps(paper, ensure_ascii=False) + '\n'
            out_file.write(jsonl.encode('utf-8'))

    end = datetime.now()
    delta = end - start
    print(f'finished on {end}, took: {delta}')


if __name__ == '__main__':
    main()

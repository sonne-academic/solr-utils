import sqlite3
import json

conn = sqlite3.connect('mag.sqlite3', check_same_thread=False)
row_conn = sqlite3.connect('mag.sqlite3', check_same_thread=False)
row_conn.row_factory = sqlite3.Row


def generate_papers():
    c = row_conn.cursor()
    for paper in c.execute('select * from Papers limit 1000;'):
        yield dict(paper)


def generate_author_affiliations(paperid):
    outer_c = row_conn.cursor()
    inner_c = row_conn.cursor()
    for aa in outer_c.execute(
            'select * from PaperAuthorAffiliations '
            'where PaperId=? '
            'order by PaperAuthorAffiliations.AuthorSequenceNumber', (paperid,)):
        aa = dict(aa)
        if type(aa['AffiliationId']) is int:
            affiliation = inner_c.execute('select * from Affiliations where AffiliationId=?',
                                          (aa['AffiliationId'],)).fetchone()
            aa['Affiliation'] = dict(affiliation)
        else:
            aa.pop('AffiliationId')
        aa['Author'] = dict(inner_c.execute('select * from Authors where AuthorId=?', (aa['AuthorId'],)).fetchone())
        yield aa


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


def generate_assembled_papers():
    c = row_conn.cursor()
    for paper in generate_papers():
        paperid = paper['PaperId']
        paper['authors'] = list(generate_author_affiliations(paperid))
        paper['urls'] = list(generate_urls(paperid))
        paper['cited_by'] = list(generate_cited_by(paperid))
        paper['references'] = list(generate_references(paperid))
        paper['resources'] = list(generate_resources(paperid))
        if type(paper['ConferenceInstanceId']) is int:
            paper['ConferenceInstance'] = dict(c.execute(
                'select * from ConferenceInstances '
                'where ConferenceInstanceId=?', (paper['ConferenceInstanceId'],)
            ).fetchone())
        if type(paper['ConferenceSeriesId']) is int:
            paper['ConferenceSeries'] = dict(c.execute(
                'select * from ConferenceSeries '
                'where ConferenceSeriesId=?', (paper['ConferenceSeriesId'],)
            ).fetchone())
        if type(paper['JournalId']) is int:
            paper['Journal'] = dict(c.execute(
                'select * from Journals where JournalId=?', (paper['JournalId'],)
            ).fetchone())
        yield paper


def strip_empty_fields(dic: dict):
    empty_keys = []
    for k in dic:
        if isinstance(dic[k], str) and '' == dic[k]:
            empty_keys.append(k)
        elif isinstance(dic[k], dict):
            strip_empty_fields(dic[k])
    for k in empty_keys:
        dic.pop(k)


def main():
    for paper in generate_assembled_papers():
        strip_empty_fields(paper)
        jsonl=json.dumps(paper, ensure_ascii=False)
        print(jsonl)

if __name__ == '__main__':
    main()

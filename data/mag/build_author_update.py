from typing import Optional, List
import json
from solr.instances import get_localhost_session
from data.mag import generate_paper_author_affiliations, DATA_FOLDER
import gzip
from datetime import datetime
from multiprocessing import Pool, cpu_count
from urllib.parse import quote_from_bytes
from os import fspath, scandir
from sys import intern
from os import DirEntry
s = get_localhost_session()

def get_parallel(generator):
    with Pool(processes=cpu_count()*4) as pool:
        yield from pool.imap(make_update, generator)

def get_authors(authorids: List[str]) -> Optional[list]:
    response = s.collection('mag_authors').get.ids(authorids)
    data = response.json()
    try:
        adata = data['response']['docs']
        authors = {a['AuthorId']: a['DisplayName'] for a in adata}
        return [authors.get(i, 'MISSING_DATA') for i in authorids]
    except KeyError:
        return []


def make_update(tpl):
    paperid, authorids = tpl
    return json.dumps({'PaperId': paperid, 'Author': {'set': get_authors(authorids)}}) + '\n'


def build_updates():
    for paperid, authorids in generate_paper_author_affiliations():
        yield json.dumps({'PaperId': paperid, 'Author': {'set': get_authors(authorids)}}) + '\n'


def write_to_gzip():
    with gzip.open(DATA_FOLDER / 'author_updates.jsonl.gz', 'w') as out_file:
        for content in get_parallel(generate_paper_author_affiliations()):
            out_file.write(content.encode('utf-8'))


if __name__ == '__main__':
    start = datetime.now()
    write_to_gzip()
    end = datetime.now()
    # 564606997 lines
    print(f'took {end-start}')
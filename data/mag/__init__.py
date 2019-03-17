from data import DATA_HOME, read_gzip_lines
import csv
import json
import sys
from data.mag_papers.headers import Authors, Papers

_ENCODING = 'utf-8'
DATA_FOLDER = DATA_HOME / 'mag'
csv.field_size_limit(sys.maxsize)

AUTHORS_FILE = DATA_FOLDER / f'Authors.txt.gz'
PAPERS_FILE = DATA_FOLDER / f'Papers.txt.gz'
REFERENCES_FILE = DATA_FOLDER / f'PaperReferences.txt.gz'


def generate_json_string(headers, generator):
    for line in generator:
        values = line.split('\t')
        values = [v.strip() for v in values]
        thing = dict(zip(headers, values))
        empty=[]
        for k,v in thing.items():
            if v.strip() == '':
                empty.append(k)
        for k in empty:
            thing.pop(k)
        s=json.dumps(thing)
        yield s


def generate_authors():
    yield from generate_json_string(Authors, read_gzip_lines(AUTHORS_FILE, _ENCODING))


def generate_papers():
    yield from generate_json_string(Papers, read_gzip_lines(PAPERS_FILE, _ENCODING))


def generate_reference_updates():
    current_id = None
    references = []
    for line in read_gzip_lines(REFERENCES_FILE, _ENCODING):
        next_id, ref = line.split('\t')
        ref = ref.strip()
        if next_id != current_id:
            if len(references) >0:
                yield json.dumps({'PaperId': current_id, 'References': {'set': references}})
            current_id = next_id
            references = []
        references.append(ref)

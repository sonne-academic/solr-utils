from data import DATA_HOME, read_gzip_lines, ItemsPerSecondBar
import json
import sqlite3
from data.mag.data_classes.paper_author_affiliations import PaperAuthorAffiliation
from data.mag.headers import Authors, Papers, Journals, ConferenceInstances, ConferenceSeries, PaperAuthorAffiliations

_ENCODING = 'utf-8'
ENCODING = 'utf-8'
DATA_FOLDER = DATA_HOME / 'mag'
conn = sqlite3.connect(DATA_FOLDER/'mag.sqlite3', check_same_thread=False)

AUTHORS_FILE = DATA_FOLDER / f'Authors.txt.gz'
PAPERS_FILE = DATA_FOLDER / f'Papers.txt.gz'
PAPERURLS_FILE = DATA_FOLDER / f'PaperUrls.txt.gz'
JOURNALS_FILE = DATA_FOLDER / f'Journals.txt.gz'
REFERENCES_FILE = DATA_FOLDER / f'PaperReferences.txt.gz'
CONF_INST_FILE = DATA_FOLDER / 'ConferenceInstances.txt.gz'
CONF_SERIES_FILE = DATA_FOLDER / 'ConferenceSeries.txt.gz'
PAPER_AUTHOR_FILE = DATA_FOLDER / 'PaperAuthorAffiliations.txt.gz'

AUTHOR_UPDATE_FILE = DATA_FOLDER / f'author_updates.jsonl.gz'
JOURNAL_UPDATE_FILE = DATA_FOLDER / f'journal_updates.jsonl.gz'
CONF_INST_UPDATE_FILE = DATA_FOLDER / f'conference_instance_updates.jsonl.gz'
CONF_SER_UPDATE_FILE = DATA_FOLDER / f'conference_series_updates.jsonl.gz'

DENORM_PAPER_FILE = DATA_FOLDER / f'papers_denormailzed.jsonl.gz'


def read_gzip_lines_utf8(path):
    yield from read_gzip_lines(path, encoding=_ENCODING)


def discard_empty(thing: dict):
    empty = []
    for k, v in thing.items():
        if v == '':
            empty.append(k)
    for k in empty:
        thing.pop(k)


def generate_json_dict(headers, generator):
    for line in generator:
        values = line.split('\t')
        values = [v.strip() for v in values]
        thing = dict(zip(headers, values))

        yield thing


def generate_json_string(headers, generator):
    for thing in generate_json_dict(headers, generator):
        discard_empty(thing)
        s = json.dumps(thing)
        yield s


def generate_authors():
    yield from generate_json_string(Authors, read_gzip_lines(AUTHORS_FILE, _ENCODING))


def generate_papers():
    yield from generate_json_string(Papers, read_gzip_lines(PAPERS_FILE, _ENCODING))


def generate_journals():
    yield from generate_json_string(Journals, read_gzip_lines(JOURNALS_FILE, _ENCODING))


def generate_conference_instances():
    yield from generate_json_string(ConferenceInstances, read_gzip_lines(CONF_INST_FILE, _ENCODING))


def generate_conference_series():
    yield from generate_json_string(ConferenceSeries, read_gzip_lines(CONF_SERIES_FILE, _ENCODING))


def generate_author_updates():
    yield from read_gzip_lines(AUTHOR_UPDATE_FILE, _ENCODING)

def generate_journal_updates():
    yield from read_gzip_lines(JOURNAL_UPDATE_FILE, _ENCODING)

def generate_conference_series_updates():
    yield from read_gzip_lines(CONF_SER_UPDATE_FILE, _ENCODING)

def generate_conference_instance_updates():
    yield from read_gzip_lines(CONF_INST_UPDATE_FILE, _ENCODING)

def generate_denormailzed_papers():
    yield from read_gzip_lines(DENORM_PAPER_FILE, _ENCODING)


def generate_paper_author_affiliations():
    current_paper_id = None
    rels = dict()
    for idx, thing in enumerate(generate_json_dict(PaperAuthorAffiliations, read_gzip_lines(PAPER_AUTHOR_FILE, _ENCODING))):
        if 0 == idx % 10_000:
            print(f'{idx}', end=' ')
        if 0 == idx % 100_000:
            print()
        rel = PaperAuthorAffiliation(**thing)
        if rel.PaperId != current_paper_id:
            if 0 < len(rels):
                yield current_paper_id, [rels[idx].AuthorId for idx in sorted(rels)]
            current_paper_id = rel.PaperId
            rels = dict()
        rels[int(rel.AuthorSequenceNumber)] = rel


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


def generate_url_updates():
    current_id = None
    urls = []
    for line in read_gzip_lines(PAPERURLS_FILE, _ENCODING):
        next_id, _, url = line.split('\t')
        url = url.strip()
        if next_id != current_id:
            if len(urls) >0:
                yield json.dumps({'id': current_id, 'urls': {'set': urls}})
            current_id = next_id
            urls = []
        urls.append(url)


if __name__ == '__main__':
    for idx, rel in enumerate(generate_paper_author_affiliations()):
        if idx == 10:
            exit(0)
        print(rel)

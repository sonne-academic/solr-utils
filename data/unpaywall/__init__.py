from data import DATA_HOME, read_gzip_lines

_DATA = DATA_HOME / 'unpaywall' / 'unpaywall_snapshot_2018-06-21T164548_with_versions.jsonl.gz'
_ENCODING = 'latin-1'

DATA_FOLDER = DATA_HOME / 'unpaywall'


def read_all():
    yield from read_gzip_lines(_DATA, _ENCODING)
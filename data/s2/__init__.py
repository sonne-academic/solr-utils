from data import read_gzip_lines
from data_config import S2_DATA

_ENCODING = 'utf-8'


def file_list():
    for i in range(47):
        yield S2_DATA / f's2-corpus-{i:02d}.gz'


def read_all():
    for filename in file_list():
        yield from read_gzip_lines(filename, _ENCODING)

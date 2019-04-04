from data import DATA_HOME, read_gzip_lines

_ENCODING = 'utf-8'
DATA_FOLDER = DATA_HOME / 's2nex'


def file_list():
    for i in range(47):
        yield DATA_FOLDER / f's2-corpus-{i:02d}.gz'


def read_all():
    for filename in file_list():
        yield from read_gzip_lines(filename, _ENCODING)

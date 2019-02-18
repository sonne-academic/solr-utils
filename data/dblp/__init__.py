from data import DATA_HOME

DATA_FOLDER = DATA_HOME / 'dblp'


def file_list():
    yield DATA_FOLDER / 'dblp-2018-09-01.xml.gz'
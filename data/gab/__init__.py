from data import DATA_HOME


DATA_FOLDER = DATA_HOME / 'gab'


def file_list():
    yield DATA_FOLDER / 'gab_posts_jan_2018.json.gz'


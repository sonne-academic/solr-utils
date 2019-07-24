from data import mag
from solr.instances import get_session
from data import upload_batches_unparsed
from solr.session import SolrSession
from solr.configsets import get_config


def reset_collection(s: SolrSession):
    print('deleting collection')
    print(s.admin.collections.delete('mag.2019-03-22').json())

    print('deleting config')
    print(s.admin.configs.delete('mag').json())

    print('sending latest config')
    print(s.admin.configs.upload('mag.2019-03-22', get_config('mag')).json())

    print('creating collection')
    print(s.admin.collections.create('mag.2019-03-22', 4, 1, 1, 'mag.2019-03-22').json())


if __name__ == '__main__':
    s = get_session('localhost', 8984)

    reset = True
    if reset is True:
        reset_collection(s)
    upload_batches_unparsed(s, 'mag.2019-03-22', mag.read_gzip_lines_utf8(mag.DATA_FOLDER / 'merged.jsonl.gz'))

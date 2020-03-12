from data.mag import generate_authors
from solr.instances import get_session
from data import upload_batches_unparsed
from solr.session import SolrSession
from solr.configsets import get_config


def reset_collection(s: SolrSession):
    print('deleting collection')
    print(s.admin.collections.delete('mag_authors').json())

    print('deleting config')
    print(s.admin.configs.delete('mag_authors').json())

    print('sending latest config')
    print(s.admin.configs.upload('mag_authors', get_config('mag_authors')).json())

    print('creating collection')
    print(s.admin.collections.create('mag_authors', 4, 1, 1, 'mag_authors').json())


if __name__ == '__main__':
    s = get_session('localhost', 8984)

    reset = False
    if reset is True:
        reset_collection(s)
    upload_batches_unparsed(s, 'mag_authors', generate_authors())

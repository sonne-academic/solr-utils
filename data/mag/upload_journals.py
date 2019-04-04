from data.mag import generate_journals
from solr.instances import get_localhost_session
from data import upload_batches_unparsed


def reset_collection(s):
    print('deleting collection')
    print(s.admin.collections.delete('mag_journals').json())

    print('deleting config')
    print(s.admin.configs.delete('mag_journals').json())

    print('sending latest config')
    print(s.admin.configs.upload('mag_journals', '/home/bone/solr/solr/configsets/configs/mag_journals').json())

    print('creating collection')
    print(s.admin.collections.create('mag_journals', 3, 1, 1, 'mag_journals').json())


if __name__ == '__main__':
    s = get_localhost_session()

    reset = True
    if reset is True:
        reset_collection(s)
    upload_batches_unparsed(s,'mag_journals', generate_journals())

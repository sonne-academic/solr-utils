from data.mag import generate_papers
from data import upload_batches_unparsed
from solr.instances import get_localhost_session


def reset_collection(s):
    print('deleting collection')
    print(s.admin.collections.delete('mag_papers').json())

    print('deleting config')
    print(s.admin.configs.delete('mag_papers').json())

    print('sending latest config')
    print(s.admin.configs.upload('mag_papers', '/home/bone/solr/solr/configsets/configs/mag_papers').json())

    print('creating collection')
    print(s.admin.collections.create('mag_papers', 3, 1, 1, 'mag_papers').json())


if __name__ == '__main__':
    batch_size = 10_000
    s = get_localhost_session()

    reset = False
    if reset is True:
        reset_collection(s)
    upload_batches_unparsed(s,'mag_papers',generate_papers())

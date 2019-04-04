from data.mag import generate_conference_series
from solr.instances import get_localhost_session
from data import upload_batches_unparsed

COLLECTION = 'mag_conf_series'
def reset_collection(s):
    print('deleting collection')
    print(s.admin.collections.delete(COLLECTION).json())

    print('deleting config')
    print(s.admin.configs.delete(COLLECTION).json())

    print('sending latest config')
    print(s.admin.configs.upload(COLLECTION, f'/home/bone/solr/solr/configsets/configs/{COLLECTION}').json())

    print('creating collection')
    print(s.admin.collections.create(COLLECTION, 3, 1, 1, COLLECTION).json())


if __name__ == '__main__':
    s = get_localhost_session()

    reset = True
    if reset is True:
        reset_collection(s)
    upload_batches_unparsed(s,COLLECTION, generate_conference_series())

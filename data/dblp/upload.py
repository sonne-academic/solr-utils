from data.dblp.convert import yield_from_gzip
from solr.instances import get_localhost_session


if __name__ == '__main__':
    collection = 'dblp'
    config = 'dblp'
    s = get_localhost_session()
    RESET = False
    if RESET:
        print('deleting collection')
        print(s.admin.collections.delete(collection).json())

        print('deleting config')
        print(s.admin.configs.delete(config).json())

        print('sending latest config')
        print(s.admin.configs.upload(config,f'/home/bone/solr/solr/configsets/configs/{config}').json())

        print('creating collection')
        print(s.admin.collections.create(collection,3,1,1,config).json())

    print('sending documents')
    r = s.collection(collection).update.xml(yield_from_gzip())
    print(r.text)

    print('sending commit')
    r = s.collection(collection).update.xml('<commit/>')
    print(r.text)

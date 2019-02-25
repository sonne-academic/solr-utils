from data.dblp.convert_to_jsonl import yield_from_gzip
from solr.instances import get_localhost_session
from multiprocessing import Pool, cpu_count
import itertools
import json
from datetime import datetime

def parse_json(line):
    parsed = json.loads(line)
    # dblp-2019-02-01.xml.gz contains one set with a duplicate year field
    # this will replace the list with the first value
    try:
        if list is type(parsed['year']):
            parsed['year'] = parsed['year'][0]
    except KeyError:
        pass
    parsed['id'] = parsed.pop('key')
    return json.dumps(parsed)


def batch_jsonl(generator, batchsize):
    """
    creates larger chunks from a genenerator function.

    :param generator: the generator function that yields lines of json
    :param batchsize: the maximum size of the batch
    :return: yields utf-8 encoded bytes
    """
    with Pool(processes=cpu_count()) as pool:
        while True:
            batch = itertools.islice(generator, batchsize)
            batch = '\n'.join(pool.imap(parse_json, batch))
            if 0 < len(batch):
                yield batch.encode('utf-8')
            else:
                break


def upload_parallel(generator, session):
    with Pool(processes=cpu_count()) as pool:
        yield from pool.imap(session.collection('dblp').update.jsonl, generator)



if __name__ == '__main__':
    collection = 'dblp'
    config_local = 'dblp'
    config_online = 'dblp'
    s = get_localhost_session()
    RESET = True
    if RESET:
        print('deleting collection')
        """ {
          'responseHeader': {'status': 0, 'QTime': 201}, 
          'success': {
            'solr2:8983_solr': {'responseHeader': {'status': 0, 'QTime': 19}}, 
            'solr0:8983_solr': {'responseHeader': {'status': 0, 'QTime': 20}}, 
            'solr1:8983_solr': {'responseHeader': {'status': 0, 'QTime': 20}}
          }
        } """
        print(s.admin.collections.delete('dblp').json())

        print('deleting config')
        # {'responseHeader': {'status': 0, 'QTime': 99}}
        print(s.admin.configs.delete('dblp').json())

        print('sending latest config')
        # {'responseHeader': {'status': 0, 'QTime': 148}}
        print(s.admin.configs.upload('dblp','/home/bone/solr/solr/configsets/configs/dblp').json())

        print('creating collection')
        """ {
          'responseHeader': {'status': 0, 'QTime': 1888}, 
          'success': { 
            'solr1:8983_solr': {'responseHeader': {'status': 0, 'QTime': 1299}, 'core': 's2_shard3_replica_n4'}, 
            'solr2:8983_solr': {'responseHeader': {'status': 0, 'QTime': 1300}, 'core': 's2_shard2_replica_n2'}, 
            'solr0:8983_solr': {'responseHeader': {'status': 0, 'QTime': 1303}, 'core': 's2_shard1_replica_n1'}
          }
        } """
        """{
          'responseHeader': {'status': 0, 'QTime': 1804}, 
          'failure': {
            'solr2:8983_solr': "org.apache.solr.client.solrj.impl.HttpSolrClient$RemoteSolrException:Error from server at http://solr2:8983/solr: Error CREATEing SolrCore 'dblp_shard2_replica_n2': Unable to create core [dblp_shard2_replica_n2] Caused by: Unknown fieldType 'text_ngram' specified on field suggest_ngram", 
            'solr1:8983_solr': "org.apache.solr.client.solrj.impl.HttpSolrClient$RemoteSolrException:Error from server at http://solr1:8983/solr: Error CREATEing SolrCore 'dblp_shard1_replica_n1': Unable to create core [dblp_shard1_replica_n1] Caused by: Unknown fieldType 'text_ngram' specified on field suggest_ngram", 
            'solr0:8983_solr': "org.apache.solr.client.solrj.impl.HttpSolrClient$RemoteSolrException:Error from server at http://solr0:8983/solr: Error CREATEing SolrCore 'dblp_shard3_replica_n4': Unable to create core [dblp_shard3_replica_n4] Caused by: Unknown fieldType 'text_ngram' specified on field suggest_ngram"
          }
        }
        """
        print(s.admin.collections.create('dblp',3,1,1,'dblp').json())

    print('sending documents')
    counter = 0
    batch_size = 10_000
    batch_generator = batch_jsonl(yield_from_gzip(),batch_size)
    for response in upload_parallel(batch_generator, s):  # 3922 batches with 10_000 size
        counter += 1
        # {'responseHeader': {'rf': 1, 'status': 0, 'QTime': 2499}}
        d = response.json()
        if d['responseHeader']['status'] != 0:
            print(f'{d}')
        print(f'{counter:4d}', end=' ')
        if counter % 10 == 0:
            print()

    # r = s.collection(collection).update.jsonl(yield_from_gzip())
    # print(r.text)

    print('sending commit')
    r = s.collection(collection).update.xml('<commit/>')
    print(r.text)

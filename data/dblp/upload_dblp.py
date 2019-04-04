from data.dblp.convert_to_jsonl import yield_from_gzip
from solr.instances import get_localhost_session
from multiprocessing import Pool, cpu_count
import itertools
import json
from datetime import datetime
from data import batch_jsonl_parsed
from urllib.parse import urlparse
from code import interact
import re

def rename(dic, old, new):
    try:
        dic[new] = dic.pop(old)
    except KeyError:
        pass

new_names = {
    'pub_type': 'doc_type',
}
count_fields = ['author']

def as_list(parsed, name):
    if name not in parsed:
        return
    if type(parsed[name]) is list:
        return
    l = parsed.pop(name)
    parsed[name] = [l]

convert_to_list = ['author','ee']

doi_re = re.compile(r'.*/(10.[0-9]+(\.[0-9]+)?/.*)')

def find_doi(inp):
    for url in inp:
        if 'doi' not in url:
            continue
        match = doi_re.match(url)
        if not match:
            continue
        groups = match.groups()
        if 0 < len(groups):
            return groups[0]
    return None

def parse_json(line):
    try:
        parsed = json.loads(line)
    except json.decoder.JSONDecodeError as e:
        raise Exception(f'line: {line}')
    # dblp-2019-02-01.xml.gz contains one set with a duplicate year field
    # this will replace the list with the first value
    try:
        if list is type(parsed['year']):
            parsed['year'] = parsed['year'][0]
    except KeyError:
        pass
    for old, new in new_names.items():
        rename(parsed,old,new)
    for field in count_fields:
        parsed[f'{field}_count'] = len(parsed.get(field, []))
    for field in convert_to_list:
        as_list(parsed, field)
    doi = find_doi(parsed.get('ee', []))
    if doi is not None:
        parsed['doi'] = doi

    # for url in parsed.get('ee', []):
    #     u = urlparse(url)
    #     if not u or not u.hostname:
    #         continue
    #     if u.hostname.endswith('doi.org'):
    #         parsed['doi'] = u.path[1:]
    #         break
    #     elif u.hostname == 'doi.ieeecomputersociety.org':
    #         parsed['doi'] = u.path[1:]
    #         break

    # if parsed['key'] == 'series/ais/LimbasiyaA18':
    #     interact('no doi?', local=locals())

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


def maybe_add_field(c, name: str, typ: str):
    response = c.schema.fields.get_single(name)
    if 200 != response.status_code:
        print(f'adding field {name}: {typ}:')
        print(c.schema.fields.add(name, typ).json())
    else:
        print(f'field {name} exists, skipping')

if __name__ == '__main__':
    collection = 'dblp'
    config_local = 'dblp'
    config_online = 'dblp'
    s = get_localhost_session()
    RESET = False
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
        print(s.admin.collections.create('dblp',4,1,1,'dblp').json())

    print('sending documents')
    c = s.collection('dblp')
    maybe_add_field(c, 'doi', 'important_string')
    maybe_add_field(c, 'note', 'important_strings')
    maybe_add_field(c, 'author_count', 'pint')

    counter = 0
    batch_size = 10_000
    batch_generator = batch_jsonl_parsed(yield_from_gzip(), batch_size, parse_json)
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

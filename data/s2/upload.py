from data.s2 import read_all
from solr.instances import get_localhost_session
import itertools
from multiprocessing import Pool, cpu_count
import json


def parse_json(line):
    parsed = json.loads(line)
    authors = []
    try:
        authors = [x.get('name','') for x in parsed.pop('authors')]
    except KeyError:
        pass
    parsed['author'] = authors
    parsed['inCitations_count'] = len(parsed.get('inCitations', []))
    parsed['outCitations_count'] = len(parsed.get('outCitations', []))
    parsed['entities_count'] = len(parsed.get('entities',[]))
    parsed['author_count'] = len(parsed.get('author',[]))
    return json.dumps(parsed)


def batch_jsonl(generator, batchsize):
    with Pool(processes=cpu_count()) as pool:
        while True:
            batch = itertools.islice(generator, batchsize)
            batch = '\n'.join(pool.imap(parse_json, batch))
            if 0 < len(batch):
                yield batch
            else:
                break


if __name__ == '__main__':
    s = get_localhost_session()

    reset = False
    if reset is True:
        print('deleting collection')
        print(s.admin.collections.delete('s2').json())

        print('deleting config')
        print(s.admin.configs.delete('s2').json())

        print('sending latest config')
        print(s.admin.configs.upload('s2','/home/bone/solr/solr/configsets/configs/s2').json())

        print('creating collection')
        print(s.admin.collections.create('s2',3,1,1,'s2').json())

    print('sending documents')
    counter = 0
    for batch in batch_jsonl(read_all(),batch_size):  # 3922 batches with 10_000 size
        counter += 1
        r = s.collection('s2').update.jsonl(batch.encode('utf-8'),commit=True)
        print(f'finished batch {counter:4d}: {r.json()}')

from data.s2 import read_all
from solr.instances import get_localhost_session
import itertools


def batch_jsonl(generator, batchsize):
    while True:
        batch = itertools.islice(generator, batchsize)
        batch = '\n'.join(batch)
        if 0 < len(batch):
            yield batch
        else:
            break


if __name__ == '__main__':
    s = get_localhost_session()

    print('deleting collection')
    print(s.admin.collections.delete('s2').json())

    print('deleting config')
    print(s.admin.configs.delete('s2').json())

    print('sending latest config')
    print(s.admin.configs.upload('s2','/home/bone/thesis/code/solr/configsets/configs/s2').json())

    print('creating collection')
    print(s.admin.collections.create('s2',3,1,1,'s2').json())

    print('sending documents')
    counter = 0
    for batch in batch_jsonl(read_all(),10_000):  # 3922 batches with 10_000 size
        counter += 1
        r = s.collection('s2').update.jsonl(batch.encode('utf-8'),commit=True)
        print(f'finished batch {counter:4d}: {r.json()}')

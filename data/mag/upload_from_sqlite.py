from data.mag.build_docs_from_sqlite import generate_papers, UPDATE_GENERATORS, strip_and_dump_from_gen
from solr.instances import get_session
from data import upload_batches_unparsed
from solr.session import SolrSession
from solr.configsets import get_config
from multiprocessing import Pool, cpu_count
import itertools


def batch_jsonl(generator, batchsize):
    """
    creates larger chunks from a genenerator function.

    :param generator: the generator function that yields lines of json
    :param batchsize: the maximum size of the batch
    :return: yields utf-8 encoded bytes
    """
    while True:
        batch = itertools.islice(generator, batchsize)
        batch = '\n,'.join(batch)
        if 0 < len(batch):
            batch = '['+batch+']'
            yield batch.encode('utf-8')
        else:
            break


def upload_parallel(generator, session):
    with Pool(processes=cpu_count()) as pool:
        yield from pool.imap(session.collection('mag').update.jsonUpdate, generator)


def reset_collection(s: SolrSession):
    print('deleting collection')
    print(s.admin.collections.delete('mag').json())

    print('deleting config')
    print(s.admin.configs.delete('mag').json())

    print('sending latest config')
    print(s.admin.configs.upload('mag', get_config('mag')).json())

    print('creating collection')
    print(s.admin.collections.create('mag', 4, 1, 1, 'mag').json())


def main():
    s = get_session('localhost', 8984)
    reset = False
    if reset is True:
        reset_collection(s)
    upload_batches_unparsed(s, 'mag', strip_and_dump_from_gen(generate_papers()))
    for generator in UPDATE_GENERATORS:
        strip_gen = strip_and_dump_from_gen(generator())
        batch_gen = batch_jsonl(strip_gen, 10_000)
        for response in upload_parallel(batch_gen, s):  # 3922 batches with 10_000 size
            d = response.json()
            if d['responseHeader']['status'] != 0:
                print(f'{d}')


if __name__ == '__main__':
    main()

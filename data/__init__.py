import gzip
import json
from json.decoder import JSONDecodeError
from multiprocessing import Pool, cpu_count
import itertools
from typing import Callable
from data_config import DATA_HOME


def batch_jsonl_parsed(generator, batchsize, parser_fn: Callable[[str], str]):
    """
    creates larger chunks from a genenerator function.

    :param generator: the generator function that yields lines of json
    :param batchsize: the maximum size of the batch
    :param parser_fn: a preprocessor for the json values
    :return: yields utf-8 encoded bytes
    """
    with Pool(processes=cpu_count()) as pool:
        while True:
            batch = itertools.islice(generator, batchsize)
            batch = '\n'.join(pool.imap(parser_fn, batch))
            if 0 < len(batch):
                yield batch.encode('utf-8')
            else:
                break


def batch_jsonl_unparsed(generator, batchsize=10_000):
    """
    creates larger chunks from a genenerator function.

    :param generator: the generator function that yields lines of json
    :param batchsize: the maximum size of the batch
    :return: yields utf-8 encoded bytes
    """
    while True:
        batch = itertools.islice(generator, batchsize)
        batch = '\n'.join(batch)
        if 0 < len(batch):
            yield batch.encode('utf-8')
        else:
            break


def upload_batches_unparsed(session, collection: str, generator):
    print('sending documents')
    counter = 0
    batch_generator = batch_jsonl_unparsed(generator)
    for response in upload_parallel(batch_generator, session, collection):  # 3922 batches with 10_000 size
        counter += 1
        d = response.json()
        if d['responseHeader']['status'] != 0:
            print(f'{d}')
        print(f'{counter:4d}', end=' ')
        if counter % 10 == 0:
            print()
    print('sending commit')
    r = session.collection(collection).update.xml('<commit/>')
    print(r.text)


def read_gzip_lines(file, encoding):
    with gzip.open(file, 'rt', encoding=encoding) as f:
        yield from f


def parse_json(line):
    try:
        return line, json.loads(line)
    except JSONDecodeError:
        print(f'error decoding line: {line}')
        return "{}", {}


def parse_jsonl_parallel(generator, processes=4):
    with Pool(processes=processes) as pool:
        yield from pool.imap(parse_json, generator)


def upload_parallel(generator, session, collection):
    with Pool(processes=cpu_count()*2) as pool:
        yield from pool.imap(session.collection(collection).update.jsonl, generator)

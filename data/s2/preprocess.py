from multiprocessing import Pool, Process
import gzip
import json
from datetime import datetime

from data.s2 import buckets, DATA_FOLDER, file_list
from data.s2.buckets import Writer

input_dir = '/home/bone/thesis/data/s2/'


def read_file(file):
    start_file = datetime.now()

    with gzip.open(file, 'rt', encoding='utf-8') as jsonl:
        yield from jsonl
    delta = datetime.now() - start_file
    print(f'read_file: finished reading {file} after {delta.seconds:4d}s')


def parse_json(line):
    return line, json.loads(line)


def read_parallel(gen):
    with Pool(processes=4) as pool:
        yield from pool.imap(parse_json, gen)


def finalize(procs, writers):
    for writer in writers:
        writer.q.put('STOP')

    print('write_bucket: finished reading, waiting for processes to finish')
    for proc in procs:
        proc.join()
        print(f'write_bucket: process {proc} finished')


def write_buckets():
    counter = 0

    writers = [
        # Writer('year', buckets.year),
        # Writer('authorid', buckets.author_id),
        # Writer('incit', buckets.in_cit),
        # Writer('outcit', buckets.out_cit),
        Writer('id', buckets.s2id),
        Writer('journal', buckets.journal),
        Writer('venue', buckets.venue),
        Writer('source', buckets.source)
        ]
    procs = []

    for writer in writers:
        p = Process(target=writer.run)
        p.start()
        procs.append(p)

    for file in file_list():
        start_file = datetime.now()
        for line, node in read_parallel(read_file(file)):
            for writer in writers:
                writer.push(line, node)
            counter += 1
            if counter % 100000 == 0:
                print(f'write_bucket: counter: {counter:8d}')
        delta = datetime.now() - start_file
        print(f'write_bucket: finished queueing {file} after {delta.seconds:4d}s')

    finalize(procs, writers)


if __name__ == '__main__':
    write_buckets()

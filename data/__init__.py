import gzip
import json
from json.decoder import JSONDecodeError
from pathlib import Path
from multiprocessing import Pool

DATA_HOME = Path.home() / 'thesis' / 'data'

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

import gzip
from collections.abc import Mapping
from multiprocessing import SimpleQueue
from os import mkdir
import math
import re

output_dir = '/storage/thesis/s2'


class Bucket(Mapping):
    def __init__(self, name):
        self.name = name
        self.buckets = dict()
        self.dir = f'{output_dir}/{name}'
        mkdir(self.dir)

    def __getitem__(self, k):
        try:
            return self.buckets[k]
        except KeyError:
            self.buckets[k] = gzip.open(f'{self.dir}/{k}.gz', 'wt', encoding='utf-8')
            return self.buckets[k]

    def __len__(self) -> int:
        return len(self.buckets)

    def __iter__(self):
        return iter(self.buckets)

    def close(self):
        for bucket in self.buckets.values():
            bucket.close()


class Writer:
    def __init__(self, name, bucket_func):
        self.buckets = Bucket(name)
        self.q = SimpleQueue()
        self.get_bucket = bucket_func

    def push(self, line, node):
        self.q.put((line, node))

    def run(self):
        for line, node in iter(self.q.get, 'STOP'):
            self.buckets[self.get_bucket(node)].write(line)
        self.buckets.close()


def year(node):
    return node.get('year', 'none')


def author_id(node):
    try:
        return int(node['authors'][0]['ids'][0]) // 1000000
    except KeyError:
        return 'none'
    except IndexError:
        return 'none'


def three_digit_or_magnitude(count: int):
    if 0 == count:
        return 'none'
    if 1000 > count:
        return str(count)
    return f'e{int(math.log10(count)):02d}'


def out_cit(node):
    try:
        return three_digit_or_magnitude(len(node['outCitations']))
    except KeyError:
        return 'none'


def in_cit(node):
    try:
        return three_digit_or_magnitude(len(node['inCitations']))
    except KeyError:
        return 'none'


not_a_char = re.compile(r'[^a-zA-Z]')


def safe_bucket_name(input: str):
    return not_a_char.sub('_',input)


def first_two_lower_chars_or_XX(input: Mapping, field: str):
    try:
        return safe_bucket_name(str(input[field])[0:2].lower())
    except KeyError:
        return 'XX'

def s2id(node):
    return first_two_lower_chars_or_XX(node, 'id')  # first two chars (16*16==256) open files


def journal(node):
    return first_two_lower_chars_or_XX(node, 'journalName') # first two chars (26*26==676) open files


def venue(node):
    return first_two_lower_chars_or_XX(node, 'venue') # first two chars (26*26==676) open files


def source(node):
    #  sources is either 'medline' or 'dblp'
    try:
        srcs = [str(src).lower() for src in node['sources']]
    except:
        return 'none'
    count = len(srcs)
    if 0 == count:
        return 'none'
    if 1 == count:
        return srcs[0]
    if 2 == count:
        return 'both'
    # idk lol
    return 'idk'

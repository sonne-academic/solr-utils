from data.s2 import read_all
from solr.instances import get_localhost_session
import itertools
from multiprocessing import Pool, cpu_count
import json


"""
export interface Document {
    entities:      string[];
    journalVolume: string; -> volume
    journalPages:  string; -> pages
    pmid:          string;
    year?:         number;
    outCitations:  string[];
    s2Url:         string;
    s2PdfUrl:      string;
    id:            string;
    authors:       Author[]; -> author (string[])
    journalName:   string; -> journal
    paperAbstract: string;
    inCitations:   string[];
    pdfUrls:       string[];
    title:         string;
    doi:           string;
    sources:       Source[];
    doiUrl:        string;
    venue:         string;
}

export interface Author {
    name: string; -> use only this
    ids:  string[]; -> discard this
}

export enum Source {
    Dblp = "DBLP",
    Medline = "Medline",
}

"""

def parse_json(line: str) -> str:
    """
    parse one line of json data, change the names of some fields and add the length of multivalued fields
    :param line: a string containing document as json
    :return: the modified data as string
    """
    parsed = json.loads(line)
    # rename authors to author and discard ids
    try:
        parsed['author'] = [x.get('name', '') for x in parsed.pop('authors')]
    except KeyError:
        pass
    # rename journalName to journal
    try:
        parsed['journal'] = parsed.pop('journalName')
    except KeyError:
        pass
    try:
        parsed['pages'] = parsed.pop('journalPages')
    except KeyError:
        pass
    try:
        parsed['volume'] = parsed.pop('journalVolume')
    except KeyError:
        pass
    try:
        parsed['keywords'] = parsed.pop('entities')
    except KeyError:
        pass

    parsed['inCitations_count'] = len(parsed.get('inCitations', []))
    parsed['outCitations_count'] = len(parsed.get('outCitations', []))
    parsed['keywords_count'] = len(parsed.get('keywords',[]))
    parsed['author_count'] = len(parsed.get('author',[]))
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
    with Pool(processes=1) as pool:
        yield from pool.imap(session.collection('s2').update.jsonl, generator)


if __name__ == '__main__':
    document_count = 219709 + 39*1_000_000
    batch_size = 10_000
    batch_count, rest = divmod(document_count, batch_size)
    if rest>0:
        batch_count += 1

    s = get_localhost_session()

    reset = True
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
    batch_generator = batch_jsonl(read_all(),batch_size)
    for response in upload_parallel(batch_generator, s):  # 3922 batches with 10_000 size
        counter += 1
        print(f'finished batch {counter:4d}: {response.json()}')
    # for batch in batch_generator:
    #     response = s.collection('s2').update.jsonl(batch)
    #     counter += 1
    #     print(f'finished batch {counter:4d}: {response.json()}')
    print('sending commit')
    r = s.collection('s2').update.xml('<commit/>')
    print(r.text)
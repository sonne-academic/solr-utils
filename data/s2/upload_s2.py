from data.s2 import read_all
from data import batch_jsonl_parsed, upload_parallel
from solr.instances import get_localhost_session
import json


"""
export interface Document {
    id:            string;
    year?:         number;
    s2Url:         string; -> source_url
    journalVolume: string; -> volume
    journalPages:  string; -> pages
    title:         string;
    journalName:   string; -> journal
    paperAbstract: string; DELETE
    s2PdfUrl:      string;
    pmid:          string;
    doi:           string;
    venue:         string;
    doiUrl:        string;

    authors:       Author[]; -> author (string[])
    entities:      string[]; -> keywords
    outCitations:  string[]; -> references
    inCitations:   string[]; -> cited_by
    pdfUrls:       string[]; -> urls
    sources:       Source[];
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


def rename(dic, old, new):
    try:
        dic[new] = dic.pop(old)
    except KeyError:
        pass

new_names = {
    'journalName': 'journal',
    'journalPages': 'pages',
    'journalVolume': 'volume',
    'entities': 'keywords',
    's2Url': 'source_url',
    'pdfUrls': 'urls',
    'outCitations': 'references',
    'inCitations': 'cited_by'
}
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
    try:
        parsed.pop('paperAbstract')
    except KeyError:
        pass
    for old, new in new_names.items():
        rename(parsed, old, new)

    parsed['references_count'] = len(parsed.get('references', []))
    parsed['cited_by_count'] = len(parsed.get('cited_by', []))
    parsed['author_count'] = len(parsed.get('author',[]))
    return json.dumps(parsed)


if __name__ == '__main__':
    document_count = 219709 + 39*1_000_000
    batch_size = 10_000
    batch_count, rest = divmod(document_count, batch_size)
    if rest>0:
        batch_count += 1

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
        print(s.admin.collections.create('s2',4,1,1,'s2').json())

    print('sending documents')
    counter = 0
    batch_generator = batch_jsonl_parsed(read_all(),batch_size, parse_json)
    for response in upload_parallel(batch_generator, s, 's2'):  # 3922 batches with 10_000 size
        counter += 1
        d = response.json()
        if d['responseHeader']['status'] != 0:
            print(f'{d}')
        print(f'{counter:4d}', end=' ')
        if counter % 10 == 0:
            print()

    # for batch in batch_generator:
    #     response = s.collection('s2').update.jsonl(batch)
    #     counter += 1
    #     print(f'finished batch {counter:4d}: {response.json()}')
    print('sending commit')
    r = s.collection('s2').update.xml('<commit/>')
    print(r.text)
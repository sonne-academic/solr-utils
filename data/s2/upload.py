from solr.instances import get_session
from data import batch_jsonl_parsed
from solr.session import SolrSession
from solr.configsets import get_config
from data.s2 import read_all
import json
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


def rename(dic, old, new):
    try:
        dic[new] = dic.pop(old)
    except KeyError:
        pass


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
    parsed['author_count'] = len(parsed.get('author', []))
    return json.dumps(parsed)



def reset_collection(s: SolrSession):
    print('deleting collection')
    print(s.admin.collections.delete('s2.2019-01-31').json())

    print('deleting config')
    print(s.admin.configs.delete('s2.2019-01-31').json())

    print('sending latest config')
    print(s.admin.configs.upload('s2.2019-01-31', get_config('s2')).json())

    print('creating collection')
    print(s.admin.collections.create('s2.2019-01-31', 4, 1, 1, 's2.2019-01-31').json())


if __name__ == '__main__':
    s = get_session('localhost', 8984)

    reset = True
    if reset is True:
        reset_collection(s)
    batch_jsonl_parsed(read_all(), 10_000, parse_json)

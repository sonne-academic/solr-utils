from data.mag import generate_denormailzed_papers
from solr.instances import get_localhost_session
from data import batch_jsonl_parsed, upload_parallel
import json

def rename(dic, old, new):
    try:
        dic[new] = dic.pop(old)
    except KeyError:
        pass

def remove(dic, name):
    try:
        dic.pop(name)
    except KeyError:
        pass

remove_names = [
    'PaperTitle',
    'Rank',
    'EstimatedCitation',
    'CreatedDate',
    '_version_'
]
new_names = {
    'PaperId': 'id',
    'Doi': 'doi',
    'DocType': 'doc_type',
    'OriginalTitle': 'title',
    'BookTitle': 'booktitle',
    'Year': 'year',
    'Date': 'date',
    'Publisher': 'publisher',
    'JournalId': 'journalid',
    'Journal': 'journal',
    'ConferenceSeriesId': 'conferenceseriesid',
    'ConferenceInstanceId': 'conferenceinstanceid',
    'Volume': 'volume',
    'Issue': 'issue',
    'FirstPage': 'firstpage',
    'LastPage': 'lastpage',
    'ReferenceCount': 'references_count',
    'References': 'references',
    'CitationCount': 'cited_by_count',
    'OriginalVenue': 'venue',
    'ConferenceSeries': 'conferenceseries',
    'ConferenceInstance': 'conferenceinstance',
    'Author': 'author'
}
def parse_json(line: str) -> str:
    """
    parse one line of json data, change the names of some fields and add the length of multivalued fields
    :param line: a string containing document as json
    :return: the modified data as string
    """
    parsed = json.loads(line)
    # rename authors to author and discard ids
    for i in remove_names:
        remove(parsed,i)
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
    #parsed['cited_by_count'] = len(parsed.get('cited_by', []))
    parsed['author_count'] = len(parsed.get('author',[]))
    return json.dumps(parsed)


def reset_collection(s):
    print('deleting collection')
    print(s.admin.collections.delete('mag').json())

    print('deleting config')
    print(s.admin.configs.delete('mag').json())

    print('sending latest config')
    print(s.admin.configs.upload('mag', '/home/bone/solr/solr/configsets/configs/mag').json())

    print('creating collection')
    print(s.admin.collections.create('mag', 4, 1, 1, 'mag').json())


if __name__ == '__main__':
    s = get_localhost_session()

    reset = False
    if reset is True:
        reset_collection(s)

    batch_size = 10_000

    print('sending documents')
    counter = 0
    batch_generator = batch_jsonl_parsed(generate_denormailzed_papers(),batch_size, parse_json)
    for response in upload_parallel(batch_generator, s, 'mag'):  # 3922 batches with 10_000 size
        counter += 1
        d = response.json()
        if d['responseHeader']['status'] != 0:
            print(f'{d}')
        print(f'{counter:4d}', end=' ')
        if counter % 10 == 0:
            print()

    print('sending commit')
    r = s.collection('s2').update.xml('<commit/>')
    print(r.text)
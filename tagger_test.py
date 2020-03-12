from typing import List

from solr.instances import get_localhost_session
import json
from datetime import datetime
from data_config import DATA_HOME
import ijson

INPUT_FILE = DATA_HOME / 'twitter' / 'id_text_export_tagged.json'
OUTPUT_FILE = DATA_HOME / 'twitter' / 'id_text_export_tagged_no_ascii.json'


def make_tag_dict(input: List[List[any]]):
    try:
        while True:
            k = input.pop(0)
            v = input.pop(0)
            yield k, v
    except IndexError:
        pass


def yield_from_json():
    # start = datetime.now()
    # json_data = ijson.parse(INPUT_FILE.open())
    objects = ijson.items(INPUT_FILE.open(), 'result-set.docs.item')
    # end = datetime.now()
    # print(f'parsed json in: {end-start}')
    for thing in objects:
        if 'EOF' in thing:
            return
        yield thing


def yield_from_json():
    with INPUT_FILE.open() as in_file:
        for line in in_file:
            yield json.loads(line)

def main():
    with open(OUTPUT_FILE, 'wt') as out_file:
        session = get_localhost_session()
        skip_count = 0
        valid_count = 0
        for tweet in yield_from_json():
            # ALL, NO_SUB, LONGEST_DOMINANT_RIGHT
            overlap='NO_SUB'
            data = session.collection('geotaggerNoAscii').tag.tag(tweet['Text'].encode('utf-8'), overlap, ['id', 'location', 'name']).json()
            tags = data['tags']
            if len(tags) == 0:
                skip_count += 1
                continue
            tag_dicts = []
            for tag in tags:
                tag_dicts.append(dict(make_tag_dict(tag)))
            items = data['response']['docs']
            tweet['tags'] = tag_dicts
            tweet['tag_data'] = items
            out_file.write(json.dumps(tweet) + '\n')
            valid_count += 1
            if skip_count+valid_count >= 10:
                break
    print(f'found tags: {valid_count}, skipped: {skip_count}')


if __name__ == '__main__':
    start = datetime.now()
    main()
    end = datetime.now()
    print(f'took my time: {end-start}')


""" single blocking thread, no batching, with ascii folding filter
INPUT_FILE = DATA_HOME / 'twitter' / 'id_text_export.json'
OUTPUT_FILE = DATA_HOME / 'twitter' / 'id_text_export_tagged.json'

/local_home/bone/tcode/solr/venv/bin/python /local_home/bone/tcode/solr/tagger_test.py
found tags: 22199694, skipped: 10602188
took my time: 14:51:04.275767
"""

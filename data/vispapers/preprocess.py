from data.vispapers import read_all, DATA_FOLDER
import json
import gzip


def preprocess():
    with gzip.open(DATA_FOLDER / 'vispapers.jsonl.gz', 'wt', encoding='utf-8') as file:
        for document in read_all():
            file.write(json.dumps(document)+'\n')


if __name__ == '__main__':
    preprocess()
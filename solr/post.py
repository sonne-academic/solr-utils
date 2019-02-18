import requests
import itertools

def batch_jsonl(generator, batchsize):
    while True:
        batch = itertools.islice(generator, batchsize)
        batch = '\n'.join(batch)
        if 0 < len(batch):
            yield batch
        else:
            break


class UpdateSender:
    def __init__(self, solr_url):
        self.solr_url = solr_url
        self.api = requests.Session()

    def send_jsonl(self, core, generator, batchsize=10_000):
        updateRq = f'{self.solr_url}{core}/update/json/docs'
        for batch in batch_jsonl(generator, batchsize):
            resp = self.api.post(f'{updateRq}?commit=false', batch.encode('utf-8'))
            print(resp.text)

        resp = self.api.post(f'{updateRq}?commit=true', '')

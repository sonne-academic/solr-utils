from data.mag import generate_reference_updates
from solr.instances import get_localhost_session
import itertools
from multiprocessing import Pool, cpu_count


def batch_jsonl(generator, batchsize):
    """
    creates larger chunks from a genenerator function.

    :param generator: the generator function that yields lines of json
    :param batchsize: the maximum size of the batch
    :return: yields utf-8 encoded bytes
    """
    while True:
        batch = itertools.islice(generator, batchsize)
        batch = '\n,'.join(batch)
        if 0 < len(batch):
            batch = '['+batch+']'
            yield batch.encode('utf-8')
        else:
            break


def upload_parallel(generator, session):
    with Pool(processes=cpu_count()) as pool:
        yield from pool.imap(session.collection('mag_papers').update.jsonUpdate, generator)


if __name__ == '__main__':
    batch_size = 10_000

    s = get_localhost_session()
    response = s.collection('mag_papers').schema.fields.get_single('References')
    if 200 != response.status_code:
        print('adding field for references:')
        print(s.collection('mag_papers').schema.fields.add('References', 'important_strings').json())

    print('sending documents')
    counter = 0
    batch_generator = batch_jsonl(generate_reference_updates(),batch_size)
    for response in upload_parallel(batch_generator, s):  # 3922 batches with 10_000 size
        counter += 1
        d = response.json()
        if d['responseHeader']['status'] != 0:
            print(f'{d}')
        print(f'{counter:4d}', end=' ')
        if counter % 10 == 0:
            print()

    print('sending commit')
    r = s.collection('mag_papers').update.xml('<commit/>')
    print(r.text)

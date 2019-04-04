import json
from data.mag import generate_paper_author_affiliations_pg, DATA_FOLDER
import gzip
from datetime import datetime
import asyncio
import xapian


WORKER_COUNT = 8

PATH = '/home/bone/data/thesis/data/mag'
dbpath = PATH + '/authors.xpn'
db = xapian.Database(dbpath)


async def worker(name, in_q: asyncio.Queue, output: asyncio.Queue):
    print(f'worker {name} started')
    while True:
        paperid, authorids = await in_q.get()
        if paperid is None:
            in_q.task_done()
            break
        authors = dict()
        for aid in authorids:
            for pos in db.postlist(aid):
                doc = db.get_document(pos.docid)
                data: bytes = doc.get_data()
                authors[aid] = data.decode('utf-8')
        result = [authors.get(int(i), 'MISSING_DATA') for i in authorids]
        s = json.dumps({'PaperId': paperid, 'Author': {'set': result}}) + '\n'
        await output.put(s)
        in_q.task_done()
    print(f'worker {name} stopping')


async def feeder(in_q: asyncio.Queue):
    counter = 0
    for pairs in generate_paper_author_affiliations_pg():
        await in_q.put(pairs)
        counter += 1
        if counter == 1000:
            break
    print('feeder finishing')
    for i in range(WORKER_COUNT):
        await in_q.put((None, None))
    print(f'queue size: {in_q.qsize()}')


async def writer(output: asyncio.Queue):
    # with gzip.open(DATA_FOLDER / 'author_updates_pg.jsonl.gz', 'w') as file:
    with gzip.open('/tmp/author_updates_xpn.jsonl.gz', 'w') as file:
        while True:
            content = await output.get()
            if 'STOP' == content:
                output.task_done()
                break
            file.write(content.encode('utf-8'))
            output.task_done()


async def main():
    in_q = asyncio.Queue(10_000)
    output = asyncio.Queue(10_000)
    feed = asyncio.create_task(feeder(in_q))
    workers = []
    print(f'spawning {WORKER_COUNT} workers')
    for i in range(WORKER_COUNT):
        wrk = asyncio.create_task(worker(i, in_q, output))
        workers.append(wrk)
    print('finished spawning :D, creating writer')
    write = asyncio.create_task(writer(output))
    await asyncio.gather(feed, return_exceptions=True)
    print('feeder finished')
    await in_q.join()
    print('input queue finished, awaiting workers')
    await asyncio.gather(*workers, return_exceptions=True)
    print('workers done!')
    await output.join()
    print('output quere finished, should be done soon')
    await output.put('STOP')
    await asyncio.gather(write, return_exceptions=True)
    print('done!')


if __name__ == '__main__':
    start = datetime.now()
    # write_to_gzip()
    asyncio.run(main())
    end = datetime.now()
    # 564606997 lines
    print(f'took {end-start}')

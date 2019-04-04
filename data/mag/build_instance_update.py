from data.mag import generate_json_dict, CONF_INST_FILE, _ENCODING, read_gzip_lines, DATA_FOLDER
from data.mag.headers import ConferenceInstances
from solr.instances import get_async_localhost_session
import gzip
import json
import asyncio
from datetime import datetime

WORKER_COUNT = 80

async def worker(name, in_q: asyncio.Queue, output: asyncio.Queue):
    s = get_async_localhost_session()
    print(f'worker {name} started')
    while True:
        x = await in_q.get()
        if x is None:
            in_q.task_done()
            break
        expr = f'search(mag_papers,q=ConferenceInstanceId:{x["ConferenceInstanceId"]},fl=PaperId, sort="PaperId asc",qt=/export)'
        async with s.collection('mag_papers').stream.expr(expr) as resp:
            response = await resp.json()
            paperids = [doc['PaperId'] for doc in response['result-set']['docs'][:-1]]
            conference_instance_name = x['DisplayName']
            for paper in paperids:
                await output.put(json.dumps({'PaperId': paper, 'ConferenceInstance': {'set': conference_instance_name}}) + '\n')
        in_q.task_done()
    print(f'worker {name} stopping')
    await s.close()


async def feeder(in_q: asyncio.Queue):
    # counter = 0
    for pairs in gen_conf_instance():
        await in_q.put(pairs)
        # counter += 1
        # if counter == 10:
        #     break
    print('feeder finishing')
    for i in range(WORKER_COUNT):
        await in_q.put(None)
    print(f'queue size: {in_q.qsize()}')


async def writer(output: asyncio.Queue):
    # with gzip.open(DATA_FOLDER / 'author_updates_pg.jsonl.gz', 'w') as file:
    with gzip.open(DATA_FOLDER/ 'conference_instance_updates.jsonl.gz', 'w') as file:
        while True:
            content = await output.get()
            if 'STOP' == content:
                output.task_done()
                break
            file.write(content.encode('utf-8'))
            output.task_done()


def gen_conf_instance():
    # counter = 0
    for x in generate_json_dict(ConferenceInstances,read_gzip_lines(CONF_INST_FILE,_ENCODING)):
        # counter +=1
        # if 10 == counter:
        #     break
        yield x

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

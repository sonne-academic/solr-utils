from datetime import datetime
import gzip
from lxml import etree
from data.dblp import DBLP_DATA, file_list
import json
import io
import progress.bar
from progress.bar import Bar


class ProgressStream(io.BufferedReader):
    def __init__(self, raw, size: int, buffer_size=io.DEFAULT_BUFFER_SIZE) -> None:
        super().__init__(raw, buffer_size)
        suffix = '%(percent)d%% %(elapsed_td)s (ETA: %(eta_td)s)'
        self.progress = Bar(max=size, suffix=suffix, hide_cursor=False)

    def read(self, size=-1) -> bytes:
        self.progress.next(size)
        return super().read(size)

    def close(self) -> None:
        super().close()
        self.progress.finish()



note_attribs_map = {
    'type': [
        'source',
        'disstype',
        'affiliation',
        'uname',
        'isnot',
        'award',
        'isbn',
        'doi',
        'reviewid',
        'rating',
    ],
    'label': []
}
known_elements_with_attr = ['note']


def get_evt():
    for file in file_list():
        with gzip.open(file, 'rb') as xf:
            yield from etree.iterparse(xf, ['start', 'end'], load_dtd=True, dtd_validation=True)


def build_fields(it):
    depth = 0
    doprint = False
    for evt, ele in it:
        if 'start' == evt:
            depth += 1
            continue  # 514 secs, without
        elif 'end' == evt:
            depth -= 1
        else:
            raise ValueError('build_fields got an event other than "start" or "end"')

        if -1 == depth:
            # document ends
            break
        if 0 != depth:
            # ignore deeper nested tags
            continue

        if 'title' == ele.tag:
            realtitle = etree.tostring(ele, encoding='unicode').replace('<title>', '').replace('</title>', '').strip()
            if doprint:
                print(depth, ele.tag, realtitle)
            yield 'title', realtitle
            continue
        if 'note' == ele.tag:
            for k, v in ele.attrib.items():
                if k not in note_attribs_map:
                    print(f'new attr: {k}')
                    note_attribs_map[k] = []
                if v not in note_attribs_map[k]:
                    if 'label' != k:
                        print(f'new value for attrib "{k}": {v}')
                        note_attribs_map[k].append(v)
            attrs = ','.join([f'[{k}:{v}]' for k, v in ele.attrib.items()])
            yield ele.tag, f'({attrs}): {ele.text}'
            continue
        elif len(list(ele.attrib.keys())) != 0:
            pass
            # print(f'')

        yield ele.tag, ele.text
        continue


def build_docs(it):
    current_elem = []
    for evt, root in it:
        if 'end' == evt:
            break
        doc = dict()
        for k, v in root.attrib.items():
            if k not in doc:
                doc[k] = v
                continue
            if type(doc[k]) is str:
                prev = doc.pop(k)
                doc[k] = [prev]
            assert type(doc[k]) is list
            doc[k].append(v)

        assert 'pub_type' not in doc
        doc['pub_type'] = root.tag
        for k, v in build_fields(it):
            if v is None:
                print(f'warning: empty value encountered for key {k}')
                continue
            if k not in doc:
                doc[k] = v
                continue
            if type(doc[k]) is str:
                prev = doc.pop(k)
                doc[k] = [prev]

            if type(doc[k]) is not list:
                temp: bytes = etree.tostring(root, encoding='utf-8')
                print(temp.decode('utf-8'))
                # print(f'{k}: {doc[k]} is not list, but {type(doc[k])}')
                raise AssertionError(f'{k}: {doc[k]} is not list, but {type(doc[k])}')
            doc[k].append(v)
        yield doc
        root.clear()


def build_upload_document(it=get_evt()):
    # it = generate_events()
    root_event, root_element = next(it)
    assert root_event == 'start'
    assert root_element.tag == 'dblp'
    yield from build_docs(it)


def write_to_gzip():
    with gzip.open(DBLP_DATA / 'dblp-2019-07-01.jsonl.gz', 'wb') as out_file:
        for content in build_upload_document():
            b = json.dumps(content, ensure_ascii=False).encode('utf-8')
            out_file.write(b + b'\n')


def yield_from_gzip():
    path = DBLP_DATA / 'dblp-2019-07-01.jsonl.gz'
    size = path.stat().st_size
    file = path.open('rb')
    ps=ProgressStream(file, size)
    decoder = gzip.GzipFile(filename=path, fileobj=ps)
    for line in decoder:
        yield line
        # pos = file.tell()
        # if pb.index < pos:
        #     pb.goto(pos)
    # pb.finish()
    # with gzip.open(DBLP_DATA / 'dblp-2019-07-01.jsonl.gz', 'rt', encoding='utf-8') as in_file:
    #     yield from in_file


if __name__ == '__main__':
    start = datetime.now()
    write_to_gzip()
    end = datetime.now()
    print(f'took {end - start}')

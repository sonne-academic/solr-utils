import gzip
import bz2
from lxml import etree as ET
import zstandard as zstd
from data.dblp import DATA_FOLDER, file_list
import json

def get_evt():
    for file in file_list():
        with gzip.open(file, 'rb') as xf:
            yield from ET.iterparse(xf, ['start', 'end'], load_dtd=True)


def build_fields(it):
    depth = 0
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
        if 0 == depth:
            yield ele.tag, ele.text
            continue

        # ignore all deeper nested elements
        assert 0 < depth
        if 1 < depth:
            print(depth, ele.tag, ele.text)


def build_docs(it):
    current_elem = []
    for evt, root in it:
        if 'end' == evt:
            break
        doc = dict()
        for k,v in root.attrib.items():
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
        for k,v in build_fields(it):
            if k not in doc:
                doc[k] = v
                continue
            if type(doc[k]) is str:
                prev = doc.pop(k)
                doc[k] = [prev]
            assert type(doc[k]) is list
            doc[k].append(v)
        yield json.dumps(doc, ensure_ascii=False).encode('utf-8')
        yield b'\n'
        root.clear()


def build_upload_document():
    it = get_evt()
    root_event, root_element = next(it)
    assert root_event == 'start'
    assert root_element.tag == 'dblp'
    yield from build_docs(it)


def write_to_gzip():
    with gzip.open(DATA_FOLDER / 'dblp_docs.jsonl.gz', 'wb') as out_file:
        for content in build_upload_document():
            out_file.write(content)

def yield_from_gzip():
    with gzip.open(DATA_FOLDER / 'dblp_docs.jsonl.gz', 'rt', encoding='utf-8') as in_file:
        yield from in_file

def write_to_bz2():
    with bz2.open(DATA_FOLDER / 'dblp_docs.jsonl.bz2', 'wb') as out_file:
        for content in build_upload_document():
            out_file.write(content)


def write_to_zstd():
    cctx = zstd.ZstdCompressor()
    with open(DATA_FOLDER / 'dblp_docs.jsonl.zst', 'wb') as file:
        with cctx.stream_writer(file) as compressor:
            for content in build_upload_document():
                compressor.write(content)


if __name__ == '__main__':
    write_to_gzip()


import gzip
import bz2
from lxml import etree as ET
import zstandard as zstd
from data.dblp import DATA_FOLDER, file_list


def get_evt():
    for file in file_list():
        with gzip.open(file, 'rb') as xf:
            yield from ET.iterparse(xf, ['start', 'end'], load_dtd=True)


def add_field(doc, name, text):
    ET.SubElement(doc, 'field', attrib={'name': name}).text = text


def build_fields(doc, it):
    depth = 0
    things = []
    for evt, ele in it:
        if 'start' == evt:
            depth += 1
            # continue  # 514 secs, without
        else:
            depth -= 1

        if -1 == depth:
            # document ends
            break
        elif 0 == depth:
            add_field(doc, ele.tag, ele.text)
            things.append(ele.tag)
        else:
            assert 0 < depth
            # ignore all deeper nested elements
            continue


def build_docs(it):
    current_elem = []
    for evt, root in it:
        if 'end' == evt:
            break
        doc = ET.Element('doc')
        for k, v in root.attrib.items():
            add_field(doc, k, v)
        # add_field(doc, 'key', root.attrib['key'])
        add_field(doc, 'pub_type', root.tag)
        build_fields(doc, it)
        yield ET.tostring(doc, encoding='utf-8')
        yield b'\n'


def build_upload_document():
    it = get_evt()
    root_event, root_element = next(it)
    assert root_event == 'start'
    assert root_element.tag == 'dblp'
    yield b'<add>\n'
    yield from build_docs(it)
    yield b'</add>'


def write_to_gzip():
    with gzip.open(DATA_FOLDER / 'dblp_docs.xml.gz', 'w') as out_file:
        for content in build_upload_document():
            out_file.write(content)

def yield_from_gzip():
    with gzip.open(DATA_FOLDER / 'dblp_docs.xml.gz', 'r') as in_file:
        yield from in_file

def write_to_bz2():
    with bz2.open(DATA_FOLDER / 'dblp_docs.xml.bz2', 'wb') as out_file:
        for content in build_upload_document():
            out_file.write(content)


def write_to_zstd():
    cctx = zstd.ZstdCompressor()
    with open(DATA_FOLDER / 'dblp_docs.xml.zst', 'wb') as file:
        with cctx.stream_writer(file) as compressor:
            for content in build_upload_document():
                compressor.write(content)


if __name__ == '__main__':
    write_to_gzip()

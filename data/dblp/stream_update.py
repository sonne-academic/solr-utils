import requests
from lxml import etree
from pathlib import Path
import gzip
from data_config import DBLP_DATA
import zlib
from progress.bar import Bar

__all__ = ['generate_events']

SOURCE_URL = 'https://dblp.org/xml/release/?C=M;O=D;F=0'
BASE_URL = 'https://dblp.org/xml/release/'


def generate_links():
    listing = requests.get(SOURCE_URL).text
    # tree: lxml.html.Element
    tree = etree.fromstring(listing, etree.HTMLParser())
    for a in tree.iterdescendants('a'):
        if 'href' in a.attrib:
            yield a.attrib['href']


def select_most_recent(iterable, ending):
    rev = reversed(sorted(filter(lambda x: x.endswith(ending), iterable)))
    return next(rev)


def decompress_gzip_stream(stream):
    decoder = zlib.decompressobj(wbits=zlib.MAX_WBITS | 16)
    for chunk in stream:
        decoded = decoder.decompress(chunk)
        if decoded:
            yield decoded


def generate_with_progress(response, path: str):
    # dtd is resolved via base_url
    stream = response.raw
    parser = etree.XMLPullParser(
        events=['start', 'end'],
        base_url=path,
        load_dtd=True,
        dtd_validation=True,
    )
    suffix = '%(percent)d%% %(elapsed_td)s (ETA: %(eta_td)s)'
    length = int(response.headers['Content-Length'])
    progress = Bar(suffix=suffix, max=length, hide_cursor=False)
    try:
        for line in decompress_gzip_stream(stream):
            parser.feed(line)
            yield from parser.read_events()
            current_pos = stream.tell()
            if current_pos > progress.index:
                # have to check, otherwise ETA is screwed up
                progress.goto(current_pos)
    except KeyboardInterrupt:
        pass
    finally:
        progress.finish()


def generate_no_progress(response, path: str):
    # dtd is resolved via GzipFile filename
    gz_file = gzip.GzipFile(fileobj=response.raw, filename=path)
    yield from etree.iterparse(
        gz_file,
        events=['start', 'end'],
        load_dtd=True,
        dtd_validation=True,
    )


def generate_events(show_progress=True, keep_dtd=False):
    file_list = list(generate_links())
    dtd = select_most_recent(file_list, 'dtd')
    gz = select_most_recent(file_list, 'gz')
    md5 = select_most_recent(file_list, 'md5')
    dtd_path = DBLP_DATA / Path(dtd)
    gz_path = DBLP_DATA / Path(gz)

    print(f'log generating from {gz} with {dtd}')
    dtd_path.write_text(requests.get(BASE_URL+dtd).text)

    response = requests.get(BASE_URL + gz, stream=True)
    if not response.ok:
        raise ValueError(f'could not grab .gz, server responded with {response.status_code}.')

    if not show_progress:
        yield from generate_no_progress(response, str(gz_path))
    else:
        yield from generate_with_progress(response, str(gz_path))

    if not keep_dtd:
        dtd_path.unlink()


def main():
    for count, event in enumerate(generate_events(keep_dtd=True)):
        evt, ele = event
        if 'end' == evt:
            ele.clear()
        # print(event)
        # if count == 10:
        #     break
        pass


if __name__ == '__main__':
    main()

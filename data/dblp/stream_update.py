import requests
from lxml.html import parse
from lxml import etree
import lxml
from pathlib import Path
import gzip

SOURCE_URL = 'https://dblp.org/xml/release/?C=M;O=D;F=0'
BASE_URL = 'https://dblp.org/xml/release/'


def generate_file_list():
    listing = requests.get(SOURCE_URL).text
    tree: lxml.html.Element = etree.fromstring(listing, etree.HTMLParser())
    for a in tree.iterdescendants('a'):
        if 'href' in a.attrib:
            yield a.attrib['href']


def get_most_recent(iterable, ending):
    rev = reversed(sorted(filter(lambda x: x.endswith(ending), iterable)))
    return next(rev)


def generate_events():
    file_list = list(generate_file_list())
    dtd = get_most_recent(file_list, 'dtd')
    gz = get_most_recent(file_list, 'gz')
    md5 = get_most_recent(file_list, 'md5')
    dtd_path = Path(dtd)
    gz_path = Path(gz)

    print(f'log generating from {gz} with {dtd}')
    dtd_path.write_text(requests.get(BASE_URL+dtd).text)

    stream = requests.get(BASE_URL + gz, stream=True)
    gz_file = gzip.GzipFile(fileobj=stream.raw, filename=str(gz_path))

    yield from etree.iterparse(gz_file, ['start', 'end'], load_dtd=True, dtd_validation=True)

    dtd_path.unlink()


def main():
    for count, event in enumerate(generate_events()):
        print(event)
        if count == 10:
            break


if __name__ == '__main__':
    main()

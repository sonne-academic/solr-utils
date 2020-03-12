from pathlib import Path
import logging
import requests
from lxml import etree
import gzip
import shutil

__all__ = ['LocalSource', 'RemoteSource']
log = logging.getLogger()


def get_most_recent(iterable, ending):
    rev = reversed(sorted(filter(lambda x: x.endswith(ending), iterable)))
    return next(rev)


class LocalSource:
    def __init__(self, basepath: Path):
        self.path = basepath / 'dblp'
        if not self.path.is_dir():
            self.path.mkdir(parents=True, exist_ok=True)

    @property
    def files(self):
        path = self.path
        for entry in path.iterdir():
            if not entry.is_file():
                continue
            if '.gz' == entry.suffix:
                yield entry.name

    @property
    def latest(self):
        return get_most_recent(self.files, 'gz')

    def make_stream(self, name: str = None):
        if None is name:
            name = self.latest
        return gzip.open(self.path / name, 'rb')


class RemoteSource:
    SOURCE_URL = 'https://dblp.org/xml/release/?C=M;O=D;F=0'
    BASE_URL = 'https://dblp.org/xml/release/'

    def __init__(self, basepath: Path):
        self._files = []
        self.path = basepath / 'dblp'
        if not self.path.is_dir():
            self.path.mkdir(parents=True, exist_ok=True)

    @property
    def files(self):
        if len(self._files):
            for h in self._files:
                if h.endswith('.gz'):
                    yield h
            return
        listing = requests.get(self.BASE_URL).text
        tree = etree.fromstring(listing, etree.HTMLParser())
        for a in tree.iterdescendants('a'):
            if 'href' in a.attrib:
                h = a.attrib['href']
                if h.endswith('.gz'):
                    yield h
                self._files.append(h)

    @property
    def latest(self):
        return get_most_recent(self.files, 'gz')

    def make_stream(self, name: str = None):
        self.download_dtd()
        if None is name:
            name = self.latest
        gz_path = self.path / name
        stream = self.make_gz_stream(name)
        return gzip.GzipFile(fileobj=stream.raw, filename=str(gz_path))

    def make_gz_stream(self, name: str = None):
        if None is name:
            name = self.latest
        response = requests.get(self.BASE_URL + name, stream=True)
        return response.raw

    def download_dtd(self):
        for dtd in filter(lambda x: x.endswith('dtd'), self._files):
            dtd_path = self.path / dtd
            if dtd_path.is_file():
                print(f'skipped existing {dtd_path}')
                continue
            dtd_path.write_text(requests.get(self.BASE_URL + dtd).text)
            print(f'wrote {dtd_path}')

    def download(self, name: str):
        out_file_path = self.path / name
        if out_file_path.is_file():
            log.warning(f'{out_file_path} exists, will not overwrite')
            return
        log.info(f'grabbing {name}')
        stream = self.make_gz_stream()
        with open(str(out_file_path), 'wb') as out_file:
            shutil.copyfileobj(stream, out_file)


# md5 = get_most_recent(file_list, 'md5')
# print(f'log generating from {gz} with {dtd}')
# yield from etree.iterparse(gz_file, ['start', 'end'], load_dtd=True, dtd_validation=True)
# dtd_path.unlink()

from cli.cmdparser import ParserManager, Argument
from pathlib import Path
import logging
PM = ParserManager('data', 'command help')
log = logging.getLogger()


def argument_parser():
    return PM.parser


@PM.command(
    'download files from an open data source',
    Argument('source', help='what data do you want to download'),
    Argument('output_folder', help='the directory for the output', default=Path.cwd(), nargs='?'),
)
def download(source, output_folder):
    if isinstance(output_folder, str):
        output_folder = Path(output_folder)
    if 'dblp' == source:
        from data.dblp import sources
        src = sources.RemoteSource(output_folder)
        src.download(src.latest)
    else:
        log.error(f'not implemented for {source}')


@PM.command(
    'upload from an open data source to solr',
    Argument('source', help='what data do you want to upload'),
    Argument('host', help='host to upload to', default='localhost:8983'),
    Argument('--stream', help='stream the files directly from the source', action='store_true')
)
def upload(source, host, stream):
    pass
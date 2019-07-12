from data.mag.build_docs_from_sqlite import generate_papers, count_papers, strip_and_dump_from_gen
from solr.instances import get_session
from data import upload_batches_unparsed
from solr.session import SolrSession
from solr.configsets import get_config


def reset_collection(s: SolrSession):
    print('deleting collection')
    print(s.admin.collections.delete('mag').json())

    print('deleting config')
    print(s.admin.configs.delete('mag').json())

    print('sending latest config')
    print(s.admin.configs.upload('mag', get_config('mag')).json())

    print('creating collection')
    print(s.admin.collections.create('mag', 4, 1, 1, 'mag').json())


if __name__ == '__main__':
    s = get_session('localhost', 8984)
    rows = count_papers()
    reset = False
    if reset is True:
        reset_collection(s)
    generator = strip_and_dump_from_gen(generate_papers(max_num=rows))
    upload_batches_unparsed(s, 'mag', generator)

from typing import List

from solr.api import SolrPathApi
from solr.api.collection.config import SolrCollectionConfig
from solr.api.collection.schema import SolrCollectionSchema
from solr.api.collection.update import SolrCollectionUpdate

__all__ = ['SolrCollection']


class SolrCollection:
    def __init__(self, session, collection_name):
        self.session = session
        self.collection = collection_name
        self._update = SolrCollectionUpdate(session, collection_name)
        self._schema = SolrCollectionSchema(session, collection_name)
        self._config = SolrCollectionConfig(session, collection_name)
        self._stream = SolrStream(session, collection_name)
        self._graph = SolrGraph(session, collection_name)
        self._get = SolrGet(session, collection_name)
        self._tag = SolrTag(session, collection_name)

    @property
    def schema(self):
        return self._schema

    @property
    def config(self):
        return self._config

    @property
    def update(self):
        return self._update

    @property
    def stream(self):
        return self._stream

    @property
    def graph(self):
        return self._graph

    @property
    def get(self):
        return self._get

    @property
    def tag(self):
        return self._tag


    def search(self, query, requestHandler='/select', **kwargs):
        if query != '':
            kwargs['q'] = query
        return self.session._get_path(self.collection + requestHandler, params=kwargs)

class SolrStream(SolrPathApi):
    def __init__(self, session, collection_name):
        super().__init__(session, collection_name + '/stream')

    def expr(self, expression):
        params = {
            'expr': str(expression)
        }
        return self._get(params=params)


class SolrGet(SolrPathApi):
    def __init__(self, session, collection_name):
        super().__init__(session, collection_name + '/get')

    def id(self, _id):
        params = {
            'id': _id
        }
        return self._get(params=params)

    def ids(self, _ids):
        params = {
            'ids': _ids
        }
        return self._post(json={'params':params})


class SolrTag(SolrPathApi):
    def __init__(self, session, collection_name):
        super().__init__(session, collection_name + '/tag')

    def tag(self, payload: str, overlap_strategy: str, fields: List[str]):
        headers={'Content-Type': 'text/plain'}
        params = {
            'fl': ','.join(fields),
            'overlaps': overlap_strategy   # ALL, NO_SUB, LONGEST_DOMINANT_RIGHT
        }
        return self._post(params=params, headers=headers, data=payload)


class SolrGraph(SolrPathApi):
    def __init__(self, session, collection_name):
        super().__init__(session, collection_name + '/graph')

    def expr(self, expression):
        params = {
            'expr': str(expression)
        }
        return self._get(params=params)


class SolrQuery(SolrPathApi):

    def __init__(self, session, collection_name):
        super().__init__(session, '/query')
        self.collection = collection_name




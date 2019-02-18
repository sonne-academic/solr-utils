import asyncio

import requests
import aiohttp
from solr.api.admin import SolrAdmin
from solr.api.collection import SolrCollection

class SolrConnector:
    def connect(self) -> str:
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class SolrSession:
    def __init__(self, connector: SolrConnector):
        super().__init__()
        self.connector = connector
        self.host = self.connector.connect()
        self._session = requests.Session()
        self._admin = SolrAdmin(self)
        self._collections = {}

    def _post_path(self, path, **kwargs):
        return self._session.post(self.host + path, **kwargs)

    def _get_path(self, path, **kwargs):
        return self._session.get(self.host + path, **kwargs)

    def close(self):
        self._session.close()
        self.connector.close()

    @property
    def admin(self):
        return self._admin

    def collection(self, name) -> SolrCollection:
        try:
            return self._collections[name]
        except KeyError:
            self._collections[name] = SolrCollection(self, name)
            return self._collections[name]


class SolrAsyncSession:
    def __init__(self, connector: SolrConnector):
        super().__init__()
        self.connector = connector
        self.host = self.connector.connect()
        self._loop = asyncio.get_event_loop()
        self._session = aiohttp.ClientSession(loop=self._loop)
        self._admin = SolrAdmin(self)
        self._collections = {}

    def _post_path(self, path, **kwargs):
        return self._session.post(self.host + path, **kwargs)

    def _get_path(self, path, **kwargs):
        return self._session.get(self.host + path, **kwargs)

    async def close(self):
        await self._session.close()
        self.connector.close()

    @property
    def admin(self):
        return self._admin

    def collection(self, name) -> SolrCollection:
        try:
            return self._collections[name]
        except KeyError:
            self._collections[name] = SolrCollection(self, name)
            return self._collections[name]
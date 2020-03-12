from solr.api import SolrPathApi


class SolrCollectionConfig(SolrPathApi):
    """
    https://lucene.apache.org/solr/guide/8_3/config-api.html
    """
    def __init__(self, session, collection_name: str):
        super().__init__(session, collection_name + '/config')
        self._overlay = config_overlay(session, collection_name)
        self._query = config_query(session, collection_name)
        self._requestHandler = config_requestHandler(session, collection_name)
        self._searchComponent = config_searchComponent(session, collection_name)
        self._updateHandler = config_updateHandler(session, collection_name)
        self._queryResponseWriter = config_queryResponseWriter(session, collection_name)
        self._initParams = config_initParams(session, collection_name)
        self._znodeVersion = config_znodeVersion(session, collection_name)
        self._listener = config_listener(session, collection_name)
        self._directoryFactory = config_directoryFactory(session, collection_name)
        self._indexConfig = config_indexConfig(session, collection_name)
        self._codecFactory = config_codecFactory(session, collection_name)

    @property
    def overlay(self):
        return self._overlay

    @property
    def query(self):
        return self._query

    @property
    def requestHandler(self):
        return self._requestHandler

    @property
    def searchComponent(self):
        return self._searchComponent

    @property
    def updateHandler(self):
        return self._updateHandler

    @property
    def queryResponseWriter(self):
        return self._queryResponseWriter

    @property
    def initParams(self):
        return self._initParams

    @property
    def znodeVersion(self):
        return self._znodeVersion

    @property
    def listener(self):
        return self._listener

    @property
    def directoryFactory(self):
        return self._directoryFactory

    @property
    def indexConfig(self):
        return self._indexConfig

    @property
    def codecFactory(self):
        return self._codecFactory


class config_overlay(SolrPathApi):
    def __init__(self, session, collection_name):
        super().__init__(session, collection_name + '/config/overlay')

    def get_all(self):
        return self._get()

class config_query(SolrPathApi):
    def __init__(self, session, collection_name):
        super().__init__(session, collection_name + '/config/query')

    def get_all(self):
        return self._get()

class config_requestHandler(SolrPathApi):
    def __init__(self, session, collection_name):
        super().__init__(session, collection_name + '/config/requestHandler')

    def get(self, componentName):
        return self._get(params={'componentName': componentName})

    def get_all(self):
        return self._get()

class config_searchComponent(SolrPathApi):
    def __init__(self, session, collection_name):
        super().__init__(session, collection_name + '/config/searchComponent')

    def get(self, componentName):
        return self._get(params={'componentName': componentName})

    def get_all(self):
        return self._get()

class config_updateHandler(SolrPathApi):
    def __init__(self, session, collection_name):
        super().__init__(session, collection_name + '/config/updateHandler')

    def get_all(self):
        return self._get()

class UpdateHandlerProperties:
    def __init__(self, handler: config_updateHandler):
        self._handler = handler

    @property
    def autoCommit(self):
        pass

    @property
    def autoSoftCommit(self):
        pass

    @property
    def commitWithin(self):
        pass

    @property
    def indexWriter(self):
        pass

class UpdateHandlerAutoCommit:
    @property
    def maxDocs(self):
        pass

    @property
    def maxTime(self):
        pass

    @property
    def openSearcher(self):
        pass

class config_queryResponseWriter(SolrPathApi):
    def __init__(self, session, collection_name):
        super().__init__(session, collection_name + '/config/queryResponseWriter')

    def get(self, componentName):
        return self._get(params={'componentName': componentName})

    def get_all(self):
        return self._get()

class config_initParams(SolrPathApi):
    def __init__(self, session, collection_name):
        super().__init__(session, collection_name + '/config/initParams')

    def get_all(self):
        return self._get()

class config_znodeVersion(SolrPathApi):
    def __init__(self, session, collection_name):
        super().__init__(session, collection_name + '/config/znodeVersion')

    def get_all(self):
        return self._get()

class config_listener(SolrPathApi):
    def __init__(self, session, collection_name):
        super().__init__(session, collection_name + '/config/listener')

    def get_all(self):
        return self._get()

class config_directoryFactory(SolrPathApi):
    def __init__(self, session, collection_name):
        super().__init__(session, collection_name + '/config/directoryFactory')

    def get_all(self):
        return self._get()

class config_indexConfig(SolrPathApi):
    def __init__(self, session, collection_name):
        super().__init__(session, collection_name + '/config/indexConfig')

    def get_all(self):
        return self._get()

class config_codecFactory(SolrPathApi):
    def __init__(self, session, collection_name):
        super().__init__(session, collection_name + '/config/codecFactory')

    def get_all(self):
        return self._get()



common_properties = [
    'updateHandler.autoCommit.maxDocs',
    'updateHandler.autoCommit.maxTime',
    'updateHandler.autoCommit.openSearcher',
    'updateHandler.autoSoftCommit.maxDocs',
    'updateHandler.autoSoftCommit.maxTime',
    'updateHandler.commitWithin.softCommit',
    'updateHandler.indexWriter.closeWaitsForMerges',
    'query.filterCache.class',
    'query.filterCache.size',
    'query.filterCache.initialSize',
    'query.filterCache.autowarmCount',
    'query.filterCache.maxRamMB',
    'query.filterCache.regenerator',
    'query.queryResultCache.class',
    'query.queryResultCache.size',
    'query.queryResultCache.initialSize',
    'query.queryResultCache.autowarmCount',
    'query.queryResultCache.maxRamMB',
    'query.queryResultCache.regenerator',
    'query.documentCache.class',
    'query.documentCache.size',
    'query.documentCache.initialSize',
    'query.documentCache.autowarmCount',
    'query.documentCache.regenerator',
    'query.fieldValueCache.class',
    'query.fieldValueCache.size',
    'query.fieldValueCache.initialSize',
    'query.fieldValueCache.autowarmCount',
    'query.fieldValueCache.regenerator',
    'query.maxBooleanClauses',
    'query.enableLazyFieldLoading',
    'query.useFilterForSortedQuery',
    'query.queryResultWindowSize',
    'query.queryResultMaxDocCached',
    'requestDispatcher.handleSelect',
    'requestDispatcher.requestParsers.enableRemoteStreaming',
    'requestDispatcher.requestParsers.enableStreamBody',
    'requestDispatcher.requestParsers.multipartUploadLimitInKB',
    'requestDispatcher.requestParsers.formdataUploadLimitInKB',
    'requestDispatcher.requestParsers.addHttpRequestToContext',
]

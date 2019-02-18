class StreamSource:
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.extra_args=None
        self.extra_kwargs=None

    def __str__(self) -> str:
        return f'{self.name}({self.join()})'

    def add_extra_args(self):
        pass

    def join_args(self, *args):
        return ', '.join([str(arg) for arg in args])

    def join_kwargs(self, **kwargs):
        return self.join_args(*['='.join([k, f'"{v}"']) for k, v in kwargs.items()])

    def join(self):
        joined = []
        if self.args:
            joined.append(self.join_args(*self.args))
        if self.kwargs:
            joined.append(self.join_kwargs(**self.kwargs))
        if self.extra_args:
            joined.append(self.join_args(*self.extra_args))
        if self.extra_kwargs:
            joined.append(self.join_kwargs(**self.extra_kwargs))
        return self.join_args(*joined)


class Search(StreamSource):
    # http://lucene.apache.org/solr/guide/7_4/stream-source-reference.html#search-parameters
    def __init__(self, collection, q, fl, sort, zkHost=None, qt='/select', rows=10, partitionKeys=None):
        """
        The search function searches a SolrCloud collection and emits a stream of tuples that match the query. This is very similar to a standard Solr query, and uses many of the same parameters.
        This expression allows you to specify a request hander using the qt parameter. By default, the /select handler is used. The /select handler can be used for simple rapid prototyping of expressions. For production, however, you will most likely want to use the /export handler which is designed to sort and export entire result sets. The /export handler is not used by default because it has stricter requirements then the /select handler so it’s not as easy to get started working with. To read more about the /export handler requirements review the section Exporting Result Sets.

        :param collection: (Mandatory) the collection being searched.
        :param q: (Mandatory) The query to perform on the Solr index.
        :param fl: (Mandatory) The list of fields to return.
        :param sort: (Mandatory) The sort criteria.
        :param zkHost: Only needs to be defined if the collection being searched is found in a different zkHost than the local stream handler.
        :param qt: Specifies the query type, or request handler, to use. Set this to /export to work with large result sets. The default is /select.
        :param rows: (Mandatory with the /select handler) The rows parameter specifies how many rows to return. This parameter is only needed with the /select handler (which is the default) since the /export handler always returns all rows.
        :param partitionKeys: Comma delimited list of keys to partition the search results by. To be used with the parallel function for parallelizing operations across worker nodes. See the parallel function for details.
        """
        args = [collection]
        kwargs = {
            'q': q,
            'fl': fl,
            'sort': sort,
            'qt': qt
        }
        if '/select' == qt:
            kwargs['rows'] = rows

        if partitionKeys:
            kwargs['partitionKeys'] = partitionKeys

        if zkHost:
            kwargs['zkHost'] = zkHost

        super().__init__('search', *args, **kwargs)


class Echo(StreamSource):
    def __init__(self, string: str):
        """
        The echo function returns a single Tuple echoing its text parameter. Echo is the simplest stream source designed to provide text to a text analyzing stream decorator.

        :param string:
        """
        super().__init__('echo', string)


class Facet(StreamSource):
    # http://lucene.apache.org/solr/guide/7_4/stream-source-reference.html#facet
    def __init__(self, collection, q, buckets, bucketSorts=None, bucketSizeLimit=None, metrics=None):
        """
        The facet function provides aggregations that are rolled up over buckets. Under the covers the facet function pushes down the aggregation into the search engine using Solr’s JSON Facet API. This provides sub-second performance for many use cases. The facet function is appropriate for use with a low to moderate number of distinct values in the bucket fields. To support high cardinality aggregations see the rollup function.

        :param collection: (Mandatory) Collection the facets will be aggregated from.
        :param q: (Mandatory) The query to build the aggregations from.
        :param buckets: (Mandatory) Comma separated list of fields to rollup over. The comma separated list represents the dimensions in a multi-dimensional rollup.
        :param bucketSorts: Comma separated list of sorts to apply to each dimension in the buckets parameters. Sorts can be on the computed metrics or on the bucket values.
        :param bucketSizeLimit:The number of buckets to include. This value is applied to each dimension.
        :param metrics: List of metrics to compute for the buckets. Currently supported metrics are sum(col), avg(col), min(col), max(col), count(*).
        """
        kwargs = {
            'q': q,
            'buckets': buckets
        }
        args = [collection]
        metrics = metrics
        if bucketSorts:
            kwargs['bucketSorts'] = bucketSorts
        if bucketSizeLimit:
            kwargs['bucketSizeLimit'] = bucketSizeLimit
        super().__init__('facet', *args, **kwargs)
        self.metrics = metrics

    def __str__(self) -> str:
        if self.metrics:
            return f'{self.name}({self.join()}, {self.metrics})'
        return super().__str__()


class Features(StreamSource):
    # http://lucene.apache.org/solr/guide/7_4/stream-source-reference.html#features
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        raise NotImplementedError


class Nodes(StreamSource):
    def __init__(self, collection, walk, gather, in_stream=None, scatter=None, metrics=None, fq=None, maxDocFreq=None, trackTraversal=False):
        args = [collection]
        if in_stream:
            args.append(in_stream)
        kwargs= {
            'walk': walk,
            'gather': gather,
        }
        if scatter:
            kwargs['scatter'] = scatter
        if fq:
            kwargs['fq'] = fq
        if maxDocFreq:
            kwargs['maxDocFreq'] = maxDocFreq
        if trackTraversal:
            kwargs['trackTraversal'] = trackTraversal
        self.extra_args = []
        if metrics:
            self.extra_args.append(metrics)
        super().__init__('nodes', *args, **kwargs)


class Knn(StreamSource):
    # http://lucene.apache.org/solr/guide/7_4/stream-source-reference.html#knn
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        raise NotImplementedError

class Model(StreamSource):
    # http://lucene.apache.org/solr/guide/7_4/stream-source-reference.html#knn
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        raise NotImplementedError

class Random(StreamSource):
    # http://lucene.apache.org/solr/guide/7_4/stream-source-reference.html#knn
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        raise NotImplementedError

class SignificantTerms(StreamSource):
    # http://lucene.apache.org/solr/guide/7_4/stream-source-reference.html#knn
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        raise NotImplementedError

class ShortestPath(StreamSource):
    # http://lucene.apache.org/solr/guide/7_4/stream-source-reference.html#knn
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        raise NotImplementedError

class Shuffle(StreamSource):
    # http://lucene.apache.org/solr/guide/7_4/stream-source-reference.html#knn
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        raise NotImplementedError

class Stats(StreamSource):
    # http://lucene.apache.org/solr/guide/7_4/stream-source-reference.html#knn
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        raise NotImplementedError

class TimeSeries(StreamSource):
    # http://lucene.apache.org/solr/guide/7_4/stream-source-reference.html#knn
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        raise NotImplementedError

class Train(StreamSource):
    # http://lucene.apache.org/solr/guide/7_4/stream-source-reference.html#knn
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        raise NotImplementedError

class Topic(StreamSource):
    # http://lucene.apache.org/solr/guide/7_4/stream-source-reference.html#knn
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        raise NotImplementedError

class Tuple(StreamSource):
    # http://lucene.apache.org/solr/guide/7_4/stream-source-reference.html#knn
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        raise NotImplementedError




if __name__ == '__main__':
    print(Echo("stringasdasdasd"))
    print(Search('dblp', q='author:Timo\ Ropinski', fl='author, key', sort='key asc'))

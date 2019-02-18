from solr.api.stream.sources import StreamSource, Model, Topic, Search
class StreamDecorator(StreamSource):
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

class CartesianProduct(StreamDecorator):
    def __init__(self, in_stream: StreamSource, fieldNameOrEvaluator, productSort=None):
        if productSort:
            super().__init__('cartesianProduct', in_stream, fieldNameOrEvaluator, productSort=productSort)
        else:
            super().__init__('cartesianProduct', in_stream, fieldNameOrEvaluator)


class Classify(StreamDecorator):
    # docs are borked: http://lucene.apache.org/solr/guide/7_4/stream-decorator-reference.html#classify
    def __init__(self, model_expr: Model, field, in_stream, *args, **kwargs):
        super().__init__('classify', in_stream, *args, **kwargs)
        raise NotImplementedError


class Commit(StreamDecorator):
    def __init__(self, dest_collection, in_stream, batchSize=0, waitFlush=False, waitSearcher=False, softCommit=False):
        kwargs = {'batchSize': batchSize}
        if waitFlush:
            kwargs['waitFlush'] = 'true'
        else:
            kwargs['waitFlush'] = 'false'
        if waitSearcher:
            kwargs['waitSearcher'] = 'true'
        else:
            kwargs['waitSearcher'] = 'false'
        if softCommit:
            kwargs['softCommit'] = 'true'
        else:
            kwargs['softCommit'] = 'false'

        super().__init__('commit', dest_collection, **kwargs)
        self.extra_args = [in_stream]


class Complement(StreamDecorator):
    def __init__(self, in_stream1: StreamSource, in_stream2: StreamSource, on):
        super().__init__('complement', in_stream1, in_stream2, on=on)


class Daemon(StreamDecorator):
    def __init__(self, name, in_stream, *args, **kwargs):
        super().__init__('daemon', in_stream, *args, **kwargs)
        raise NotImplementedError


class Eval(StreamDecorator):
    def __init__(self, stream_expression: StreamSource):
        super().__init__('eval', stream_expression)


class Executor(StreamDecorator):
    def __init__(self, in_stream: StreamSource, threads=None):
        super().__init__('executor', threads=threads)
        self.extra_args = [in_stream]


class Fetch(StreamDecorator):
    def __init__(self, collection, in_stream, fl, on=None, batchSize=None):
        super().__init__('fetch', collection, in_stream, fl=fl, on=on, batchSize=batchSize)


class Having(StreamDecorator):
    def __init__(self, in_stream: StreamSource, booleanEvaluator):
        super().__init__('having', in_stream, booleanEvaluator)


class LeftOuterJoin(StreamDecorator):
    def __init__(self, stream_left: StreamSource, stream_right: StreamSource, on):
        super().__init__('leftOuterJoin', stream_left, stream_right, on=on)


class HashJoin(StreamDecorator):
    def __init__(self, stream_left: StreamSource, stream_right: StreamSource, on):
        super().__init__('hashJoin', stream_left, hashed=stream_right, on=on)


class InnerJoin(StreamDecorator):
    def __init__(self, stream_left: StreamSource, stream_right: StreamSource, on):
        super().__init__('innerJoin', stream_left, stream_right, on=on)


class Intersect(StreamDecorator):
    def __init__(self, stream_left: StreamSource, stream_right: StreamSource, on):
        super().__init__('intersect', stream_left, stream_right, on=on)


class Merge(StreamDecorator):
    def __init__(self, on, *args):
        if len(args) < 2:
            raise ValueError('must at least provide 2 stream sources via args')
        super().__init__('merge', *args, on=on)


class Null(StreamDecorator):
    def __init__(self, in_stream):
        super().__init__('null', in_stream)


class OuterHashJoin(StreamDecorator):
    def __init__(self, stream_left: StreamSource, stream_right: StreamSource, on):
        super().__init__('outerHashJoin', stream_left, hashed=stream_right, on=on)


class Parallel(StreamDecorator):
    def __init__(self, collection, in_stream, workers, sort, zkHost=None):
        if zkHost:
            super().__init__('parallel', collection, in_stream, workers=workers, zkHost=zkHost, sort=sort)
        else:
            super().__init__('parallel', collection, in_stream, workers=workers, sort=sort)


class Proirity(StreamDecorator):
    def __init__(self, topic1: Topic, topic2: Topic):
        super().__init__('priority', topic1, topic2)


class Reduce(StreamDecorator):
    def __init__(self, in_stream, by, reduce_operation):
        super().__init__('reduce', in_stream, by=by)
        self.extra_args = [reduce_operation]


class Rollup(StreamDecorator):
    def __init__(self, in_stream: StreamSource, over, metrics):
        super().__init__('rollup', in_stream, over=over)
        self.extra_args = [metrics]


class ScoreNodes(StreamDecorator):
    # graph traversal
    def __init__(self, name, in_stream, *args, **kwargs):
        super().__init__(name, in_stream, *args, **kwargs)
        raise NotImplementedError


class Select(StreamDecorator):
    def __init__(self, in_stream: StreamSource, *args):
        super().__init__('select', in_stream, *args)

class Sort(StreamDecorator):
    def __init__(self, in_stream, by):
        super().__init__('sort', in_stream, by=by)


class Top(StreamDecorator):
    def __init__(self, count, in_stream, sort):
        super().__init__('top', n=count)
        self.extra_args = [in_stream]
        self.extra_kwargs = {'sort': sort}


class Unique(StreamDecorator):
    def __init__(self, in_stream, over):
        super().__init__('unique', in_stream, over=over)


class Update(StreamDecorator):
    def __init__(self, dest_collection, in_stream, batchSize):
        super().__init__('update', dest_collection, batchSize=batchSize)
        self.extra_args = [in_stream]



if __name__ == '__main__':
    print(Top(3, Search('collection1','*:*','id,a_s,a_i',"a_f desc, a_i desc"),"a_f asc"))
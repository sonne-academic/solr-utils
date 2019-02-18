import requests
import queue
import threading
from data.dblp.convert import build_upload_document


class WriteableQueue(queue.Queue):
    def write(self, data):
        # An empty string would be interpreted as EOF by the receiving server
        if data:
            self.put(data)

    def __iter__(self):
        return iter(self.get, None)

    def close(self):
        self.put(None)


def post_request(iterable):
    headers = {'Content-Type': 'text/xml'}
    r = requests.post('http://localhost:8983/solr/dblp/update', data=iterable, headers=headers)
    print(r.text)


if __name__ == '__main__':
    # q = WriteableQueue(1024)
    # threading.Thread(target=post_request, args=(q,)).start()
    post_request(build_upload_document())
    # for content in build_document():
    #     q.write(content)
    #
    # # closing ends the request
    # q.close()



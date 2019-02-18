from solr.post import UpdateSender
from data.unpaywall import read_all


if __name__ == '__main__':
    us = UpdateSender('http://localhost:8983/solr/')
    us.send_jsonl('sless', read_all())
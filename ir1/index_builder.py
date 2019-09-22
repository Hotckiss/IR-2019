import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk
import os
from tqdm import tqdm
import time


def create_es_action(index, doc_id, document):
    return {
        '_index': index,
        '_id': doc_id,
        '_source': document
    }


def pretty_print_result(search_result, fields=None):
    if fields is None:
        fields = []
    res = search_result['hits']
    print(f'Total documents: {res["total"]["value"]}')
    for hit in res['hits']:
        print(f'Doc {hit["_id"]}, score is {hit["_score"]}')
        for field in fields:
            print(f'{field}: {hit["_source"][field]}')


class Index:
    def __init__(self, index, settings):
        self.index_name = index
        self.settings = settings
        self.es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'timeout': 360}])
        if not self.es.indices.exists(index=index):
            self.es.indices.create(index=index, body=settings)

    def es_actions_generator(self):
        for doc_name in tqdm(os.listdir("res/json")):
            with open(f"res/json/{doc_name}", "r") as inf:
                doc_id = int(''.join(list(filter(str.isdigit, doc_name))))
                doc = json.load(inf)
            yield create_es_action(self.index_name, doc_id, doc)

    def add_documents(self):
        for ok, result in parallel_bulk(self.es, self.es_actions_generator(), queue_size=4, thread_count=4, chunk_size=1000):
            if not ok:
                print(result)

    def get_doc_by_id(self, doc_id):
        return self.es.get(index=self.index_name, id=doc_id)['_source']

    def search(self, query, *args):
        pretty_print_result(self.es.search(index=self.index_name, body=query, size=1000), args)
        # note that size set to 20 just because default value is 10 and we know that we have 12 docs and 10 < 12 < 20


settings_1 = {
    'mappings': {
        'properties': {
            'text': {
                'type': 'text'
            }
        }
    }
}


if __name__ == '__main__':
    index = Index("docs", settings_1)
    query = {
        'query': {
            'match_all': {}
        }
    }
    start = time.time()
    index.add_documents()
    print(time.time() - start)
    index.search(query)

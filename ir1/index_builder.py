import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk
import os
from tqdm import tqdm
import time
from lxml import etree
from sklearn.metrics import r2_score


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


def get_score(search_result):
    res = {}
    for hit in search_result['hits']['hits']:
        res[hit["_id"]] = hit["_score"]
    return res


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
        for ok, result in parallel_bulk(self.es, self.es_actions_generator(), queue_size=4, thread_count=4,
                                        chunk_size=1000):
            if not ok:
                print(result)

    def get_doc_by_id(self, doc_id):
        return self.es.get(index=self.index_name, id=doc_id)['_source']

    def search(self, query, *args):
        get_score(self.es.search(index=self.index_name, body=query, size=1000))
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


class Query:
    def __init__(self, task_id, query, relevance):
        self.task_id = task_id
        self.query = query
        self.relevance = relevance

    def json_query(self):
        return {
            'query': {
                'bool': {
                    'should': [
                        {
                            'match': {
                                'text': self.query
                            }
                        }
                    ]
                }
            }
        }


class SearchQualityChecker:
    def __init__(self, queries, index):
        self.queries = queries
        self.index = index
        self.results = {}

    def search(self):
        self.results = {}
        for query in self.queries:
            actual = self.index.search(query.json_query())
            self.results[query.task_id] = [(actual[k], query.relevance[k]) for k in query.relevance]

    def r2(self):
        for query in self.queries:
            r2 = r2_score(self.results[query.task_id][1], self.results[query.task_id][0])
            print(f"Task {query.task_id}, r2={r2}")


def get_relevance():
    res = {}
    xml_tree = etree.parse("data/or_relevant-minus_table.xml")
    root = xml_tree.getroot()
    for task in root.getchildren():
        relevance = {}
        for document in task.getchildren():
            relevance[document.get("id")] = document.get("relevance")
        res[task.get("id")] = relevance
    print(len(res))
    return res


def generate_queries_plain_texts():
    relevances = get_relevance()
    xml_tree = etree.parse("data/web2008_adhoc.xml")
    root = xml_tree.getroot()
    res = []
    for task in root.getchildren():
        if task.get("id") is not None:
            for query_text in task.getchildren():
                try:
                    res.append(Query(task.get("id"), query_text.text, relevances[task.get("id")]))
                except:
                    pass
    print(len(res))
    return res


if __name__ == '__main__':
    index = Index("docs", settings_1)
    # start = time.time()
    # index.add_documents()
    # print(time.time() - start)

    queries = generate_queries_plain_texts()
    sqc = SearchQualityChecker(queries, index)
    sqc.search()
    sqc.r2()
    '''for query_text in generate_queries_texts():
        if query_text is None or query_text == "":
            continue
        query = {
            'query': {
                'bool': {
                    'should': [
                        {
                            'match': {
                                'text': query_text
                            }
                        }
                    ]
                }
            }
        }
        index.search(query)
        break'''

import json
import base64
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
from pymystem3 import Mystem

def get_features_str():
    res = {}
    max_ul = 0
    max_dl = 0
    max_pr = 0
    for filename in tqdm(os.listdir("res/lemmatized_titles_pr_len")):
        docid = int(filename.split(".")[0].split("_")[1])
        try:
            with open(os.path.join("res/lemmatized_titles_pr_len", filename), "r") as read_file:
                jsn = json.load(read_file)
                ul = int(jsn["urllen"])
                dl = int(jsn["doclen"])
                pr = float(jsn["pagerank"])
                max_ul = max(max_ul, ul)
                max_dl = max(max_dl, dl)
                max_pr = max(max_pr, pr)
        except:
            continue

    for filename in tqdm(os.listdir("res/lemmatized_titles_pr_len")):
        docid = int(filename.split(".")[0].split("_")[1])
        try:
            with open(os.path.join("res/lemmatized_titles_pr_len", filename), "r") as read_file:
                jsn = json.load(read_file)
                ul = int(jsn["urllen"])
                dl = int(jsn["doclen"])
                pr = float(jsn["pagerank"])
                res[docid] = "1:" + str(ul / max_ul) + " 2:" + str(dl / max_dl) + " 3:" + str(pr / max_pr)
        except:
            continue

    return res

def get_titles_texts():
    res1 = {}
    res2 = {}
    for filename in tqdm(os.listdir("res/lemmatized_titles_pr_len")):

        docid = int(filename.split(".")[0].split("_")[1])
        try:
            with open(os.path.join("res/lemmatized_titles_pr_len", filename), "r") as read_file:
                jsn = json.load(read_file)
                title = str(jsn["title"])
                text = str(jsn["content"])
                res1[docid] = title
                res2[docid] = text
        except:
            continue


    return res1, res2

def get_relevance(url_id, id_url):
    relevance = {}
    with open('data/2008.xml', 'r', encoding="cp1251") as src:
        raw_xml = src.read()
        soup = BeautifulSoup(raw_xml)

        for task in soup.find_all('task'):
            documents = task.find_all('document')
            vital = {}
            for doc in documents:
                doc['id'] = url_id.get(doc['id'], None)

                if doc['relevance'] == 'vital':
                    vital[doc['id']] = 1
                else:
                    vital[doc['id']] = 0
            relevance[task['id']] = vital

    return relevance

def get_quieries(relevance):
    queries = {}
    with open('data/web2008_adhoc.xml','r', encoding="cp1251") as src:
        raw_xml = src.read()
        soup = BeautifulSoup(raw_xml)
        for task in soup.find_all('task'):
            if task['id'] in relevance:
                queries[task['id']] = task.querytext.string
    return queries

def load():
    f = open("data/pagerank.txt", "r")
    has_vertices = True
    url_id = {}
    id_url = {}
    while has_vertices:
        l = f.readline()
        if len(l) < 2:
            break

        split = l.split(" ")
        docID = int(split[0])
        docURL = split[1]
        url_id[docURL] = docID
        id_url[docID] = docURL

    return url_id, id_url

def count_query_coverage(query_words, text):
    matches = 0
    for word in query_words:
        matches += 1 if word in text else 0
    return matches / len(query_words)


def count_span(qw, tw):
    if len(qw) > len(tw):
        return 0

    words_cnt = {}
    for word in qw:
        words_cnt[word] = 0

    qw = set(qw)
    unique_words_cnt = 0
    l = 0
    ans = len(tw) + 1
    for r in range(0, len(tw)):
        word = tw[r]
        if word in words_cnt:
            words_cnt[word] += 1
            if words_cnt[word] == 1:
                unique_words_cnt += 1

        if unique_words_cnt == len(qw):
            word = tw[l]
            while word not in words_cnt or words_cnt[word] > 1:
                l += 1
                if word in words_cnt:
                    words_cnt[word] -= 1
                word = tw[l]
            ans = min(ans, r - l + 1)

    if ans == len(tw) + 1:
        return 0
    return len(qw) / ans

if __name__== "__main__":
    stem = Mystem()
    titles, texts = get_titles_texts()
    print(texts)
    print(titles)
    features = get_features_str()
    url_id, id_url = load()
    rel = get_relevance(url_id, id_url)
    qs = get_quieries(rel)

    f = open("t32_all.txt", "w")
    max_qlen = 0
    for i in rel.items():
        for j in i[1].items():
            if j[0] is not None and features.get(j[0], None) is not None:
                 max_qlen = max(max_qlen, len(qs[i[0]]))

    for i in rel.items():
        for j in i[1].items():
            if j[0] is not None and features.get(j[0], None) is not None:
                f.write(str(j[1]) + " " "qid:" + str(i[0][3:]) + " " + features[j[0]] + " 4:" + str(len(qs[i[0]]) / max_qlen) +\
                        " 5:" + str(count_query_coverage(stem.lemmatize(qs[i[0]]), titles[j[0]])) +\
                        " 6:" + str(count_query_coverage(stem.lemmatize(qs[i[0]]), texts[j[0]])) +\
                        " 7:" + str(count_span(stem.lemmatize(qs[i[0]]), texts[j[0]])) + "\n")

    f.close()
    with open("res/lemmatized_titles_pr_len/doc_4.json", "r") as read_file:
        data = json.load(read_file)
        print(data["title"])
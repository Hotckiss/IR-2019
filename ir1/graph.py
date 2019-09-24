from urllib.parse import urljoin
from collections import defaultdict
from networkx import pagerank
from text_preproceccing import Set

import networkx as nx

def load_graph():
    f = open("res/links/graph.txt", "r")
    has_vertices = True

    nodes, edges = [], []
    while has_vertices:
        rawID = f.readline()
        if len(rawID) == 0:
            break
        docID = int(rawID)
        docURL = f.readline()[:-1].lower()  # remove end of line
        degree = int(f.readline())
        nodes.append(docURL)
        print(docID)
        for _ in range(degree):
            to_url = f.readline()[:-1]  # remove end of line
            try:
                resolved_to_url = urljoin(docURL, to_url)
            except:
                continue
            success = resolved_to_url.startswith("http")
            if success:
                edges.append((docURL, resolved_to_url))

    print("Graph loaded")
    return (nodes, edges)

def pagerank_graph(n, e):
    graph = nx.DiGraph()

    hash_map = defaultdict(bool)
    for node in n:
        hash_map[node] = True
        graph.add_node(node)

    count = 0
    for ed in e:
        fr, t = ed
        if hash_map[t]:  # edge to doc in collection
            count += 1
            print(str(count) + " completed")
            graph.add_edge(fr, t)

    pr = pagerank(graph)

    sorted_pr = list(map(lambda pair: pair[0], list(reversed(sorted(pr.items(), key=lambda kv: kv[1])))))[:100]

    sn, se = [], []
    for node in n:
        if sorted_pr.__contains__(node):
            sn.append(node)

    hash_map_best = defaultdict(bool)
    for node in sn:
        hash_map_best[node] = True

    f = open("res/graph_top_and.csv", "w")
    for ed in e:
        fr, t = ed
        if hash_map_best[t] and hash_map_best[fr]:  # edge to doc in collection
            count += 1
            print(str(count) + " completed")
            f.write(fr + ";" + t + "\n")

    f.close()


def degree_graph(n, e):

    hash_map = defaultdict(bool)
    for node in n:
        hash_map[node] = True

    degrees = defaultdict(int)
    uniq = defaultdict(Set)

    for ed in e:
        fr, t = ed
        if hash_map[t] and hash_map[fr]:  # edge to doc in collection
            if not uniq[t].contains(fr):
                degrees[t] += 1
                uniq[t].add(fr)

    sorted_pr = list(map(lambda pair: pair[0], list(reversed(sorted(degrees.items(), key=lambda kv: kv[1])))))[:200]

    sn, se = [], []
    for node in n:
        if sorted_pr.__contains__(node):
            sn.append(node)

    print(sn)
    hash_map_best = defaultdict(bool)
    for node in sn:
        hash_map_best[node] = True

    f = open("res/graph_degree.csv", "w")
    for ed in e:
        fr, t = ed
        if hash_map_best[t] and hash_map_best[fr]:  # edge to doc in collection
            f.write(fr + ";" + t + "\n")

    f.close()


def degree_subset(n, e, prefix, fn):
    e = list(filter(lambda edge: str(edge[0]).startswith(prefix) and str(edge[1]).startswith(prefix), e))
    n = list(filter(lambda node: str(node).startswith(prefix), n))

    hash_map = defaultdict(bool)
    for node in n:
        hash_map[node] = True

    f = open("res/graph_" + fn + ".csv", "w")
    for ed in e:
        fr, t = ed
        if hash_map[t] and hash_map[fr]:  # edge to doc in collection
            f.write(fr + ";" + t + "\n")

    f.close()
if __name__ == '__main__':
    n, e = load_graph()
    pagerank_graph(n, e)
    degree_graph(n, e)
    degree_subset(n, e, "http://forum.linux.by", "0")
    degree_subset(n, e, "http://catalog.tut.by", "1")
    degree_subset(n, e, "http://news.extra.by", "2")
    degree_subset(n, e, "http://photoclub.by", "3")
    degree_subset(n, e, "http://forum.billiard.by", "4")
    degree_subset(n, e, "http://atom.by", "5")
    degree_subset(n, e, "http://tut.by", "6")
    degree_subset(n, e, "http://magic.shop.by", "7")
    degree_subset(n, e, "http://litera.by", "8")
    degree_subset(n, e, "http://data.mf.grsu.by", "9")
    degree_subset(n, e, "http://all.by", "10")

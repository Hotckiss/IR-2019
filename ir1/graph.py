from urllib.parse import urlparse
from pathlib import Path
from collections import defaultdict

from networkx import pagerank
import networkx as nx
class URLResolver:
    def __init__(self, docURL):
        self.docURL = docURL
        self.parsed_docURL = urlparse(docURL)

    def apply_edge_url(self, to_url):
        if to_url.startswith("?"):  # params
            return self.docURL + to_url

        try:
            parsed_to_url = urlparse(to_url)
        except:
            return ""

        if len(parsed_to_url.netloc) > 0:    # absolute link
            return to_url
        else:                            # relative link
            pth = str(parsed_to_url.path)
            if len(pth) == 0:            # empty path
                return to_url
            elif pth.startswith("/"):    # path from root
                return self.parsed_docURL.scheme + "://" + self.parsed_docURL.netloc + pth
            elif pth.startswith("../"):  # outer dir
                doc_path = Path(self.parsed_docURL.path)
                to_path = Path(pth)
                new_path = doc_path.joinpath(to_path).resolve()
                return self.parsed_docURL.scheme + "://" + self.parsed_docURL.netloc + str(new_path)
            else:   # inner dir
                doc_path = Path(self.parsed_docURL.path)
                to_path = Path(pth[2:] if pth.startswith("./") else pth)
                if not self.docURL.endswith("/"):
                    doc_path = doc_path.joinpath(Path("../")).resolve()  # move step up
                new_path = doc_path.joinpath(to_path).resolve()
                return self.parsed_docURL.scheme + "://" + self.parsed_docURL.netloc + str(new_path)


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
        resolver = URLResolver(docURL)
        nodes.append(docURL)
        print(docID)
        for _ in range(degree):
            to_url = f.readline()[:-1]  # remove end of line
            if to_url.find("#") == -1:  # docs url do not contain this
                res = resolver.apply_edge_url(to_url).lower()
                success = res.startswith("http")
                if success:
                    edges.append((docURL, res))

    print("Graph loaded")
    return (nodes, edges)

if __name__ == '__main__':
    n, e = load_graph()
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

    sorted_pr = list(map(lambda pair:  pair[0], list(reversed(sorted(pr.items(), key=lambda kv: kv[1])))))[:100]

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

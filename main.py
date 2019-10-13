import base64
from bs4 import BeautifulSoup, Comment
from lxml import etree
import re
import matplotlib.pyplot as plt
import math
import nltk
from nltk.tokenize import word_tokenize, RegexpTokenizer
import html5lib
from multiprocessing import Pool
import json
nltk.download('punkt')

DATA_DIR = "data/"
VOLUME_PREFIX = "byweb."
VOLUMES_COUNT = 10


class Document:
    def __init__(self, content, url, id, parser='html.parser', decode=False):
        self.id = id
        self.parser = parser
        if decode:
            self.url = base64.urlsafe_b64decode(url).decode("cp1251")
            self.content = base64.b64decode(content).decode("cp1251")

        else:
            self.url = url
            self.content = content

    def print_description(self):
        print("ID = " + str(self.id) + "; URL = " + str(self.url) + "; size = " + str(len(self.content)))

    def print_content(self):
        print(self.content)

    def print_text(self):
        print(self.clean_text())

    # can throw exception
    def clean_text(self):
        soup = BeautifulSoup(self.content, self.parser)

        [x.extract() for x in soup.find_all('script')]
        [x.extract() for x in soup.find_all('style')]
        [x.extract() for x in soup.find_all('meta')]
        [x.extract() for x in soup.find_all('noscript')]
        [x.extract() for x in soup.find_all('head')]
        [x.extract() for x in soup.find_all('[document]')]
        [x.extract() for x in soup.find_all('title')]
        [x.extract() for x in soup.find_all('script')]
        [x.extract() for x in soup.find_all('tag')]
        [x.extract() for x in soup.find_all(text=lambda text: isinstance(text, Comment))]

        text = soup.get_text(" ", strip=True)
        t = re.sub("(<!--.*?-->)", "", text, flags=re.DOTALL)
        return t

    def title(self):
        soup = BeautifulSoup(self.content, self.parser)
        for x in soup.find_all('title'):
            return x.get_text()

    # can throw exception
    def print_prettify(self):
        soup = BeautifulSoup(self.content, self.parser)
        print(soup.prettify())

    # can throw exception
    def print_links(self):
        soup = BeautifulSoup(self.content, self.parser)
        for link in soup.find_all('a'):
            href = link.get('href')
            if href is not None:
                print(href)

    # can throw exception
    def save_links(self, file_name):
        soup = BeautifulSoup(self.content, self.parser)
        links = []

        for link in soup.find_all('a'):
            href = link.get('href')
            if href is not None and len(href) > 0:
                cleaned_href = href.replace('\n', '').replace('\t', '').replace('\r', '')
                links.append(cleaned_href)

        f = open(file_name, "a")
        f.write(self.id + "\n")
        f.write(self.url + "\n")
        f.write(str(len(links)) + "\n")
        for link in links:
            f.write(link + "\n")
        f.close()

    # can throw exception
    def make_html(self):
        f = open("res/html/" + "doc_" + str(self.id) + ".html", "w")
        soup = BeautifulSoup(self.content, self.parser)
        f.write(soup.prettify())
        f.close()

    def make_text_file(self):
        f = open("res/text/" + "doc_" + str(self.id) + ".txt", "w", encoding="utf8")
        f.write(self.clean_text())
        f.close()

    def make_text_file_with_title(self):
        f = open("res/text_titles/" + "doc_" + str(self.id) + ".txt", "w", encoding="utf8")
        f.write(self.title() + "\n")
        f.write(self.clean_text())
        f.close()

    def make_text_file_with_title_json(self):
        f = open("res/text_titles_json/" + "doc_" + str(self.id) + ".json", "w", encoding="utf8")
        title = self.title()
        content = self.clean_text()
        jsn = {
            "title": title,
            "content": content
        }
        json.dump(jsn, f, ensure_ascii=False)
        f.close()

    def size(self):
        return len(self.content)

    def decode(self):
        self.url = base64.urlsafe_b64decode(self.url)
        self.content = base64.b64decode(self.content)


class DocumentStatsCollector:
    def __init__(self, remove_punkt=False):
        self.handled = 0
        self.documents_count = 0
        self.completed_with_errors = 0
        self.documents_word_lengths = []
        self.documents_byte_html_lengths = []
        self.documents_byte_html_no_comments_lengths = []
        self.documents_byte_text_lengths = []
        self.remove_punkt = remove_punkt

    def handle(self, document):
        self.handled += 1
        print(str(self.handled) + " docs handled...")

        try:
            clean_text = document.clean_text()
            document.make_text_file()
        except:
            self.completed_with_errors += 1
            return

        self.documents_count += 1
        self.documents_byte_html_lengths.append(len(document.content.encode("utf-8")))
        no_comments_text = re.sub("(<!--.*?-->)", "", document.content, flags=re.DOTALL)
        self.documents_byte_html_no_comments_lengths.append(len(no_comments_text.encode("utf-8")))

        if self.remove_punkt:
            tokenizer = RegexpTokenizer(r'\w+')
            clean_text = " ".join(tokenizer.tokenize(clean_text))
        self.documents_byte_text_lengths.append(len(clean_text.encode("utf-8")))
        self.documents_word_lengths.append(len(clean_text.split()))

    def stats(self):
        bounds_words = [2000, 10000, 0xffffffff]
        bounds_bytes = [20000, 50000, 0xffffffff]

        for i in range(len(bounds_words)):
            filtered_words = list(filter(lambda x: x <= bounds_words[i], self.documents_word_lengths))
            plot_hist(filtered_words, "words_distribution_" + str(i))

        for i in range(len(bounds_bytes)):
            filtered_bytes = list(filter(lambda x: x <= bounds_bytes[i], self.documents_byte_text_lengths))
            plot_hist(filtered_bytes, "bytes_distribution_" + str(i))

        th_ratio = [a / b for a, b in zip(self.documents_byte_text_lengths, self.documents_byte_html_lengths)]
        plot_hist(th_ratio, "th_ratio_distribution")

        th_ratio = [a / b for a, b in
                    zip(self.documents_byte_text_lengths, self.documents_byte_html_no_comments_lengths)]
        plot_hist(th_ratio, "th_ratio_distribution_no_comments")

        f = open("res/task_1_summary.txt", "w")
        f.write("Documents count: " + str(self.documents_count + self.completed_with_errors) + "\n")
        f.write("Average words count: " + str(sum(self.documents_word_lengths) / self.documents_count) + "\n")
        f.write("Average bytes count: " + str(sum(self.documents_byte_text_lengths) / self.documents_count) + "\n")
        f.write("Average text/(text+HTML) value: " + str(
            sum(self.documents_byte_text_lengths) / sum(self.documents_byte_html_lengths)) + "\n")
        f.write("Average text/(text+HTML) value(no comments in HTML): " + str(
            sum(self.documents_byte_text_lengths) / sum(self.documents_byte_html_no_comments_lengths)) + "\n")
        f.close()


def plot_hist(data, file_name, cols_num=20):
    plt.clf()
    plt.hist(data, cols_num)
    plt.savefig("res/plots/" + file_name + ".png")


def process_documents(file_name, handler, limit=None):
    xml_tree = etree.parse(DATA_DIR + file_name + ".xml")
    root = xml_tree.getroot()
    processed = 0

    for document in root.getchildren():
        content, url, id = "", "", ""

        for property in document.getchildren():
            if property.tag == 'docID':
                id = property.text
            elif property.tag == 'docURL':
                url = property.text
            else:
                content = property.text

        document = Document(content, url, id, parser='lxml', decode=True)
        handler.handle(document)

        processed += 1
        if limit is not None and processed >= limit:
            break



def process_volume(volume):
    stats_collector = DocumentStatsCollector(remove_punkt=False)
    print("Process volume " + str(volume + 1) + "...")
    process_documents(VOLUME_PREFIX + str(volume), stats_collector)

def process_volume_titles(vl):
    volume, log = vl
    stats_collector = DocWithTitleHandler(log)
    print("Process volume " + str(volume + 1) + "...")
    process_documents(VOLUME_PREFIX + str(volume), stats_collector)

def multiprocess_main():
    with Pool(10) as pool:
        pool.map(process_volume, range(VOLUMES_COUNT))

def multiprocess_main_titles():
    with Pool(10) as pool:
        pool.map(process_volume_titles, zip(range(VOLUMES_COUNT), [True, False, False, False, False, False, False, False, False, False]))

class DocWithTitleHandler:
    def __init__(self, log):
        self.log = log
        self.handled = 0

    def handle(self, document):
        self.handled += 1
        if self.log:
            print(str(self.handled) + " docs handled...")
        document.make_text_file_with_title_json()

def correct():
    with open("data/task3_test_all.txt") as inp, open("data/task3_test_with_lines.txt", "w") as out:
        test_lines = inp.readlines()
        for i, line in enumerate(test_lines):
            l = "0 " + line.split("\n")[0][3:] + " #line=" + str(i) + "\n"
            out.write(l)

from sklearn.feature_selection import mutual_info_classif
import numpy as np
def importance():
    with open("t32_all.txt") as inp:
        lines = inp.readlines()
        X = np.zeros((len(lines), 8))
        y = np.zeros(len(lines))
        for i, line in enumerate(lines):
            s = line.split("\n")[0].split(" ")
            X[i][0] = float(s[2].split(":")[1])
            X[i][1] = float(s[3].split(":")[1])
            X[i][2] = float(s[4].split(":")[1])
            X[i][3] = float(s[5].split(":")[1])
            X[i][4] = float(s[6].split(":")[1])
            X[i][5] = float(s[7].split(":")[1])
            X[i][6] = float(s[8].split(":")[1])
            X[i][7] = float(s[9].split(":")[1])
            y[i] = s[0]
    return mutual_info_classif(X, y)

import matplotlib.pyplot as plt

if __name__ == '__main__':
    x = [4, 5, 6 ,7]
    y = [




        0.7571032403,
        0.7578100,
        0.7572230,
    0.7600311773]

    plt.clf()
    plt.xlabel('Boost')
    plt.ylabel('r@20')
    plt.plot(x, y)
    plt.savefig("res/plots/dep.png")


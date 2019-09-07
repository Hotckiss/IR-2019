import base64
from bs4 import BeautifulSoup
from lxml import etree
import re
import matplotlib.pyplot as plt
import math

DATA_DIR = "data/"
VOLUME_PREFIX = "byweb."

class Document:
    def __init__(self, content, url, id, decode=False):
        self.id = id
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

    def clean_text(self):
        soup = BeautifulSoup(self.content, 'html.parser')

        text = soup.get_text(" ", strip=True)
        t = re.sub("(<!--.*?-->)", "", text, flags=re.DOTALL)
        return t

    def print_prettify(self):
        soup = BeautifulSoup(self.content, 'html.parser')
        print(soup.prettify())

    def make_html(self):
        f = open("res/html/" + "doc_" + str(self.id) + ".html", "w")
        soup = BeautifulSoup(self.content, 'html.parser')
        f.write(soup.prettify())
        f.close()

    def make_text_file(self):
        f = open("res/text/" + "doc_" + str(self.id) + ".txt", "w")
        f.write(self.clean_text())
        f.close()

    def size(self):
        return len(self.content)

    def decode(self):
        self.url = base64.urlsafe_b64decode(self.url)
        self.content = base64.b64decode(self.content)

class DocumentStatsCollector:
    def __init__(self):
        self.documents_count = 0
        self.documents_word_lengths = []
        self.documents_byte_html_lengths = []
        self.documents_byte_html_no_comments_lengths = []
        self.documents_byte_text_lengths = []

    def handle(self, document):
        self.documents_count += 1
        self.documents_byte_html_lengths.append(len(document.content.encode("utf-8")))
        no_comments_text = re.sub("(<!--.*?-->)", "", document.content, flags=re.DOTALL)
        self.documents_byte_html_no_comments_lengths.append(len(no_comments_text.encode("utf-8")))
        text = document.clean_text()
        self.documents_byte_text_lengths.append(len(text.encode("utf-8")))
        self.documents_word_lengths.append(len(text.split()))

    def stats(self):
        print("Documents count: " + str(self.documents_count))
        print("Average words count: " + str(sum(self.documents_word_lengths) / self.documents_count))
        print("Average bytes count: " + str(sum(self.documents_byte_text_lengths) / self.documents_count))
        print("Average text/(text+HTML) value: " + str(sum(self.documents_byte_text_lengths) / sum(self.documents_byte_html_lengths)))
        print("Average text/(text+HTML) value(no comments in HTML): " + str(sum(self.documents_byte_text_lengths) / sum(self.documents_byte_html_no_comments_lengths)))

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

        th_ratio = [a / b for a, b in zip(self.documents_byte_text_lengths, self.documents_byte_html_no_comments_lengths)]
        plot_hist(th_ratio, "th_ratio_distribution_no_comments")

        f = open("res/task_1_summary.txt", "w")
        f.write("Documents count: " + str(self.documents_count))
        f.write("Average words count: " + str(sum(self.documents_word_lengths) / self.documents_count))
        f.write("Average bytes count: " + str(sum(self.documents_byte_text_lengths) / self.documents_count))
        f.write("Average text/(text+HTML) value: " + str(sum(self.documents_byte_text_lengths) / sum(self.documents_byte_html_lengths)))
        f.write("Average text/(text+HTML) value(no comments in HTML): " + str(sum(self.documents_byte_text_lengths) / sum(self.documents_byte_html_no_comments_lengths)))
        f.close()


def plot_hist(data, file_name, cols_num=20):
    plt.clf()
    plt.hist(data, cols_num)
    plt.savefig("res/plots/" + file_name + ".png")


def extract_documents(file_name, decode=False):
    xml_tree = etree.parse(DATA_DIR + file_name + ".xml")
    root = xml_tree.getroot()
    documents = []
    for document in root.getchildren():
        content, url, id = "", "", ""

        for property in document.getchildren():
            if property.tag == 'docID':
                id = property.text
            elif property.tag == 'docURL':
                url = property.text
            else:
                content = property.text

        documents.append(Document(content, url, id, decode=decode))

    return documents


def process_documents(file_name, handler):
    xml_tree = etree.parse(DATA_DIR + file_name + ".xml")
    root = xml_tree.getroot()
    for document in root.getchildren():
        content, url, id = "", "", ""

        for property in document.getchildren():
            if property.tag == 'docID':
                id = property.text
            elif property.tag == 'docURL':
                url = property.text
            else:
                content = property.text
        if int(id) > 10000:
            break
        document = Document(content, url, id, decode=True)
        handler.handle(document)


if __name__ == '__main__':
    stats_collector = DocumentStatsCollector()
    for volume in range(1):
        print("Process volume " + str(volume))
        process_documents(VOLUME_PREFIX + str(volume), stats_collector)

    stats_collector.stats()

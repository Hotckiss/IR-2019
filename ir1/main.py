import base64
from bs4 import BeautifulSoup
from lxml import etree
import re

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
        soup = BeautifulSoup(self.content)
        print(soup.get_text(" ", strip=True))

    def clean_text(self):
        soup = BeautifulSoup(self.content, 'html.parser')
        return soup.get_text(" ", strip=True)

    def clean_text_no_comments(self):
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

    def make_text_file_no_comments(self):
        f = open("res/text/" + "clean_doc_" + str(self.id) + ".txt", "w")
        f.write(self.clean_text_no_comments())
        f.close()

    def size(self):
        return len(self.content)

    def decode(self):
        self.url = base64.urlsafe_b64decode(self.url)
        self.content = base64.b64decode(self.content)


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


if __name__ == '__main__':
    all_documents = []
    for volume in range(10):
        all_documents.extend(extract_documents(VOLUME_PREFIX + str(volume), decode=True))

    print("Docs count: " + str(len(all_documents)))
    doc = all_documents[0]
    doc.print_description()
    doc.make_html()
    doc.make_text_file_no_comments()
    doc.make_text_file()

from pymystem3 import Mystem
from main import process_documents
from multiprocessing import Pool
from collections import defaultdict
import re
import matplotlib.pyplot as plt
import math
from string import punctuation
from nltk.corpus import stopwords

import nltk
nltk.download('stopwords')

VOLUME_PREFIX = "byweb."
VOLUMES_COUNT = 10

russian_stopwords = stopwords.words("russian")
english_stopwords = stopwords.words("english")
black_list = ["°", "№", "©", "...", "//", "://", "</", "\">", "=\"", "=\'", "\r", "\n", "\t"]


class Set:
    def __init__(self):
        self.set = defaultdict(bool)

    def add(self, elem):
        self.set[elem] = True

    def contains(self, elem):
        return self.set[elem]

    def size(self):
        return len(self.set.keys())


class CollectionDictionary:
    def __init__(self):
        self.dict = defaultdict(int)
        self.words_len_count = 0

    def add(self, word):
        if self.dict[word] == 0:
            self.words_len_count += len(word)
        self.dict[word] += 1

    def get(self, word):
        return self.dict[word]

    def mean_word_len(self):
        return self.words_len_count / len(self.dict.keys())

    def most_freq(self, n):
        return list(reversed(sorted(self.dict.items(), key=lambda kv: kv[1])))[:n]

    def most_freq_values(self, n):
        return list(map(lambda pair: pair[1], list(reversed(sorted(self.dict.items(), key=lambda kv: kv[1])))))[:n]

class MyStemHandler:
    def __init__(self, log_debug=False):
        self.log_debug = log_debug
        self.dictionary = CollectionDictionary()
        self.handled = 0
        self.collection_words_count = 0
        self.total_words_len = 0
        self.idf = defaultdict(Set)
        self.english_check = re.compile(r'[a-z]')
        self.en_words = 0
        self.stopwords_count = 0
        self.stem = Mystem()

    def handle(self, document):
        self.handled += 1
        raw_text = document.clean_text()
        lowercase_text = raw_text.lower()
        words = nltk.word_tokenize(lowercase_text)
        tokens = []
        for word in words:
            tokens.extend(self.stem.lemmatize(word))

        for token in tokens:
            if token in russian_stopwords or token in english_stopwords:
                self.stopwords_count += 1
        tokens = [token for token in tokens if token != " " and token.strip() not in punctuation \
                  and token not in russian_stopwords and token not in english_stopwords \
                  and token not in black_list \
                  and token.find("\r") == -1 \
                  and token.find("\n") == -1 \
                  and token.find("\t") == -1 \
                  and not token.isdigit()]

        self.collection_words_count += len(tokens)
        for token in tokens:
            self.dictionary.add(token)
            self.idf[token].add(document.id)
            self.total_words_len += len(token)

            if self.english_check.match(token):
                self.en_words += 1

        if self.log_debug:
            print(str(self.handled) + " handled")

        if self.handled % 1000 == 0:
            self.stats()

        return tokens

    # 1 - % of stop words
    # 2 - mean word len in collection
    # 3 - mean word len in dict
    # 4 - % of english words
    # 5 - freq
    # 6 - idf
    # 7 - plot
    def stats(self):

        f = open("res/task_2_summary.txt", "w")

        # 1
        f.write("Stopwords value: " + str(self.stopwords_count / self.collection_words_count) + "\n")
        # 2
        f.write("Mean word len in collection: " + str(self.total_words_len / self.collection_words_count) + "\n")
        # 3
        f.write("Mean word len in dict: " + str(self.dictionary.mean_word_len()) + "\n")
        # 4
        f.write("Average english words count: " + str(self.en_words / self.collection_words_count) + "\n")

        # 5
        top_n = 10000
        top_dict = self.dictionary.most_freq(top_n)
        f.write("Top words from dict (cf):" + "\n")
        for word in top_dict:
            f.write(str(word[0]) + " " + str(word[1]) + "\n")

        # 6
        top_dict_idf = list(reversed(sorted(self.idf.items(), key=lambda kv: kv[1].size())))[:top_n]
        f.write("Top words from dict (idf):" + "\n")
        for word in top_dict_idf:
            f.write(str(word[0]) + " " + str(word[1].size()) + "\n")

        # 7

        plt.clf()
        x = range(top_n)
        y = [math.log2(a) for a in self.dictionary.most_freq_values(top_n)]
        plt.plot(x, y)
        plt.savefig("res/plots/rank_freq.png")

        f.close()


def process_volume(vl):
    volume, log = vl
    handler = MyStemHandler(log)
    print("Process volume " + str(volume + 1) + "...")
    process_documents(VOLUME_PREFIX + str(volume), handler)

def multiprocess_main():
    with Pool(10) as pool:
        pool.map(process_volume, zip(range(VOLUMES_COUNT), [True, False, False, False, False, False, False, False, False, False]))

def debug():
    handler = MyStemHandler(log_debug=True)
    for i in range(VOLUMES_COUNT):
        process_documents(VOLUME_PREFIX + str(i), handler)
    handler.stats()

if __name__ == "__main__":
    debug()


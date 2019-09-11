from multiprocessing import Pool
from main import process_documents

DATA_DIR = "data/"
VOLUME_PREFIX = "byweb."
VOLUMES_COUNT = 10


class GraphBuilder:
    def __init__(self, volume, log=False):
        self.handled = 0
        self.volume = volume
        self.log = log

    def handle(self, document):
        self.handled += 1
        if self.log:
            print(str(self.handled) + " docs handled...")

        document.save_links("res/links/graph_" + str(self.volume) + ".txt")


def process_volume(vl):
    volume, log = vl
    builder = GraphBuilder(volume, log)
    print("Process volume " + str(volume + 1) + "...")
    process_documents(VOLUME_PREFIX + str(volume), builder)


def merge_files():
    with open("res/links/graph.txt", 'w') as outfile:
        for volume in range(VOLUMES_COUNT):
            file_name = "res/links/graph_" + str(volume) + ".txt"
            with open(file_name) as infile:
                for line in infile:
                    outfile.write(line)


if __name__ == '__main__':
    with Pool(10) as pool:
        pool.map(process_volume, zip(range(VOLUMES_COUNT), [True, False, False, False, False, False, False, False, False, False]))

import sys

imat_name = "data/task3_train.txt"
imat_name_out = "data/task3_train_all.txt"

def add_zeros():
    with open("data/task3_test.txt") as inp, open("data/task3_test_all.txt", "w") as out:
        for line in inp.readlines():
            line_split = line.split(" ")
            out.write(line_split[0] + " " + line_split[1])
            ptr = 2
            for i in range(1, 246):
                try:
                    if (ptr < len(line_split) and int(line_split[ptr].split(":")[0]) == i):
                        out.write(" " + line_split[ptr].split("\n")[0])
                        ptr += 1
                    else:
                        out.write(" " + str(i) + ":0")
                except:
                    return
            out.write("\n")

def main():
    print("Started formatter\n")
    add_zeros()

if __name__== "__main__":
  main()

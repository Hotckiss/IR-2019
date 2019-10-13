import json
import os
from tqdm import tqdm

path_to_text_files = "data/filtered_tokens_texts2/"
path_to_json_files = "data/json_filtered_tokens_texts/"

path_to_text_files2 = "data/text"
path_to_json_files2 = "data/json_text"


path_to_text_files3 = "res/lemmatized"
path_to_json_files3 = "data/json_text_lemmatized_full"

def to_json(inputdir, outputdir):
    for filename in tqdm(os.listdir(inputdir)):
        try:
            with open(os.path.join(inputdir, filename), "r", encoding="utf8") as file:
                content = {
                    "text": file.read()
                }
                json_filename = os.path.splitext(filename)[0] + ".json"
                with open(os.path.join(outputdir, json_filename), "w+", encoding="utf8") as json_file:
                    json.dump(content, json_file, ensure_ascii=False)
        except:
            continue


if __name__ == "__main__":
    to_json(path_to_text_files3, path_to_json_files3)

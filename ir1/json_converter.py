import json
import os
from tqdm import tqdm

path_to_text_files = "data/filtered_tokens_texts/"
path_to_json_files = "data/json_filtered_tokens_texts/"


def to_json():
    for filename in tqdm(os.listdir(path_to_text_files)):
        with open(os.path.join(path_to_text_files, filename), "r", encoding="utf8") as file:
            content = {
                "text": file.read()
            }
            json_filename = os.path.splitext(filename)[0] + ".json"
            with open(os.path.join(path_to_json_files, json_filename), "w+", encoding="utf8") as json_file:
                json.dump(content, json_file, ensure_ascii=False)


to_json()

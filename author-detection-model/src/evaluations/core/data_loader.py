import os
import json

def load_data(key, data_dir="../eval_data"):
    file_path = os.path.join(os.path.dirname(__file__), data_dir, f"{key}.json")
    with open(file_path) as fp:
        data = json.load(fp)
        return data
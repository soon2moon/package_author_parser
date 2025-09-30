import os
import json
from datetime import datetime

def compose_result(query, prompt, response, duration):
    result = {
            'id':query["id"],
            'prompt' : prompt,
            'eval_type': query["eval_type"],
            'query': query["text"],
            'time': duration,
            'response':response.answer,
            'scores':response.info["scores"],
            'context':response.info["context"]
        }
    return result

def log_results(key, result, save_dir="../eval_results"):
    save_dir = os.path.join(os.path.dirname(__file__), save_dir)
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    save_path = os.path.join(save_dir, "{0}-{1}.json".format(key, timestamp))

    with open(save_path, "w") as fp:
        json.dump(result, fp)
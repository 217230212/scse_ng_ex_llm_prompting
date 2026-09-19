import json
import os


def load_items(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    return data["items"]


def get_unclaimed_items(items):
    return [item for item in items if item["status"] == "unclaimed"]


def save_result(result, filename):
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(filename, "w") as f:
        json.dump(result, f, indent=4)

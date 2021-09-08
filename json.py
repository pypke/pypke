import json
from pathlib import Path


def get_path():
    """
    A function to get the current path to bot.py\n
    Returns:
     - cwd (string): The Path To The main.py Directory
    """
    cwd = Path(__file__).parents[1]
    cwd = str(cwd)
    return cwd


def read_json(filename):
    """
    A function to read a json file and return the data.\n
    Params:
     - filename (string): The name of the file to open\n
    Returns:
     - data (dict): A dict of the data in the file
    """
    cwd = get_path()
    with open(cwd + "/bot_config/" + filename + ".json", "r") as file:
        data = json.load(file)
    return data


def write_json(data, filename):
    """
    A function used to write data to a json file\n
    Params:
     - data (dict): The data to write to the file
     - filename (string): The name of the file to write to
    """
    cwd = get_path()
    with open(cwd + "/bot_config/" + filename + ".json", "w") as file:
        json.dump(data, file, indent=4)
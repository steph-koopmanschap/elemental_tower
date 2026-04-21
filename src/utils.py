import json
import os

# Load pre-defined towers from .json file.
def load_tower_definitions() -> dict:
    filename = "towers.json"
    print("Loading from file: ", filename)
    with open(filename, 'r') as json_file:
        tower_defs = json.load(json_file)
    print("File loaded.")
    return tower_defs


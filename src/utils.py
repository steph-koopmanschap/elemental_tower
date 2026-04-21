import json
import os


def load_tower_definitions() -> list:
    """Load pre-defined tower data from towers.json."""
    filename = "towers.json"
    print("Loading from file: ", filename)
    with open(filename, 'r') as json_file:
        tower_defs = json.load(json_file)
    print("File loaded.")
    return tower_defs


def load_level(path: str) -> dict | None:
    """Load a level from a .json file. Returns the level dict or None on error."""
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        print(f"Level loaded: {os.path.basename(path)}")
        return data
    except Exception as e:
        print(f"Failed to load level: {e}")
        return None


# Tile type constants (must match level_editor.py)
TILE_EMPTY = 0
TILE_PATH  = 1
TILE_START = 2
TILE_END   = 3


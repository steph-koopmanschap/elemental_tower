import json
import os
from src.settings import TILE_SIZE

# Tile type constants (must match level_editor.py)
TILE_EMPTY = 0
TILE_PATH  = 1
TILE_START = 2
TILE_END   = 3


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


def build_waypoints(grid: list) -> list:
    """
    Walk the path tiles in the grid from START → END using BFS/flood-fill
    and return an ordered list of pixel-centre coordinates.

    Returns a list of (px_x, px_y) tuples.
    """
    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    # Find start cell
    start = None
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == TILE_START:
                start = (c, r)
                break
        if start:
            break

    if not start:
        print("build_waypoints: no START tile found")
        return []

    # Walk the connected path greedily (each cell has at most 2 path neighbours)
    path = [start]
    visited = {start}

    while True:
        cc, cr = path[-1]
        found_next = False
        for dc, dr in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nc, nr = cc + dc, cr + dr
            if (nc, nr) in visited:
                continue
            if 0 <= nr < rows and 0 <= nc < cols:
                t = grid[nr][nc]
                if t in (TILE_PATH, TILE_END):
                    path.append((nc, nr))
                    visited.add((nc, nr))
                    found_next = True
                    if t == TILE_END:
                        break
        if not found_next:
            break

    # Convert grid cells to pixel centres
    half = TILE_SIZE // 2
    return [(c * TILE_SIZE + half, r * TILE_SIZE + half) for c, r in path]


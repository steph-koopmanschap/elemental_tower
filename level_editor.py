"""
Level Editor for Tower Defense
================================
Run from the project root:  python level_editor.py

Controls
--------
  Left-click          Place selected block type on tile
  Right-click         Erase tile (set to empty)
  1                   Select PATH tool
  2                   Select START tool  (only one allowed)
  3                   Select END tool    (only one allowed)
  S                   Open file-manager to Save level
  L                   Open file-manager to Load level
  C                   Clear the entire grid
  ESC                 Quit
"""

import sys
import os
import json
import subprocess
import pygame

# ---------------------------------------------------------------------------
# Constants (mirrors src/settings.py so the editor matches the game)
# ---------------------------------------------------------------------------
SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
FPS           = 60

TOOLBAR_H  = 80          # top toolbar
STATUSBAR_H = 32         # bottom status bar
GRID_Y      = TOOLBAR_H
GRID_H      = SCREEN_HEIGHT - TOOLBAR_H - STATUSBAR_H

TILE_SIZE = 64
COLS = SCREEN_WIDTH // TILE_SIZE           # 20
ROWS = GRID_H       // TILE_SIZE           # 9

# Tile types
EMPTY = 0
PATH  = 1
START = 2
END   = 3

TILE_COLORS = {
    EMPTY: (40,  40,  40),
    PATH:  (160, 130, 80),
    START: (34,  180, 34),
    END:   (220, 50,  50),
}

TILE_LABELS = {
    PATH:  "PATH",
    START: "START",
    END:   "END",
}

# UI colours
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GRAY       = (100, 100, 100)
DARK_GRAY  = (40,  40,  40)
MID_GRAY   = (60,  60,  60)
LIGHT_GRAY = (180, 180, 180)
GOLD       = (212, 175, 55)
HIGHLIGHT  = (255, 220, 60)

LEVELS_DIR = "levels"

# ---------------------------------------------------------------------------

def _open_file_dialog(mode: str, initial_dir: str) -> str | None:
    """
    Opens a GTK file-chooser via zenity (standard on Ubuntu).
    mode: 'save' or 'open'
    Returns the chosen path string, or None if cancelled.
    """
    os.makedirs(initial_dir, exist_ok=True)
    cmd = ["zenity", "--file-selection",
           f"--filename={os.path.abspath(initial_dir)}/",
           "--file-filter=JSON files (*.json) | *.json",
           "--title=Tower Defense Level Editor"]
    if mode == "save":
        cmd.append("--save")
        cmd.append("--confirm-overwrite")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        path = result.stdout.strip()
        if path:
            if mode == "save" and not path.endswith(".json"):
                path += ".json"
            return path
    except FileNotFoundError:
        # zenity not available — fall back to a simple console prompt
        print(f"[level_editor] zenity not found. Enter file path manually.")
        path = input(f"{'Save' if mode=='save' else 'Load'} path: ").strip()
        if path:
            if mode == "save" and not path.endswith(".json"):
                path += ".json"
            return path
    return None


# ---------------------------------------------------------------------------

class LevelEditor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defense — Level Editor")
        self.clock = pygame.time.Clock()
        self.running = True

        self.grid      = [[EMPTY] * COLS for _ in range(ROWS)]
        self.tool      = PATH          # currently selected tool
        self.status    = "New level — start drawing!  |  1=Path  2=Start  3=End  S=Save  L=Load  C=Clear"
        self.painting  = False         # mouse held down

        self.font_ui     = pygame.font.SysFont("monospace", 15, bold=True)
        self.font_small  = pygame.font.SysFont("monospace", 13)
        self.font_coords = pygame.font.SysFont("monospace", 11)

    # -----------------------------------------------------------------------
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self._handle_events()
            self._draw()

    # -----------------------------------------------------------------------
    def _handle_events(self):
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if   event.key == pygame.K_ESCAPE: self.running = False
                elif event.key == pygame.K_1:      self.tool = PATH;  self.status = "Tool: PATH"
                elif event.key == pygame.K_2:      self.tool = START; self.status = "Tool: START  (only one allowed)"
                elif event.key == pygame.K_3:      self.tool = END;   self.status = "Tool: END    (only one allowed)"
                elif event.key == pygame.K_c:      self._clear(); self.status = "Grid cleared."
                elif event.key == pygame.K_s:      self._save_dialog()
                elif event.key == pygame.K_l:      self._load_dialog()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.painting = True
                    self._paint(mx, my)
                elif event.button == 3:
                    self._erase(mx, my)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.painting = False

            elif event.type == pygame.MOUSEMOTION:
                if self.painting:
                    self._paint(mx, my)

    # -----------------------------------------------------------------------
    def _tile_at(self, mx, my):
        """Return (col, row) if mouse is over the grid, else None."""
        if my < GRID_Y or my >= GRID_Y + GRID_H:
            return None
        col = mx // TILE_SIZE
        row = (my - GRID_Y) // TILE_SIZE
        if 0 <= col < COLS and 0 <= row < ROWS:
            return col, row
        return None

    def _paint(self, mx, my):
        tile = self._tile_at(mx, my)
        if tile is None:
            return
        col, row = tile

        # START and END are unique — remove any existing one first
        if self.tool == START:
            self._remove_tile_type(START)
        elif self.tool == END:
            self._remove_tile_type(END)

        self.grid[row][col] = self.tool

    def _erase(self, mx, my):
        tile = self._tile_at(mx, my)
        if tile:
            col, row = tile
            self.grid[row][col] = EMPTY

    def _remove_tile_type(self, tile_type):
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] == tile_type:
                    self.grid[r][c] = EMPTY

    def _clear(self):
        self.grid = [[EMPTY] * COLS for _ in range(ROWS)]

    # -----------------------------------------------------------------------
    def _validate(self):
        """Returns (ok, message)."""
        has_start = any(self.grid[r][c] == START for r in range(ROWS) for c in range(COLS))
        has_end   = any(self.grid[r][c] == END   for r in range(ROWS) for c in range(COLS))
        if not has_start:
            return False, "Missing START block."
        if not has_end:
            return False, "Missing END block."
        return True, "OK"

    # -----------------------------------------------------------------------
    def _save_dialog(self):
        ok, msg = self._validate()
        if not ok:
            self.status = f"Cannot save: {msg}"
            return

        path = _open_file_dialog("save", LEVELS_DIR)
        if path:
            self._save(path)
        else:
            self.status = "Save cancelled."

    def _save(self, path):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        data = {
            "cols": COLS,
            "rows": ROWS,
            "tile_size": TILE_SIZE,
            "grid": self.grid          # 2-D list of ints
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        self.status = f"Saved: {os.path.basename(path)}"

    def _load_dialog(self):
        path = _open_file_dialog("open", LEVELS_DIR)
        if path:
            self._load(path)
        else:
            self.status = "Load cancelled."

    def _load(self, path):
        try:
            with open(path) as f:
                data = json.load(f)
            loaded = data["grid"]
            # Accept grids that differ in size — pad / truncate gracefully
            self.grid = [[EMPTY] * COLS for _ in range(ROWS)]
            for r in range(min(len(loaded), ROWS)):
                for c in range(min(len(loaded[r]), COLS)):
                    self.grid[r][c] = loaded[r][c]
            self.status = f"Loaded: {os.path.basename(path)}"
        except Exception as e:
            self.status = f"Load error: {e}"

    # -----------------------------------------------------------------------
    def _draw(self):
        self.screen.fill(DARK_GRAY)
        self._draw_grid()
        self._draw_toolbar()
        self._draw_statusbar()
        pygame.display.flip()

    # -----------------------------------------------------------------------
    def _draw_grid(self):
        mx, my = pygame.mouse.get_pos()
        hover  = self._tile_at(mx, my)

        for row in range(ROWS):
            for col in range(COLS):
                x = col * TILE_SIZE
                y = GRID_Y + row * TILE_SIZE
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

                tile_type = self.grid[row][col]
                color     = TILE_COLORS[tile_type]
                pygame.draw.rect(self.screen, color, rect)

                # Label for special tiles
                if tile_type in TILE_LABELS:
                    lbl = self.font_small.render(TILE_LABELS[tile_type], True, WHITE)
                    self.screen.blit(lbl, (x + TILE_SIZE//2 - lbl.get_width()//2,
                                           y + TILE_SIZE//2 - lbl.get_height()//2))

                # Grid lines
                pygame.draw.rect(self.screen, GRAY, rect, 1)

                # Hover highlight
                if hover == (col, row):
                    hl = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    hl.fill((*HIGHLIGHT, 70))
                    self.screen.blit(hl, (x, y))

        # Coordinate labels (every 5 columns and every row)
        for col in range(0, COLS, 5):
            s = self.font_coords.render(str(col), True, GRAY)
            self.screen.blit(s, (col * TILE_SIZE + 2, GRID_Y + 2))
        for row in range(ROWS):
            s = self.font_coords.render(str(row), True, GRAY)
            self.screen.blit(s, (2, GRID_Y + row * TILE_SIZE + 2))

    # -----------------------------------------------------------------------
    def _draw_toolbar(self):
        bar = pygame.Rect(0, 0, SCREEN_WIDTH, TOOLBAR_H)
        pygame.draw.rect(self.screen, MID_GRAY, bar)
        pygame.draw.line(self.screen, GRAY, (0, TOOLBAR_H - 1), (SCREEN_WIDTH, TOOLBAR_H - 1), 1)

        title = self.font_ui.render("LEVEL EDITOR", True, GOLD)
        self.screen.blit(title, (14, 10))

        # Tool buttons
        tools = [
            (PATH,  "1 — Path",  TILE_COLORS[PATH]),
            (START, "2 — Start", TILE_COLORS[START]),
            (END,   "3 — End",   TILE_COLORS[END]),
        ]
        bw, bh = 130, 36
        bx = 200
        for tool_id, label, color in tools:
            brect = pygame.Rect(bx, (TOOLBAR_H - bh) // 2, bw, bh)
            pygame.draw.rect(self.screen, color, brect, border_radius=6)
            border = HIGHLIGHT if self.tool == tool_id else (70, 70, 70)
            bwidth = 3 if self.tool == tool_id else 1
            pygame.draw.rect(self.screen, border, brect, bwidth, border_radius=6)
            ls = self.font_ui.render(label, True, WHITE)
            self.screen.blit(ls, (brect.centerx - ls.get_width()//2,
                                   brect.centery - ls.get_height()//2))
            bx += bw + 10

        # Action hints
        hints = [
            ("S — Save",  GOLD),
            ("L — Load",  (160, 220, 255)),
            ("C — Clear", (220, 150, 50)),
            ("ESC — Quit",(180, 100, 100)),
        ]
        hx = SCREEN_WIDTH - 20
        for text, color in reversed(hints):
            hs = self.font_ui.render(text, True, color)
            hx -= hs.get_width() + 20
            self.screen.blit(hs, (hx, (TOOLBAR_H - hs.get_height()) // 2))

        # Right-click hint
        rc = self.font_small.render("Right-click = erase", True, GRAY)
        self.screen.blit(rc, (14, TOOLBAR_H - rc.get_height() - 6))

    # -----------------------------------------------------------------------
    def _draw_statusbar(self):
        y = SCREEN_HEIGHT - STATUSBAR_H
        bar = pygame.Rect(0, y, SCREEN_WIDTH, STATUSBAR_H)
        pygame.draw.rect(self.screen, (30, 30, 38), bar)
        pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH, y), 1)

        # Tile counts
        path_n  = sum(self.grid[r][c] == PATH  for r in range(ROWS) for c in range(COLS))
        start_n = sum(self.grid[r][c] == START for r in range(ROWS) for c in range(COLS))
        end_n   = sum(self.grid[r][c] == END   for r in range(ROWS) for c in range(COLS))

        info = f"  Path tiles: {path_n}   Start: {start_n}/1   End: {end_n}/1   |   {self.status}"
        ts = self.font_small.render(info, True, LIGHT_GRAY)
        self.screen.blit(ts, (8, y + (STATUSBAR_H - ts.get_height()) // 2))

    # -----------------------------------------------------------------------
    def quit(self):
        pygame.quit()


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    editor = LevelEditor()
    try:
        editor.run()
    finally:
        editor.quit()

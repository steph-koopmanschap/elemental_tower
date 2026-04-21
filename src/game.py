import pygame
from src.settings import *
from src.utils import load_tower_definitions, load_level, TILE_PATH, TILE_START, TILE_END, TILE_EMPTY
from src.hud import HUD
from src.tower import Tower
from src.info_screen import InfoScreen

# Colours for path tiles drawn in game
_PATH_COLOR  = (160, 130, 80)
_START_COLOR = (34,  180, 34)
_END_COLOR   = (220, 50,  50)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock   = pygame.time.Clock()
        self.running = True

        # Player state
        self.money = STARTING_MONEY
        self.lives = STARTING_LIVES

        # Tower data — loaded from towers.json
        self.tower_defs = load_tower_definitions()

        # Level grid — None means no level loaded (all tiles placeable)
        self.level_grid  = None    # 2-D list of ints, set by load_level()
        self.path_cells  = set()   # (col, row) cells that are PATH/START/END

        # Placed towers
        self.placed_towers  = []
        self.occupied_cells = set()

        # Selection / cursor
        self.selected_slot = None
        self.cursor_tile   = None

        # UI helpers
        self.hud         = HUD()
        self.info_screen = InfoScreen()
        self.show_info   = False

        self.font_small = pygame.font.SysFont("monospace", 14)
        self.font_label = pygame.font.SysFont("monospace", 12)

    # ------------------------------------------------------------------
    def load_level_file(self, path: str):
        """Load a level .json file and register its path cells."""
        data = load_level(path)
        if data is None:
            return
        self.level_grid = data["grid"]
        self.path_cells = set()
        for r, row in enumerate(self.level_grid):
            for c, tile in enumerate(row):
                if tile in (TILE_PATH, TILE_START, TILE_END):
                    self.path_cells.add((c, r))
        # Remove any already-placed towers that are now on the path
        self.placed_towers  = [t for t in self.placed_towers
                               if (t.col, t.row) not in self.path_cells]
        self.occupied_cells = {(t.col, t.row) for t in self.placed_towers}

    # ------------------------------------------------------------------
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

    # ------------------------------------------------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.show_info = not self.show_info
                elif event.key == pygame.K_ESCAPE:
                    if self.show_info:
                        self.show_info = False
                    elif self.selected_slot is not None:
                        self.selected_slot = None
                    else:
                        self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.show_info:
                    self._handle_click(event.pos)

    def _handle_click(self, pos):
        slot_i = self.hud.get_slot_at(pos)
        if slot_i is not None:
            tdef = self.tower_defs[slot_i]
            if tdef["unlocked"]:
                self.selected_slot = None if self.selected_slot == slot_i else slot_i
            return

        col, row = pos[0] // TILE_SIZE, pos[1] // TILE_SIZE
        if 0 <= col < COLS and 0 <= row < ROWS:
            self._try_place_tower(col, row)

    def _try_place_tower(self, col, row):
        if self.selected_slot is None:
            return
        tdef = self.tower_defs[self.selected_slot]
        if not tdef["unlocked"]:
            return
        if (col, row) in self.occupied_cells:
            return
        if (col, row) in self.path_cells:      # ← blocked by path
            return
        if self.money < tdef["cost"]:
            return
        self.money -= tdef["cost"]
        self.placed_towers.append(Tower(tdef, col, row))
        self.occupied_cells.add((col, row))

    # ------------------------------------------------------------------
    def update(self):
        mx, my = pygame.mouse.get_pos()
        col, row = mx // TILE_SIZE, my // TILE_SIZE
        if 0 <= col < COLS and 0 <= row < ROWS and my < GAME_HEIGHT:
            self.cursor_tile = (col, row)
        else:
            self.cursor_tile = None

    # ------------------------------------------------------------------
    def draw(self):
        self.screen.fill(DARK_GRAY)
        self._draw_grid()
        self._draw_towers()
        self._draw_placement_preview()
        self.hud.draw(self.screen, self.money, self.lives,
                      self.tower_defs, self.selected_slot)
        if self.show_info:
            self.info_screen.draw(self.screen, self.tower_defs)
        pygame.display.flip()

    def _draw_grid(self):
        for row in range(ROWS):
            for col in range(COLS):
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE,
                                   TILE_SIZE, TILE_SIZE)

                # Determine tile colour
                if self.level_grid is not None and row < len(self.level_grid) and col < len(self.level_grid[row]):
                    tile = self.level_grid[row][col]
                    if tile == TILE_PATH:
                        pygame.draw.rect(self.screen, _PATH_COLOR, rect)
                    elif tile == TILE_START:
                        pygame.draw.rect(self.screen, _START_COLOR, rect)
                        lbl = self.font_label.render("START", True, WHITE)
                        self.screen.blit(lbl, (rect.centerx - lbl.get_width()//2,
                                               rect.centery - lbl.get_height()//2))
                    elif tile == TILE_END:
                        pygame.draw.rect(self.screen, _END_COLOR, rect)
                        lbl = self.font_label.render("END", True, WHITE)
                        self.screen.blit(lbl, (rect.centerx - lbl.get_width()//2,
                                               rect.centery - lbl.get_height()//2))

                pygame.draw.rect(self.screen, GRAY, rect, 1)

    def _draw_towers(self):
        for tower in self.placed_towers:
            tower.draw(self.screen)

    def _draw_placement_preview(self):
        if self.selected_slot is None or self.cursor_tile is None:
            return
        col, row   = self.cursor_tile
        tdef       = self.tower_defs[self.selected_slot]
        blocked    = (col, row) in self.occupied_cells or (col, row) in self.path_cells
        affordable = self.money >= tdef["cost"]
        rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

        ghost = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        if blocked or not affordable:
            ghost.fill((220, 50, 50, 100))
            self.screen.blit(ghost, rect.topleft)
            pygame.draw.rect(self.screen, RED, rect, 2)
        else:
            r, g, b = tdef["color"]
            ghost.fill((r, g, b, 120))
            self.screen.blit(ghost, rect.topleft)
            pygame.draw.rect(self.screen, WHITE, rect, 2)

        label = self.font_small.render(f"-${tdef['cost']}", True,
                                       RED if not affordable else GOLD)
        self.screen.blit(label, (rect.x + 4, rect.y - 18))

    # ------------------------------------------------------------------
    def quit(self):
        pygame.quit()


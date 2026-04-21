import pygame
import os
from src.settings import *
from src.utils import (load_tower_definitions, load_level,
                        TILE_PATH, TILE_START, TILE_END, TILE_EMPTY,
                        build_waypoints)
from src.hud import HUD
from src.tower import Tower
from src.info_screen import InfoScreen
from src.wave_manager import WaveManager, WAITING_FOR_START, GAME_OVER
from src.upgrade_screen import UpgradeScreen

# Tile colours
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

        # Fonts
        self.font_small    = pygame.font.SysFont("monospace", 14)
        self.font_label    = pygame.font.SysFont("monospace", 12)
        self.font_gameover = pygame.font.SysFont("monospace", 72, bold=True)
        self.font_go_sub   = pygame.font.SysFont("monospace", 26)

        # Player state
        self.money     = STARTING_MONEY
        self.lives     = STARTING_LIVES
        self.game_over = False

        # Tower data
        self.tower_defs = load_tower_definitions()

        # Level
        self.level_grid  = None
        self.path_cells  = set()
        self.waypoints   = []

        # Towers placed on map
        self.placed_towers  = []
        self.occupied_cells = set()

        # Live projectiles
        self.projectiles = []

        # Selection / cursor
        self.selected_slot = None
        self.cursor_tile   = None

        # Wave manager (created after level load)
        self.wave_manager = None

        # UI
        self.hud         = HUD()
        self.info_screen   = InfoScreen()
        self.show_info     = False
        self.upgrade_screen = UpgradeScreen()

        # Load default level
        if os.path.exists(DEFAULT_LEVEL):
            self._load_level(DEFAULT_LEVEL)
        else:
            print(f"Warning: default level not found: {DEFAULT_LEVEL}")
            self.wave_manager = WaveManager([])

    # ------------------------------------------------------------------
    def _load_level(self, path: str):
        data = load_level(path)
        if data is None:
            self.wave_manager = WaveManager([])
            return

        self.level_grid = data["grid"]
        self.path_cells = set()
        for r, row in enumerate(self.level_grid):
            for c, tile in enumerate(row):
                if tile in (TILE_PATH, TILE_START, TILE_END):
                    self.path_cells.add((c, r))

        self.waypoints    = build_waypoints(self.level_grid)
        self.wave_manager = WaveManager(self.waypoints)

        self.placed_towers  = [t for t in self.placed_towers
                               if (t.col, t.row) not in self.path_cells]
        self.occupied_cells = {(t.col, t.row) for t in self.placed_towers}
        self.projectiles    = []

    # ------------------------------------------------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()

    # ------------------------------------------------------------------
    def _handle_events(self):
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
                if self.game_over:
                    return
                if self.upgrade_screen.visible:
                    self.upgrade_screen.handle_click(event.pos)
                elif not self.show_info:
                    self._handle_click(event.pos)

    def _handle_click(self, pos):
        if self.hud.start_button_rect and self.hud.start_button_rect.collidepoint(pos):
            if self.wave_manager:
                self.wave_manager.start_game()
            return

        slot_i = self.hud.get_slot_at(pos)
        if slot_i is not None:
            tdef = self.tower_defs[slot_i]
            if tdef["unlocked"]:
                self.selected_slot = None if self.selected_slot == slot_i else slot_i
            return

        col, row = pos[0] // TILE_SIZE, pos[1] // TILE_SIZE
        if 0 <= col < COLS and 0 <= row < ROWS:
            # Check if there's already a tower here — open upgrade screen
            clicked_tower = next(
                (t for t in self.placed_towers if t.col == col and t.row == row), None)
            if clicked_tower:
                self.upgrade_screen.show(
                    clicked_tower,
                    get_money_fn   = lambda: self.money,
                    spend_money_fn = lambda n: setattr(self, 'money', self.money - n),
                )
                self.selected_slot = None
            else:
                self._try_place_tower(col, row)

    def _try_place_tower(self, col, row):
        if self.selected_slot is None:
            return
        tdef = self.tower_defs[self.selected_slot]
        if not tdef["unlocked"]:
            return
        if (col, row) in self.occupied_cells or (col, row) in self.path_cells:
            return
        if self.money < tdef["cost"]:
            return
        self.money -= tdef["cost"]
        self.placed_towers.append(Tower(tdef, col, row))
        self.occupied_cells.add((col, row))

    # ------------------------------------------------------------------
    def _update(self, dt: float):
        if self.game_over:
            return

        # Cursor
        mx, my = pygame.mouse.get_pos()
        col, row = mx // TILE_SIZE, my // TILE_SIZE
        if 0 <= col < COLS and 0 <= row < ROWS and my < GAME_HEIGHT:
            self.cursor_tile = (col, row)
        else:
            self.cursor_tile = None

        # Wave manager — moves enemies, returns outcomes
        if self.wave_manager:
            lives_lost, money_earned = self.wave_manager.update(dt)
            self.lives -= lives_lost
            self.money += money_earned
            if self.lives <= 0:
                self.lives     = 0
                self.game_over = True

        # Towers — pick targets and fire
        if self.wave_manager:
            enemies = self.wave_manager.enemies
            for tower in self.placed_towers:
                new_projs = tower.update(dt, enemies)
                self.projectiles.extend(new_projs)

        # Projectiles — move, detect hits, collect money from kills
        live_projs = []
        for proj in self.projectiles:
            proj.update(dt)
            if not proj.expired:
                live_projs.append(proj)
            elif proj.hit:
                if proj.target.dead:
                    self.money        += proj.target.reward
                    proj.target.reward = 0   # prevent double-credit
        self.projectiles = live_projs

        # DOT kills — enemies that died from damage-over-time this frame
        if self.wave_manager:
            for enemy in getattr(self.wave_manager, 'dot_kills', []):
                if enemy.reward > 0:
                    self.money        += enemy.reward
                    enemy.reward       = 0

    # ------------------------------------------------------------------
    def _draw(self):
        self.screen.fill(DARK_GRAY)
        self._draw_grid()
        self._draw_towers()

        if self.wave_manager:
            self.wave_manager.draw(self.screen)

        # Projectiles drawn on top of enemies
        for proj in self.projectiles:
            proj.draw(self.screen)

        self._draw_placement_preview()

        wave_num    = self.wave_manager.wave_number       if self.wave_manager else 0
        total_waves = self.wave_manager.total_waves       if self.wave_manager else 0
        wm_state    = self.wave_manager.state             if self.wave_manager else WAITING_FOR_START
        countdown   = self.wave_manager.between_countdown if self.wave_manager else 0

        self.hud.draw(self.screen, self.money, self.lives,
                      self.tower_defs, self.selected_slot,
                      wave_num, total_waves, wm_state, countdown)

        if self.wave_manager:
            self.wave_manager.draw_overlay(self.screen, SCREEN_WIDTH, GAME_HEIGHT)

        if self.show_info:
            self.info_screen.draw(self.screen, self.tower_defs)

        self.upgrade_screen.draw(self.screen)

        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()

    # ------------------------------------------------------------------
    def _draw_grid(self):
        for row in range(ROWS):
            for col in range(COLS):
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE,
                                   TILE_SIZE, TILE_SIZE)
                if self.level_grid is not None and row < len(self.level_grid):
                    tile = self.level_grid[row][col] if col < len(self.level_grid[row]) else TILE_EMPTY
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

    def _draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))
        go  = self.font_gameover.render("GAME  OVER", True, RED)
        sub = self.font_go_sub.render("Press  ESC  to quit", True, LIGHT_GRAY)
        self.screen.blit(go,  (SCREEN_WIDTH//2 - go.get_width()//2,
                                SCREEN_HEIGHT//2 - go.get_height()//2 - 20))
        self.screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2,
                                SCREEN_HEIGHT//2 + go.get_height()//2 - 10))

    # ------------------------------------------------------------------
    def quit(self):
        pygame.quit()


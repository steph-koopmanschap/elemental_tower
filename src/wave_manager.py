"""
WaveManager — controls wave sequencing and enemy spawning.

Wave definition dict:
  duration    float   total wave duration in seconds (informational)
  count       int     number of enemies to spawn
  spawn_rate  float   seconds between each spawn
  enemy       dict    enemy template:
      hp, color, radius, speed, reward

States
------
  WAITING_FOR_START  — before the player clicks Start
  BETWEEN_WAVES      — countdown timer between waves
  SPAWNING           — actively spawning enemies this wave
  WAVE_IN_PROGRESS   — all enemies spawned, waiting for them to clear
  GAME_OVER          — player has lost
"""
import pygame
from src.enemy import Enemy
from src.settings import TIME_BETWEEN_WAVES, TILE_SIZE

# States
WAITING_FOR_START = "waiting_for_start"
BETWEEN_WAVES     = "between_waves"
SPAWNING          = "spawning"
WAVE_IN_PROGRESS  = "wave_in_progress"
GAME_OVER         = "game_over"

# Built-in wave definitions (can be overridden per-level later)
DEFAULT_WAVES = [
    {
        "duration": 20,
        "count": 8,
        "spawn_rate": 1.5,
        "enemy": {
            "hp": 30, "color": [180, 60, 60], "radius": 14,
            "speed": 60, "reward": 5
        }
    },
    {
        "duration": 25,
        "count": 12,
        "spawn_rate": 1.2,
        "enemy": {
            "hp": 50, "color": [200, 120, 30], "radius": 16,
            "speed": 70, "reward": 8
        }
    },
    {
        "duration": 30,
        "count": 15,
        "spawn_rate": 1.0,
        "enemy": {
            "hp": 80, "color": [80, 80, 220], "radius": 18,
            "speed": 80, "reward": 12
        }
    },
    {
        "duration": 35,
        "count": 20,
        "spawn_rate": 0.8,
        "enemy": {
            "hp": 120, "color": [60, 180, 60], "radius": 20,
            "speed": 90, "reward": 15
        }
    },
    {
        "duration": 40,
        "count": 25,
        "spawn_rate": 0.6,
        "enemy": {
            "hp": 200, "color": [160, 30, 200], "radius": 22,
            "speed": 100, "reward": 20
        }
    },
]


class WaveManager:
    def __init__(self, waypoints: list, waves: list = None):
        """
        waypoints: ordered list of (px_x, px_y) pixel centres along the path.
        waves:     list of wave dicts; defaults to DEFAULT_WAVES.
        """
        self.waypoints   = waypoints
        self.waves       = waves if waves else DEFAULT_WAVES

        self.state       = WAITING_FOR_START
        self.wave_index  = -1          # index of current / last wave (0-based)
        self.enemies     = []          # all live Enemy objects

        # Spawning state
        self._spawn_timer    = 0.0     # seconds until next spawn
        self._spawned_count  = 0       # enemies spawned this wave

        # Between-wave countdown
        self._between_timer  = 0.0

        self.font = pygame.font.SysFont("monospace", 48, bold=True)
        self.font_sub = pygame.font.SysFont("monospace", 22)

    # ------------------------------------------------------------------
    @property
    def wave_number(self):
        """1-based wave number for display."""
        return self.wave_index + 1

    @property
    def total_waves(self):
        return len(self.waves)

    @property
    def between_countdown(self):
        return max(0.0, self._between_timer)

    # ------------------------------------------------------------------
    def start_game(self):
        """Called when player clicks the Start button."""
        if self.state == WAITING_FOR_START:
            self._begin_wave(0)

    def _begin_wave(self, index: int):
        self.wave_index     = index
        self._spawned_count = 0
        self._spawn_timer   = 0.0
        self.state          = SPAWNING

    def _begin_between(self):
        self._between_timer = TIME_BETWEEN_WAVES
        self.state          = BETWEEN_WAVES

    # ------------------------------------------------------------------
    def update(self, dt: float) -> tuple[int, int]:
        """
        Advance wave logic and move all enemies.
        Returns (lives_lost, money_earned) this frame.
        """
        lives_lost    = 0
        money_earned  = 0

        if self.state == WAITING_FOR_START:
            return 0, 0

        if self.state == BETWEEN_WAVES:
            self._between_timer -= dt
            if self._between_timer <= 0:
                next_idx = self.wave_index + 1
                if next_idx >= len(self.waves):
                    # All waves done — keep state as-is (victory handling TBD)
                    self.state = WAVE_IN_PROGRESS
                else:
                    self._begin_wave(next_idx)
            return 0, 0

        # --- Spawning ---
        if self.state == SPAWNING:
            wave_def = self.waves[self.wave_index]
            self._spawn_timer -= dt
            if self._spawn_timer <= 0 and self._spawned_count < wave_def["count"]:
                self._spawn_enemy(wave_def["enemy"])
                self._spawned_count += 1
                self._spawn_timer = wave_def["spawn_rate"]
            if self._spawned_count >= wave_def["count"]:
                self.state = WAVE_IN_PROGRESS

        # --- Move enemies, tick DOT, collect outcomes ---
        # Projectile-kill rewards are handled in game.py.
        # DOT-kill rewards are also handled in game.py via dot_kills list.
        self.dot_kills = []   # enemies killed by DOT this frame
        alive = []
        for enemy in self.enemies:
            enemy.update(dt)

            if enemy.reached_end:
                lives_lost += 1
            elif enemy.dead:
                # Could have been killed by DOT — game.py checks and awards reward
                self.dot_kills.append(enemy)
            else:
                alive.append(enemy)

        self.enemies = alive

        # --- Check if wave is fully cleared ---
        if self.state == WAVE_IN_PROGRESS and not self.enemies:
            if self.wave_index + 1 < len(self.waves):
                self._begin_between()
            else:
                pass   # All waves complete — game won (handle in game.py)

        return lives_lost, money_earned

    def _spawn_enemy(self, edef: dict):
        e = Enemy(
            hp       = edef["hp"],
            color    = edef["color"],
            radius   = edef["radius"],
            speed    = edef["speed"],
            reward   = edef["reward"],
            waypoints= self.waypoints,
        )
        self.enemies.append(e)

    # ------------------------------------------------------------------
    def draw(self, surface):
        for enemy in self.enemies:
            enemy.draw(surface)

    def draw_overlay(self, surface, screen_w, screen_h):
        """Draw wave countdown / start prompt overlaid on the game."""
        if self.state == WAITING_FOR_START:
            self._draw_centered(surface, screen_w, screen_h,
                                "Click  START  to begin!",
                                sub=f"Wave 1 of {self.total_waves}")

        elif self.state == BETWEEN_WAVES:
            secs = int(self._between_timer) + 1
            self._draw_centered(surface, screen_w, screen_h,
                                f"Wave {self.wave_number + 1}  in  {secs}s",
                                sub=f"Wave {self.wave_number} cleared!")

    def _draw_centered(self, surface, sw, sh, text, sub=""):
        # Semi-transparent pill
        pad = 24
        main_s = self.font.render(text, True, (255, 240, 100))
        sub_s  = self.font_sub.render(sub, True, (200, 200, 200))
        w = max(main_s.get_width(), sub_s.get_width()) + pad * 2
        h = main_s.get_height() + sub_s.get_height() + pad
        rx = (sw - w) // 2
        ry = (sh // 2) - h // 2 - 30

        pill = pygame.Surface((w, h), pygame.SRCALPHA)
        pill.fill((0, 0, 0, 160))
        surface.blit(pill, (rx, ry))
        pygame.draw.rect(surface, (200, 200, 200), (rx, ry, w, h), 2, border_radius=10)

        surface.blit(main_s, (rx + pad, ry + 8))
        surface.blit(sub_s,  (rx + w // 2 - sub_s.get_width() // 2,
                               ry + main_s.get_height() + 10))


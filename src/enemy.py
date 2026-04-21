"""
Enemy — a circle that walks along the path waypoints.
"""
import pygame
from src.settings import DOT_TICK_INTERVAL, DOT_DURATION


class Enemy:
    def __init__(self, hp: int, color: tuple, radius: int,
                 speed: float, reward: int, waypoints: list):
        self.max_hp   = hp
        self.hp       = hp
        self.color    = tuple(color)
        self.radius   = radius
        self.speed    = speed
        self.reward   = reward

        self.waypoints    = waypoints
        self.waypoint_idx = 0
        self.reached_end  = False
        self.dead         = False

        # DOT state
        self._dot_damage        = 0      # HP per tick (0 = no active DOT)
        self._dot_duration_left = 0.0   # seconds remaining on DOT
        self._dot_tick_timer    = 0.0   # seconds until next tick

        # Start position
        if waypoints:
            self.x = float(waypoints[0][0])
            self.y = float(waypoints[0][1])
            self.waypoint_idx = 1
        else:
            self.x = 0.0
            self.y = 0.0

    # ------------------------------------------------------------------
    def apply_dot(self, damage_per_tick: int):
        """
        Apply or refresh a DOT effect. Does not stack — if a new DOT
        arrives while one is active, only keep the higher damage value,
        but always reset the duration.
        """
        self._dot_damage        = max(self._dot_damage, damage_per_tick)
        self._dot_duration_left = DOT_DURATION
        # Reset tick timer so next tick fires after a full interval
        self._dot_tick_timer    = DOT_TICK_INTERVAL

    @property
    def has_dot(self) -> bool:
        return self._dot_duration_left > 0 and self._dot_damage > 0

    # ------------------------------------------------------------------
    def update(self, dt: float) -> int:
        """
        Move and tick DOT.
        Returns the DOT damage dealt this frame (for money-on-kill tracking).
        """
        dot_dealt = 0

        if self.dead:
            return dot_dealt
        if self.reached_end or self.waypoint_idx >= len(self.waypoints):
            self.reached_end = True
            return dot_dealt

        # --- Movement ---
        tx, ty    = self.waypoints[self.waypoint_idx]
        dx, dy    = tx - self.x, ty - self.y
        dist      = (dx * dx + dy * dy) ** 0.5
        move_dist = self.speed * dt

        if move_dist >= dist:
            self.x, self.y = float(tx), float(ty)
            self.waypoint_idx += 1
            if self.waypoint_idx >= len(self.waypoints):
                self.reached_end = True
        else:
            self.x += dx / dist * move_dist
            self.y += dy / dist * move_dist

        # --- DOT (Damage Over Time) tick ---
        if self.has_dot:
            self._dot_duration_left -= dt
            self._dot_tick_timer    -= dt

            if self._dot_tick_timer <= 0:
                self._dot_tick_timer = DOT_TICK_INTERVAL
                self.take_damage(self._dot_damage)
                dot_dealt = self._dot_damage

            if self._dot_duration_left <= 0:
                self._dot_damage        = 0
                self._dot_duration_left = 0.0
                self._dot_tick_timer    = 0.0

        return dot_dealt

    def take_damage(self, amount: int):
        self.hp -= amount
        if self.hp <= 0:
            self.hp   = 0
            self.dead = True

    # ------------------------------------------------------------------
    def draw(self, surface):
        if self.dead:
            return

        ix, iy = int(self.x), int(self.y)

        # DOT glow ring (orange/red pulsing ring behind body)
        if self.has_dot:
            pygame.draw.circle(surface, (220, 80, 0), (ix, iy), self.radius + 4)

        # Shadow
        pygame.draw.circle(surface, (20, 20, 20), (ix + 2, iy + 2), self.radius)
        # Body
        pygame.draw.circle(surface, self.color, (ix, iy), self.radius)
        # Outline
        pygame.draw.circle(surface, (0, 0, 0), (ix, iy), self.radius, 2)

        # HP bar
        bar_w = self.radius * 2
        bar_h = 5
        bar_x = ix - self.radius
        bar_y = iy - self.radius - 9
        pygame.draw.rect(surface, (80, 0, 0),   (bar_x, bar_y, bar_w, bar_h))
        fill_w = int(bar_w * self.hp / self.max_hp)
        if fill_w > 0:
            pygame.draw.rect(surface, (0, 220, 0), (bar_x, bar_y, fill_w, bar_h))

        # DOT timer bar (orange, below HP bar)
        if self.has_dot:
            dot_frac = self._dot_duration_left / DOT_DURATION
            dot_fill = int(bar_w * dot_frac)
            pygame.draw.rect(surface, (60, 30, 0),   (bar_x, bar_y - 6, bar_w, 4))
            if dot_fill > 0:
                pygame.draw.rect(surface, (230, 120, 0), (bar_x, bar_y - 6, dot_fill, 4))


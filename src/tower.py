import math
import pygame
from src.settings import *
from src.projectile import Projectile


class Tower:
    """A placed tower on the map — detects enemies in range and fires projectiles."""

    def __init__(self, definition, grid_col, grid_row):
        self.id          = definition["id"]
        self.name        = definition["name"]
        self.cost        = definition["cost"]
        self.damage      = definition["damage"]
        self.firing_rate = definition["firing_rate"]   # shots per second
        self.range       = definition["range"]          # in tiles
        self.color       = tuple(definition["color"])
        self.col         = grid_col
        self.row         = grid_row

        # Shoot cooldown: seconds remaining until next shot allowed
        self._cooldown = 0.0

    # ------------------------------------------------------------------
    @property
    def rect(self):
        return pygame.Rect(self.col * TILE_SIZE, self.row * TILE_SIZE,
                           TILE_SIZE, TILE_SIZE)

    @property
    def centre(self):
        """Pixel centre of this tower."""
        return (self.col * TILE_SIZE + TILE_SIZE // 2,
                self.row * TILE_SIZE + TILE_SIZE // 2)

    @property
    def range_px(self):
        """Attack range in pixels."""
        return self.range * TILE_SIZE

    # ------------------------------------------------------------------
    def update(self, dt: float, enemies: list) -> list:
        """
        Advance cooldown and fire at the first in-range enemy.
        Returns a list of new Projectile objects spawned this frame.
        """
        new_projectiles = []

        if self.firing_rate <= 0:
            return new_projectiles

        self._cooldown -= dt
        if self._cooldown > 0:
            return new_projectiles

        # Find the enemy that has progressed furthest along the path
        # (highest waypoint index, then closest to next waypoint)
        target = self._pick_target(enemies)
        if target is None:
            return new_projectiles

        # Fire!
        cx, cy = self.centre
        new_projectiles.append(
            Projectile(float(cx), float(cy), target, self.damage, self.color)
        )
        self._cooldown = 1.0 / self.firing_rate   # reset cooldown

        return new_projectiles

    def _pick_target(self, enemies):
        """Return the furthest-progressed enemy within range, or None."""
        cx, cy = self.centre
        best   = None

        for enemy in enemies:
            if enemy.dead or enemy.reached_end:
                continue
            dist = math.hypot(enemy.x - cx, enemy.y - cy)
            if dist > self.range_px:
                continue
            # Prefer enemy with highest waypoint index (furthest along path)
            if best is None:
                best = enemy
            elif enemy.waypoint_idx > best.waypoint_idx:
                best = enemy

        return best

    # ------------------------------------------------------------------
    def draw(self, surface):
        r = self.rect

        # Filled base
        pygame.draw.rect(surface, self.color, r)
        pygame.draw.rect(surface, BLACK, r, 2)

        # Inner darker square (tower "body")
        inner  = r.inflate(-18, -18)
        darker = tuple(max(0, c - 50) for c in self.color)
        pygame.draw.rect(surface, darker, inner)

        # Small circle "cannon barrel" hint at centre
        cx, cy = self.centre
        pygame.draw.circle(surface, BLACK, (cx, cy), 5)
        pygame.draw.circle(surface, self.color, (cx, cy), 4)


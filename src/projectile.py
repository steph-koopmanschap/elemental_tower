"""
Projectile — fired by a tower, travels toward a target enemy.
"""
import math
import pygame
from src.settings import PROJECTILE_SPEED, PROJECTILE_RADIUS


class Projectile:
    def __init__(self, x: float, y: float, target, damage: int, color: tuple):
        """
        x, y    : pixel origin (tower centre)
        target  : Enemy instance to home toward
        damage  : HP to remove on hit
        color   : RGB tuple — matches the firing tower
        """
        self.x      = x
        self.y      = y
        self.target = target
        self.damage = damage
        self.color  = color
        self.hit    = False     # True once it has struck its target
        self.missed = False     # True if target died before impact

    # ------------------------------------------------------------------
    def update(self, dt: float):
        if self.hit or self.missed:
            return

        # If the target died before we arrived, discard the projectile
        if self.target.dead or self.target.reached_end:
            self.missed = True
            return

        tx, ty = self.target.x, self.target.y
        dx, dy = tx - self.x, ty - self.y
        dist   = math.hypot(dx, dy)
        move   = PROJECTILE_SPEED * dt

        if move >= dist:
            # Close enough — register hit
            self.x, self.y = tx, ty
            self.target.take_damage(self.damage)
            self.hit = True
        else:
            self.x += dx / dist * move
            self.y += dy / dist * move

    # ------------------------------------------------------------------
    def draw(self, surface):
        if self.hit or self.missed:
            return
        # Bright filled circle with a dark outline for contrast
        ix, iy = int(self.x), int(self.y)
        pygame.draw.circle(surface, (0, 0, 0),  (ix, iy), PROJECTILE_RADIUS + 1)
        pygame.draw.circle(surface, self.color, (ix, iy), PROJECTILE_RADIUS)

    # ------------------------------------------------------------------
    @property
    def expired(self):
        return self.hit or self.missed


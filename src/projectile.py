"""
Projectile — fired by a tower, travels toward a target enemy.
"""
import math
import pygame
from src.settings import PROJECTILE_SPEED, PROJECTILE_RADIUS


class Projectile:
    def __init__(self, x: float, y: float, target, damage: int, color: tuple,
                 is_crit: bool = False, dot_damage: int = 0):
        self.x          = x
        self.y          = y
        self.target     = target
        self.damage     = damage
        self.color      = color
        self.is_crit    = is_crit    # whether this shot was a critical hit
        self.dot_damage = dot_damage # HP per DOT tick (0 = no DOT)
        self.hit        = False
        self.missed     = False

    # ------------------------------------------------------------------
    def update(self, dt: float):
        if self.hit or self.missed:
            return

        if self.target.dead or self.target.reached_end:
            self.missed = True
            return

        tx, ty = self.target.x, self.target.y
        dx, dy = tx - self.x, ty - self.y
        dist   = math.hypot(dx, dy)
        move   = PROJECTILE_SPEED * dt

        if move >= dist:
            self.x, self.y = tx, ty
            # Apply direct damage
            self.target.take_damage(self.damage)
            # Apply DOT if any (does not stack — only refresh if new damage is higher)
            if self.dot_damage > 0 and not self.target.dead:
                self.target.apply_dot(self.dot_damage)
            self.hit = True
        else:
            self.x += dx / dist * move
            self.y += dy / dist * move

    # ------------------------------------------------------------------
    def draw(self, surface):
        if self.hit or self.missed:
            return
        ix, iy = int(self.x), int(self.y)
        # Crits get a larger, glowing outline
        if self.is_crit:
            pygame.draw.circle(surface, (255, 255, 100), (ix, iy), PROJECTILE_RADIUS + 3)
            pygame.draw.circle(surface, (255, 200, 0),   (ix, iy), PROJECTILE_RADIUS + 1)
        else:
            pygame.draw.circle(surface, (0, 0, 0), (ix, iy), PROJECTILE_RADIUS + 1)
        pygame.draw.circle(surface, self.color, (ix, iy), PROJECTILE_RADIUS)

    # ------------------------------------------------------------------
    @property
    def expired(self):
        return self.hit or self.missed

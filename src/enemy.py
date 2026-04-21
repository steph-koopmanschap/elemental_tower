"""
Enemy — a circle that walks along the path waypoints.

Properties (from wave definition):
  hp            int    hit points
  color         tuple  RGB
  radius        int    pixel radius
  speed         float  pixels per second
  reward        int    money given on death
"""
import pygame


class Enemy:
    def __init__(self, hp: int, color: tuple, radius: int,
                 speed: float, reward: int, waypoints: list):
        """
        waypoints: list of (px_x, px_y) pixel centres to walk through, in order.
        """
        self.max_hp   = hp
        self.hp       = hp
        self.color    = tuple(color)
        self.radius   = radius
        self.speed    = speed          # pixels / second
        self.reward   = reward

        self.waypoints     = waypoints
        self.waypoint_idx  = 0         # index of the NEXT waypoint to head toward
        self.reached_end   = False
        self.dead          = False

        # Start position = first waypoint
        if waypoints:
            self.x = float(waypoints[0][0])
            self.y = float(waypoints[0][1])
            self.waypoint_idx = 1
        else:
            self.x = 0.0
            self.y = 0.0

    # ------------------------------------------------------------------
    def update(self, dt: float):
        """Move toward next waypoint. dt = seconds since last frame."""
        if self.reached_end or self.dead or self.waypoint_idx >= len(self.waypoints):
            self.reached_end = True
            return

        tx, ty     = self.waypoints[self.waypoint_idx]
        dx, dy     = tx - self.x, ty - self.y
        dist       = (dx * dx + dy * dy) ** 0.5
        move_dist  = self.speed * dt

        if move_dist >= dist:
            # Snap to waypoint and advance
            self.x, self.y = float(tx), float(ty)
            self.waypoint_idx += 1
            if self.waypoint_idx >= len(self.waypoints):
                self.reached_end = True
        else:
            self.x += dx / dist * move_dist
            self.y += dy / dist * move_dist

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

        # Shadow
        pygame.draw.circle(surface, (20, 20, 20), (ix + 2, iy + 2), self.radius)

        # Body
        pygame.draw.circle(surface, self.color, (ix, iy), self.radius)

        # Outline
        pygame.draw.circle(surface, (0, 0, 0), (ix, iy), self.radius, 2)

        # HP bar — drawn above the enemy
        bar_w  = self.radius * 2
        bar_h  = 5
        bar_x  = ix - self.radius
        bar_y  = iy - self.radius - 9
        # Background
        pygame.draw.rect(surface, (80, 0, 0),
                         (bar_x, bar_y, bar_w, bar_h))
        # Fill
        fill_w = int(bar_w * self.hp / self.max_hp)
        if fill_w > 0:
            pygame.draw.rect(surface, (0, 220, 0),
                             (bar_x, bar_y, fill_w, bar_h))


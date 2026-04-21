import pygame
from src.settings import *


class Tower:
    """A placed tower on the map."""

    def __init__(self, definition, grid_col, grid_row):
        self.id          = definition["id"]
        self.name        = definition["name"]
        self.cost        = definition["cost"]
        self.damage      = definition["damage"]
        self.firing_rate = definition["firing_rate"]
        self.range       = definition["range"]
        self.color       = tuple(definition["color"])   # JSON gives a list; pygame needs a tuple
        self.col         = grid_col
        self.row         = grid_row

    @property
    def rect(self):
        x = self.col * TILE_SIZE
        y = self.row * TILE_SIZE
        return pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

    def draw(self, surface):
        r = self.rect
        pygame.draw.rect(surface, self.color, r)
        pygame.draw.rect(surface, BLACK, r, 2)
        inner = r.inflate(-20, -20)
        darker = tuple(max(0, c - 40) for c in self.color)
        pygame.draw.rect(surface, darker, inner)

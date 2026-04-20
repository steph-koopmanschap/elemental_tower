import pygame
from src.settings import *


def _draw_heart(surface, cx, cy, size, color):
    r = size // 4
    pygame.draw.circle(surface, color, (cx - r, cy - r // 2), r)
    pygame.draw.circle(surface, color, (cx + r, cy - r // 2), r)
    points = [
        (cx - size // 2, cy - r // 2),
        (cx,             cy + size // 2),
        (cx + size // 2, cy - r // 2),
    ]
    pygame.draw.polygon(surface, color, points)


class InfoScreen:
    """Full-screen overlay listing all towers and their properties."""

    PANEL_W = 860
    PANEL_H = 560
    ROW_H   = 48
    SWATCH  = 36
    PAD     = 24

    def __init__(self):
        self.font_title  = pygame.font.SysFont("monospace", 28, bold=True)
        self.font_header = pygame.font.SysFont("monospace", 14, bold=True)
        self.font_body   = pygame.font.SysFont("monospace", 13)
        self.font_hint   = pygame.font.SysFont("monospace", 13)

    def draw(self, surface, tower_defs):
        # Dim the background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Panel
        px = (SCREEN_WIDTH  - self.PANEL_W) // 2
        py = (SCREEN_HEIGHT - self.PANEL_H) // 2
        panel = pygame.Rect(px, py, self.PANEL_W, self.PANEL_H)
        pygame.draw.rect(surface, (28, 28, 36), panel, border_radius=12)
        pygame.draw.rect(surface, LIGHT_GRAY,   panel, 2, border_radius=12)

        # Title
        title_surf = self.font_title.render("TOWER ENCYCLOPEDIA", True, WHITE)
        surface.blit(title_surf, (px + self.PANEL_W // 2 - title_surf.get_width() // 2, py + 16))

        # Column headers
        hx = px + self.PAD
        hy = py + 60
        cols = [
            (0,   "TOWER",       WHITE),
            (200, "COST",        GOLD),
            (290, "DAMAGE",      RED),
            (390, "DESCRIPTION", LIGHT_GRAY),
        ]
        for offset, label, color in cols:
            s = self.font_header.render(label, True, color)
            surface.blit(s, (hx + offset, hy))

        # Divider
        pygame.draw.line(surface, GRAY,
                         (px + self.PAD, hy + 20),
                         (px + self.PANEL_W - self.PAD, hy + 20), 1)

        # Rows
        row_y = hy + 30
        for tdef in tower_defs:
            if row_y + self.ROW_H > py + self.PANEL_H - 40:
                break

            unlocked = tdef["unlocked"]
            row_color = WHITE if unlocked else GRAY

            # Colour swatch
            swatch_rect = pygame.Rect(hx, row_y + (self.ROW_H - self.SWATCH) // 2,
                                      self.SWATCH, self.SWATCH)
            pygame.draw.rect(surface, tdef["color"] if unlocked else (50, 50, 50),
                             swatch_rect, border_radius=4)
            if not unlocked:
                q = self.font_title.render("?", True, GRAY)
                surface.blit(q, (swatch_rect.centerx - q.get_width() // 2,
                                 swatch_rect.centery - q.get_height() // 2))

            # Name
            name = tdef["name"] if unlocked else "???"
            ns = self.font_body.render(name, True, row_color)
            surface.blit(ns, (hx + self.SWATCH + 8, row_y + (self.ROW_H - ns.get_height()) // 2))

            if unlocked:
                # Cost
                cs = self.font_body.render(f"${tdef['cost']}", True, GOLD)
                surface.blit(cs, (hx + 200, row_y + (self.ROW_H - cs.get_height()) // 2))

                # Damage — sword icon + number
                dmg_x = hx + 290
                dmg_y = row_y + self.ROW_H // 2
                _draw_heart(surface, dmg_x + 8, dmg_y, 16, RED)
                ds = self.font_body.render(str(tdef["damage"]), True, RED)
                surface.blit(ds, (dmg_x + 20, dmg_y - ds.get_height() // 2))

                # Description (truncate if too long)
                desc = tdef["description"]
                if len(desc) > 52:
                    desc = desc[:49] + "..."
                desc_s = self.font_body.render(desc, True, LIGHT_GRAY)
                surface.blit(desc_s, (hx + 390, row_y + (self.ROW_H - desc_s.get_height()) // 2))

            # Row separator
            pygame.draw.line(surface, (55, 55, 65),
                             (px + self.PAD, row_y + self.ROW_H - 1),
                             (px + self.PANEL_W - self.PAD, row_y + self.ROW_H - 1), 1)

            row_y += self.ROW_H

        # Close hint
        hint = self.font_hint.render("Press  I  to close", True, GRAY)
        surface.blit(hint, (px + self.PANEL_W // 2 - hint.get_width() // 2,
                            py + self.PANEL_H - 28))

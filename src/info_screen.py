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

    PANEL_W = 1220
    PANEL_H = 600
    ROW_H   = 46
    SWATCH  = 32
    PAD     = 24

    # Layout: TOWER(0) COST(200) DMG(275) RATE(350) RANGE(430) CRIT(505) DOT(575) DESC(650)
    COLUMNS = [
        (0,   "TOWER",       WHITE),
        (200, "COST",        GOLD),
        (275, "DMG",         RED),
        (350, "RATE",        (160, 220, 255)),
        (430, "RANGE",       GREEN),
        (505, "CRIT",        (255, 220, 60)),
        (575, "DOT",         (230, 120, 0)),
        (650, "DESCRIPTION", LIGHT_GRAY),
    ]

    def __init__(self):
        self.font_title  = pygame.font.SysFont("monospace", 24, bold=True)
        self.font_header = pygame.font.SysFont("monospace", 13, bold=True)
        self.font_body   = pygame.font.SysFont("monospace", 13)
        self.font_hint   = pygame.font.SysFont("monospace", 13)

    # ------------------------------------------------------------------
    def draw(self, surface, tower_defs):
        # Dim background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        surface.blit(overlay, (0, 0))

        # Panel
        px = (SCREEN_WIDTH  - self.PANEL_W) // 2
        py = (SCREEN_HEIGHT - self.PANEL_H) // 2
        panel = pygame.Rect(px, py, self.PANEL_W, self.PANEL_H)
        pygame.draw.rect(surface, (22, 22, 30), panel, border_radius=12)
        pygame.draw.rect(surface, LIGHT_GRAY,   panel, 2,  border_radius=12)

        # Title
        title_s = self.font_title.render("TOWER  ENCYCLOPEDIA", True, WHITE)
        surface.blit(title_s, (px + self.PANEL_W // 2 - title_s.get_width() // 2, py + 14))

        # Column headers
        hx = px + self.PAD
        hy = py + 52

        for offset, label, color in self.COLUMNS:
            s = self.font_header.render(label, True, color)
            surface.blit(s, (hx + offset, hy))

        pygame.draw.line(surface, GRAY,
                         (px + self.PAD, hy + 20),
                         (px + self.PANEL_W - self.PAD, hy + 20), 1)

        # Rows
        row_y = hy + 28
        for tdef in tower_defs:
            if row_y + self.ROW_H > py + self.PANEL_H - 34:
                break

            unlocked  = tdef["unlocked"]
            row_color = WHITE if unlocked else GRAY
            swatch_color = tuple(tdef["color"]) if unlocked else (50, 50, 50)
            mid_y = row_y + self.ROW_H // 2

            # --- Colour swatch ---
            sw = pygame.Rect(hx, row_y + (self.ROW_H - self.SWATCH) // 2,
                             self.SWATCH, self.SWATCH)
            pygame.draw.rect(surface, swatch_color, sw, border_radius=4)
            if not unlocked:
                q = self.font_title.render("?", True, GRAY)
                surface.blit(q, (sw.centerx - q.get_width() // 2,
                                 sw.centery - q.get_height() // 2))

            # --- Name ---
            name_s = self.font_body.render(
                tdef["name"] if unlocked else "???", True, row_color)
            surface.blit(name_s, (hx + self.SWATCH + 6,
                                  mid_y - name_s.get_height() // 2))

            if unlocked:
                # --- Cost ---
                cs = self.font_body.render(f"${tdef['cost']}", True, GOLD)
                surface.blit(cs, (hx + 220, mid_y - cs.get_height() // 2))

                # --- Damage (small heart + number) ---
                _draw_heart(surface, hx + 300 + 7, mid_y, 13, RED)
                ds = self.font_body.render(str(tdef["damage"]), True, RED)
                surface.blit(ds, (hx + 300 + 18, mid_y - ds.get_height() // 2))

                # --- Firing rate ---
                fr_s = self.font_body.render(f"{tdef['firing_rate']}/s", True, (160, 220, 255))
                surface.blit(fr_s, (hx + 390, mid_y - fr_s.get_height() // 2))

                # --- Range ---
                rng_s = self.font_body.render(f"{tdef['range']} tiles", True, GREEN)
                surface.blit(rng_s, (hx + 430, mid_y - rng_s.get_height() // 2))

                # --- Crit chance ---
                crit_pct = int(tdef.get('crit_chance', 0) * 100)
                crit_s = self.font_body.render(f"{crit_pct}%", True, (255, 220, 60))
                surface.blit(crit_s, (hx + 505, mid_y - crit_s.get_height() // 2))

                # --- DOT damage ---
                dot_val  = tdef.get('dot_damage', 0)
                dot_text = f"{dot_val}/tick" if dot_val > 0 else "—"
                dot_col  = (230, 120, 0) if dot_val > 0 else GRAY
                dot_s = self.font_body.render(dot_text, True, dot_col)
                surface.blit(dot_s, (hx + 575, mid_y - dot_s.get_height() // 2))

                # --- Description ---
                desc = tdef["description"]
                if len(desc) > 44:
                    desc = desc[:41] + "..."
                desc_s = self.font_body.render(desc, True, LIGHT_GRAY)
                surface.blit(desc_s, (hx + 580, mid_y - desc_s.get_height() // 2))

            # Row separator
            pygame.draw.line(surface, (48, 48, 60),
                             (px + self.PAD, row_y + self.ROW_H - 1),
                             (px + self.PANEL_W - self.PAD, row_y + self.ROW_H - 1), 1)

            row_y += self.ROW_H

        # Close hint
        hint = self.font_hint.render("Press  I  to close", True, GRAY)
        surface.blit(hint, (px + self.PANEL_W // 2 - hint.get_width() // 2,
                            py + self.PANEL_H - 22))


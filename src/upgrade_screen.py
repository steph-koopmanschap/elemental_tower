"""
UpgradeScreen — shown when the player clicks a placed tower.

Layout
------
  Centre slot  : tower level + name. Clickable to level up the tower
                 (only when all elements are at tower_level + 1).
  5 outer slots: one per element, clockwise from top.
                 Shows element name, current level, upgrade cost.
                 Greyed + locked icon when upgrade is not allowed.

Upgrade rules
-------------
  - Elements can be upgraded up to (tower_level + 1).
  - Tower level-up is only available when ALL elements == tower_level + 1.
  - Each upgrade deducts money from the game.
"""
import math
import pygame
from src.settings import *


# Geometry
_PANEL_R   = 165   # centre-to-outer-slot-centre distance
_SLOT_R    = 46    # outer slot circle radius
_CENTRE_R  = 56    # centre circle radius
_PAD       = _PANEL_R + _SLOT_R + 24   # bounding half-size for clamping

# Upgrade effect labels per element
_EFFECT_LABEL = {
    "earth":  f"+{UPGRADE_DAMAGE_PER_LEVEL} DMG",
    "fire":   "(coming soon)",
    "water":  f"+{UPGRADE_FIRE_RATE_PER_LEVEL}/s",
    "wind":   f"+{UPGRADE_RANGE_PER_LEVEL} RNG",
    "spirit": "(coming soon)",
}

# Which elements are implemented
_IMPLEMENTED = {"earth", "water", "wind", "fire", "spirit"}


class UpgradeScreen:

    def __init__(self):
        self.font_name   = pygame.font.SysFont("monospace", 13, bold=True)
        self.font_body   = pygame.font.SysFont("monospace", 12)
        self.font_small  = pygame.font.SysFont("monospace", 11)
        self.font_lvl    = pygame.font.SysFont("monospace", 18, bold=True)
        self.font_hint   = pygame.font.SysFont("monospace", 11)

        self.tower   = None
        self.visible = False
        self._get_money   = lambda: 0        # injected by game.py
        self._spend_money = lambda n: None   # injected by game.py

        # 5 slots clockwise from top
        self._angles = [-90 + i * (360 / 5) for i in range(5)]

    # ------------------------------------------------------------------
    def show(self, tower, get_money_fn, spend_money_fn):
        self.tower        = tower
        self._get_money   = get_money_fn
        self._spend_money = spend_money_fn
        self.visible      = True

    def hide(self):
        self.tower   = None
        self.visible = False

    # ------------------------------------------------------------------
    def _panel_centre(self):
        if self.tower is None:
            return SCREEN_WIDTH // 2, GAME_HEIGHT // 2
        tx = self.tower.col * TILE_SIZE + TILE_SIZE // 2
        ty = self.tower.row * TILE_SIZE + TILE_SIZE // 2
        cx = max(_PAD, min(SCREEN_WIDTH  - _PAD, tx))
        cy = max(_PAD, min(GAME_HEIGHT   - _PAD, ty))
        return cx, cy

    def _slot_pos(self, angle_deg):
        cx, cy = self._panel_centre()
        rad = math.radians(angle_deg)
        return (int(cx + _PANEL_R * math.cos(rad)),
                int(cy + _PANEL_R * math.sin(rad)))

    # ------------------------------------------------------------------
    def handle_click(self, pos) -> bool:
        if not self.visible:
            return False

        cx, cy = self._panel_centre()

        # Centre slot — tower level-up
        if math.hypot(pos[0] - cx, pos[1] - cy) <= _CENTRE_R:
            self._try_levelup_tower()
            return True

        # Outer element slots
        for i, angle in enumerate(self._angles):
            sx, sy = self._slot_pos(angle)
            if math.hypot(pos[0] - sx, pos[1] - sy) <= _SLOT_R:
                self._try_upgrade_element(ELEMENT_NAMES[i])
                return True

        # Outside — close
        self.hide()
        return True

    # ------------------------------------------------------------------
    def _try_upgrade_element(self, element: str):
        t = self.tower
        allowed, _ = t.can_upgrade_element(element)
        if not allowed:
            return
        if element not in _IMPLEMENTED:
            return
        cost = t.upgrade_cost_element(element)
        if self._get_money() < cost:
            return
        self._spend_money(cost)
        t.upgrade_element(element)

    def _try_levelup_tower(self):
        t = self.tower
        allowed, _ = t.can_upgrade_tower()
        if not allowed:
            return
        cost = t.upgrade_cost_tower()
        if self._get_money() < cost:
            return
        self._spend_money(cost)
        t.upgrade_tower()

    # ------------------------------------------------------------------
    def draw(self, surface):
        if not self.visible or self.tower is None:
            return

        cx, cy = self._panel_centre()
        t = self.tower

        # ---- dim background circle ----
        dim_r = _PANEL_R + _SLOT_R + 14
        dim = pygame.Surface((dim_r * 2, dim_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(dim, (0, 0, 0, 155), (dim_r, dim_r), dim_r)
        surface.blit(dim, (cx - dim_r, cy - dim_r))

        # ---- spokes ----
        for angle in self._angles:
            sx, sy = self._slot_pos(angle)
            pygame.draw.line(surface, (80, 80, 80), (cx, cy), (sx, sy), 2)

        # ---- outer element slots ----
        for i, angle in enumerate(self._angles):
            sx, sy   = self._slot_pos(angle)
            element  = ELEMENT_NAMES[i]
            base_col = ELEMENT_COLORS[element]
            elem_lvl = t.element_levels[element]
            allowed, block_reason = t.can_upgrade_element(element)
            implemented = element in _IMPLEMENTED
            cost        = t.upgrade_cost_element(element)
            can_afford  = self._get_money() >= cost
            clickable   = allowed and implemented and can_afford

            # Dim colour if locked or not implemented
            if not allowed or not implemented:
                draw_col = tuple(max(0, c - 80) for c in base_col)
                border   = (90, 90, 90)
            elif not can_afford:
                draw_col = tuple(int(c * 0.7) for c in base_col)
                border   = (160, 80, 80)
            else:
                draw_col = base_col
                border   = WHITE

            # Shadow + fill + border
            pygame.draw.circle(surface, (10, 10, 10), (sx + 3, sy + 3), _SLOT_R)
            pygame.draw.circle(surface, draw_col, (sx, sy), _SLOT_R)
            pygame.draw.circle(surface, border,   (sx, sy), _SLOT_R, 2)

            # Element name
            name_s = self.font_name.render(element.upper(), True, WHITE)
            surface.blit(name_s, (sx - name_s.get_width() // 2, sy - 28))

            # Level badge
            lv_s = self.font_lvl.render(f"Lv{elem_lvl}", True, GOLD)
            surface.blit(lv_s, (sx - lv_s.get_width() // 2, sy - 7))

            # Effect label
            eff_s = self.font_small.render(_EFFECT_LABEL[element], True, LIGHT_GRAY)
            surface.blit(eff_s, (sx - eff_s.get_width() // 2, sy + 12))

            # Cost or lock reason
            if not allowed:
                lock_s = self.font_small.render("LOCKED", True, (180, 80, 80))
                surface.blit(lock_s, (sx - lock_s.get_width() // 2, sy + 26))
            elif not implemented:
                lock_s = self.font_small.render("SOON", True, (150, 150, 150))
                surface.blit(lock_s, (sx - lock_s.get_width() // 2, sy + 26))
            else:
                cost_col = (220, 80, 80) if not can_afford else GOLD
                cost_s   = self.font_small.render(f"${cost}", True, cost_col)
                surface.blit(cost_s, (sx - cost_s.get_width() // 2, sy + 26))

        # ---- centre tower slot ----
        tower_allowed, tower_reason = t.can_upgrade_tower()
        tower_cost = t.upgrade_cost_tower()
        can_afford_tower = self._get_money() >= tower_cost

        if tower_allowed and can_afford_tower:
            centre_border = GOLD
            centre_col    = tuple(min(255, c + 30) for c in t.color)
        elif tower_allowed:
            centre_border = (160, 80, 80)
            centre_col    = t.color
        else:
            centre_border = GOLD
            centre_col    = t.color

        pygame.draw.circle(surface, (10, 10, 10), (cx + 3, cy + 3), _CENTRE_R)
        pygame.draw.circle(surface, centre_col,   (cx, cy), _CENTRE_R)
        pygame.draw.circle(surface, centre_border, (cx, cy), _CENTRE_R, 3)

        # Tower name
        words = t.name.split()
        mid   = math.ceil(len(words) / 2)
        lines = [" ".join(words[:mid]), " ".join(words[mid:])] if len(words) > 1 else [t.name]
        for j, line in enumerate(lines):
            ls = self.font_name.render(line, True, WHITE)
            y_off = -22 + j * 15
            surface.blit(ls, (cx - ls.get_width() // 2, cy + y_off))

        # Tower level — large, prominent
        tl_s = self.font_lvl.render(f"Lv {t.tower_level}", True, GOLD)
        surface.blit(tl_s, (cx - tl_s.get_width() // 2, cy + 2))

        # Level-up prompt or requirement
        if tower_allowed:
            cost_col = (220, 80, 80) if not can_afford_tower else (100, 255, 100)
            prompt   = f"▲ ${tower_cost}"
            ps = self.font_small.render(prompt, True, cost_col)
            surface.blit(ps, (cx - ps.get_width() // 2, cy + 22))
        else:
            req_s = self.font_small.render(tower_reason, True, (160, 160, 160))
            surface.blit(req_s, (cx - req_s.get_width() // 2, cy + 22))

        # Stats lines (two rows to fit all)
        line1 = f"DMG {t.damage}  RNG {t.range}  {t.firing_rate}/s"
        line2 = f"CRIT {int(t.crit_chance*100)}%  DOT {t.dot_damage}/tick"
        st1 = self.font_hint.render(line1, True, LIGHT_GRAY)
        st2 = self.font_hint.render(line2, True, LIGHT_GRAY)
        surface.blit(st1, (cx - st1.get_width() // 2, cy + _CENTRE_R + 6))
        surface.blit(st2, (cx - st2.get_width() // 2, cy + _CENTRE_R + 18))

        # ---- bottom hint ----
        hint = self.font_hint.render(
            "Click element to upgrade  •  click tower to level up  •  click outside to close",
            True, GRAY)
        hx = cx - hint.get_width() // 2
        hy = cy + _PANEL_R + _SLOT_R + 8
        hx = max(4, min(SCREEN_WIDTH - hint.get_width() - 4, hx))
        hy = min(GAME_HEIGHT - hint.get_height() - 4, hy)
        surface.blit(hint, (hx, hy))


import pygame
from src.settings import *


def _draw_heart(surface, cx, cy, size, color):
    """Draw a filled heart centred at (cx, cy) with given size."""
    r = size // 4
    pygame.draw.circle(surface, color, (cx - r, cy - r // 2), r)
    pygame.draw.circle(surface, color, (cx + r, cy - r // 2), r)
    points = [
        (cx - size // 2, cy - r // 2),
        (cx,             cy + size // 2),
        (cx + size // 2, cy - r // 2),
    ]
    pygame.draw.polygon(surface, color, points)


class HUD:
    """Renders the bottom UI bar: stats + tower slots."""

    def __init__(self):
        self.font_large  = pygame.font.SysFont("monospace", 22, bold=True)
        self.font_medium = pygame.font.SysFont("monospace", 16, bold=True)
        self.font_small  = pygame.font.SysFont("monospace", 13)

        total_slots_width = TOWER_SLOTS * SLOT_SIZE + (TOWER_SLOTS - 1) * SLOT_PADDING
        start_x = (SCREEN_WIDTH - total_slots_width) // 2
        bar_top = GAME_HEIGHT

        self.slot_rects = []
        for i in range(TOWER_SLOTS):
            x = start_x + i * (SLOT_SIZE + SLOT_PADDING)
            y = bar_top + (UI_BAR_HEIGHT - SLOT_SIZE) // 2
            self.slot_rects.append(pygame.Rect(x, y, SLOT_SIZE, SLOT_SIZE))

    def draw(self, surface, money, lives, tower_defs, selected_index):
        self._draw_bar_background(surface)
        self._draw_stats(surface, money, lives)
        self._draw_slots(surface, tower_defs, selected_index)

    def _draw_bar_background(self, surface):
        bar_rect = pygame.Rect(0, GAME_HEIGHT, SCREEN_WIDTH, UI_BAR_HEIGHT)
        pygame.draw.rect(surface, MID_GRAY, bar_rect)
        pygame.draw.line(surface, GRAY, (0, GAME_HEIGHT), (SCREEN_WIDTH, GAME_HEIGHT), 2)

    def _draw_stats(self, surface, money, lives):
        x, y = 14, GAME_HEIGHT + 14

        # --- Money ---
        money_label = self.font_medium.render("MONEY", True, LIGHT_GRAY)
        money_value = self.font_large.render(f"${money}", True, GOLD)
        surface.blit(money_label, (x, y))
        surface.blit(money_value, (x, y + 22))

        # --- Lives: heart icon + red number ---
        lives_label = self.font_medium.render("LIVES", True, LIGHT_GRAY)
        surface.blit(lives_label, (x, y + 58))

        heart_cx = x + 12
        heart_cy = y + 84
        _draw_heart(surface, heart_cx, heart_cy, 20, RED)

        lives_surf = self.font_large.render(str(lives), True, RED)
        surface.blit(lives_surf, (heart_cx + 16, heart_cy - lives_surf.get_height() // 2))

        # --- Hint ---
        hint = self.font_small.render("[I] info   ESC quit", True, GRAY)
        surface.blit(hint, (SCREEN_WIDTH - 160, GAME_HEIGHT + 10))

    def _draw_slots(self, surface, tower_defs, selected_index):
        for i, (rect, tdef) in enumerate(zip(self.slot_rects, tower_defs)):
            unlocked   = tdef["unlocked"]
            is_selected = (i == selected_index)

            bg_color = DARK_GRAY if unlocked else (30, 30, 30)
            pygame.draw.rect(surface, bg_color, rect, border_radius=6)

            if unlocked:
                swatch = rect.inflate(-16, -16)
                swatch.height = swatch.height // 2
                pygame.draw.rect(surface, tuple(tdef["color"]), swatch, border_radius=4)

                short = tdef["name"].split()[0]
                name_surf = self.font_small.render(short, True, WHITE)
                surface.blit(name_surf, (rect.centerx - name_surf.get_width() // 2, swatch.bottom + 3))

                cost_surf = self.font_small.render(f"${tdef['cost']}", True, GOLD)
                surface.blit(cost_surf, (rect.centerx - cost_surf.get_width() // 2, swatch.bottom + 18))
            else:
                lock_surf = self.font_large.render("?", True, GRAY)
                surface.blit(lock_surf, (rect.centerx - lock_surf.get_width() // 2,
                                         rect.centery - lock_surf.get_height() // 2))

            border_color = WHITE if is_selected else (70, 70, 70)
            border_width = 3    if is_selected else 1
            pygame.draw.rect(surface, border_color, rect, border_width, border_radius=6)

            num_surf = self.font_small.render(str(i + 1), True, GRAY)
            surface.blit(num_surf, (rect.x + 4, rect.y + 4))

    def get_slot_at(self, mouse_pos):
        for i, rect in enumerate(self.slot_rects):
            if rect.collidepoint(mouse_pos):
                return i
        return None

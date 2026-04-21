import pygame
from src.settings import *
from src.wave_manager import WAITING_FOR_START, BETWEEN_WAVES, SPAWNING, WAVE_IN_PROGRESS


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


class HUD:
    """Renders the bottom UI bar: stats, wave info, Start button, tower slots."""

    def __init__(self):
        self.font_large  = pygame.font.SysFont("monospace", 22, bold=True)
        self.font_medium = pygame.font.SysFont("monospace", 16, bold=True)
        self.font_small  = pygame.font.SysFont("monospace", 13)
        self.font_wave   = pygame.font.SysFont("monospace", 15, bold=True)

        total_slots_width = TOWER_SLOTS * SLOT_SIZE + (TOWER_SLOTS - 1) * SLOT_PADDING
        start_x = (SCREEN_WIDTH - total_slots_width) // 2
        bar_top = GAME_HEIGHT

        self.slot_rects = []
        for i in range(TOWER_SLOTS):
            x = start_x + i * (SLOT_SIZE + SLOT_PADDING)
            y = bar_top + (UI_BAR_HEIGHT - SLOT_SIZE) // 2
            self.slot_rects.append(pygame.Rect(x, y, SLOT_SIZE, SLOT_SIZE))

        # Start button — right side of bar
        self.start_button_rect = pygame.Rect(
            SCREEN_WIDTH - 140, GAME_HEIGHT + 20, 120, 42)

    # ------------------------------------------------------------------
    def draw(self, surface, money, lives, tower_defs, selected_index,
             wave_num=0, total_waves=0, wm_state=WAITING_FOR_START, countdown=0):
        self._draw_bar_background(surface)
        self._draw_stats(surface, money, lives)
        self._draw_wave_info(surface, wave_num, total_waves, wm_state, countdown)
        self._draw_slots(surface, tower_defs, selected_index)
        self._draw_start_button(surface, wm_state)

    # ------------------------------------------------------------------
    def _draw_bar_background(self, surface):
        bar_rect = pygame.Rect(0, GAME_HEIGHT, SCREEN_WIDTH, UI_BAR_HEIGHT)
        pygame.draw.rect(surface, MID_GRAY, bar_rect)
        pygame.draw.line(surface, GRAY, (0, GAME_HEIGHT), (SCREEN_WIDTH, GAME_HEIGHT), 2)

    def _draw_stats(self, surface, money, lives):
        x, y = 14, GAME_HEIGHT + 14

        money_label = self.font_medium.render("MONEY", True, LIGHT_GRAY)
        money_value = self.font_large.render(f"${money}", True, GOLD)
        surface.blit(money_label, (x, y))
        surface.blit(money_value, (x, y + 22))

        lives_label = self.font_medium.render("LIVES", True, LIGHT_GRAY)
        surface.blit(lives_label, (x, y + 58))
        heart_cx = x + 12
        heart_cy = y + 84
        _draw_heart(surface, heart_cx, heart_cy, 20, RED)
        lives_surf = self.font_large.render(str(lives), True, RED)
        surface.blit(lives_surf, (heart_cx + 16, heart_cy - lives_surf.get_height() // 2))

        hint = self.font_small.render("[I] info   ESC quit", True, GRAY)
        surface.blit(hint, (14, GAME_HEIGHT + UI_BAR_HEIGHT - 18))

    def _draw_wave_info(self, surface, wave_num, total_waves, wm_state, countdown):
        x = 155
        y = GAME_HEIGHT + 14

        label = self.font_medium.render("WAVE", True, LIGHT_GRAY)
        surface.blit(label, (x, y))

        if wm_state == WAITING_FOR_START:
            val = self.font_large.render("—", True, LIGHT_GRAY)
        else:
            val = self.font_large.render(f"{wave_num} / {total_waves}", True, WHITE)
        surface.blit(val, (x, y + 22))

        if wm_state == BETWEEN_WAVES:
            cd_label = self.font_medium.render("NEXT WAVE", True, LIGHT_GRAY)
            cd_val   = self.font_large.render(f"{int(countdown) + 1}s", True, YELLOW)
            surface.blit(cd_label, (x, y + 52))
            surface.blit(cd_val,   (x, y + 72))
        elif wm_state in (SPAWNING, WAVE_IN_PROGRESS):
            status = self.font_wave.render("IN PROGRESS", True, GREEN)
            surface.blit(status, (x, y + 58))

    def _draw_start_button(self, surface, wm_state):
        r = self.start_button_rect
        if wm_state == WAITING_FOR_START:
            color  = (40, 160, 40)
            border = (100, 255, 100)
            text   = "▶  START"
        else:
            # Greyed out after game starts
            color  = (50, 50, 50)
            border = (80, 80, 80)
            text   = "STARTED"

        pygame.draw.rect(surface, color,  r, border_radius=8)
        pygame.draw.rect(surface, border, r, 2, border_radius=8)
        ts = self.font_medium.render(text, True, WHITE)
        surface.blit(ts, (r.centerx - ts.get_width() // 2,
                           r.centery - ts.get_height() // 2))

    def _draw_slots(self, surface, tower_defs, selected_index):
        for i, (rect, tdef) in enumerate(zip(self.slot_rects, tower_defs)):
            unlocked    = tdef["unlocked"]
            is_selected = (i == selected_index)

            bg_color = DARK_GRAY if unlocked else (30, 30, 30)
            pygame.draw.rect(surface, bg_color, rect, border_radius=6)

            if unlocked:
                swatch = rect.inflate(-16, -16)
                swatch.height = swatch.height // 2
                pygame.draw.rect(surface, tuple(tdef["color"]), swatch, border_radius=4)
                short = tdef["name"].split()[0]
                name_surf = self.font_small.render(short, True, WHITE)
                surface.blit(name_surf, (rect.centerx - name_surf.get_width() // 2,
                                          swatch.bottom + 3))
                cost_surf = self.font_small.render(f"${tdef['cost']}", True, GOLD)
                surface.blit(cost_surf, (rect.centerx - cost_surf.get_width() // 2,
                                          swatch.bottom + 18))
            else:
                lock_surf = self.font_large.render("?", True, GRAY)
                surface.blit(lock_surf, (rect.centerx - lock_surf.get_width() // 2,
                                          rect.centery - lock_surf.get_height() // 2))

            border_color = WHITE if is_selected else (70, 70, 70)
            border_width = 3    if is_selected else 1
            pygame.draw.rect(surface, border_color, rect, border_width, border_radius=6)

            num_surf = self.font_small.render(str(i + 1), True, GRAY)
            surface.blit(num_surf, (rect.x + 4, rect.y + 4))

    # ------------------------------------------------------------------
    def get_slot_at(self, mouse_pos):
        for i, rect in enumerate(self.slot_rects):
            if rect.collidepoint(mouse_pos):
                return i
        return None


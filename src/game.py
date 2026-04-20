import pygame
from src.settings import *


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        pass  # Game logic goes here

    def draw(self):
        self.screen.fill(DARK_GRAY)
        self._draw_grid()
        self._draw_ui()
        pygame.display.flip()

    def _draw_grid(self):
        for col in range(COLS):
            for row in range(ROWS):
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, GRAY, rect, 1)

    def _draw_ui(self):
        font = pygame.font.SysFont("monospace", 18)
        fps_text = font.render(f"FPS: {int(self.clock.get_fps())}", True, YELLOW)
        self.screen.blit(fps_text, (10, 10))
        hint = font.render("ESC to quit", True, WHITE)
        self.screen.blit(hint, (SCREEN_WIDTH - 120, 10))

    def quit(self):
        pygame.quit()
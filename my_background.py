"""
Proste animowane tlo blockchain do pygame.
Tlo pokazuje kryptograficzny deszcz bitow: kolumny znakow 0 i 1 powoli
splywaja w tle jak fragmenty hasha. Animowany jest ruch kolumn oraz ich
delikatne migotanie, a predkosc zalezy od czasu dt.
"""

import random
import pygame

class AbstractBackground:
    def update(self, dt):
        raise NotImplementedError

    def draw(self, screen):
        raise NotImplementedError

class MyBackground(AbstractBackground):
    def __init__(self, width, height, column_count=34):
        self.width = width
        self.height = height
        self.random = random.Random(12)
        self.font = None
        self.columns = []
        for _ in range(column_count):
            self.columns.append({
                "x": self.random.random(),
                "y": self.random.uniform(-1, 1),
                "speed": self.random.uniform(0.04, 0.11),
                "length": self.random.randrange(5, 12),
                "phase": self.random.random(),
            })

    def update(self, dt):
        for col in self.columns:
            col["y"] += col["speed"] * dt
            if col["y"] > 1.15:
                col["y"] = self.random.uniform(-0.35, -0.05)
                col["x"] = self.random.random()
                col["length"] = self.random.randrange(5, 12)

    def draw(self, screen):
        self.width, self.height = screen.get_size()
        if self.font is None:
            self.font = pygame.font.SysFont("consolas", 16)
        screen.fill((6, 10, 16))
        self.draw_grid(screen)
        self.draw_bits(screen)

    def draw_grid(self, screen):
        for x in range(0, self.width, 80):
            pygame.draw.line(screen, (11, 25, 32), (x, 0), (x, self.height))
        for y in range(0, self.height, 80):
            pygame.draw.line(screen, (11, 25, 32), (0, y), (self.width, y))

    def draw_bits(self, screen):
        for col in self.columns:
            x = int(col["x"] * self.width)
            y = int(col["y"] * self.height)
            for i in range(col["length"]):
                bit = "1" if (i + int(col["phase"] * 10)) % 2 == 0 else "0"
                color = (35, 85 + i * 6, 80 + i * 4)
                text = self.font.render(bit, True, color)
                screen.blit(text, (x, y - i * 18))

def run_demo():
    pygame.init()
    screen = pygame.display.set_mode((900, 600), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    background = MyBackground(*screen.get_size())
    running = True
    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        background.update(dt)
        background.draw(screen)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    run_demo()

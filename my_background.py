"""
Proste animowane tlo blockchain do pygame.
Kropki to wezly sieci, linie to polaczenia, a male punkty to dane przesylane
miedzy wezlami. Animowane sa pulsowanie wezlow i ruch danych po liniach.
Tlo pasuje do symulacji blockchain, konsensusu i propagacji blokow.
"""

import math
import random
import pygame

class AbstractBackground:
    def update(self, dt):
        raise NotImplementedError

    def draw(self, screen):
        raise NotImplementedError

class MyBackground(AbstractBackground):
    def __init__(self, width, height, node_count=20):
        self.width = width
        self.height = height
        self.time = 0
        self.random = random.Random(7)
        self.nodes = [
            {
                "x": self.random.uniform(0.08, 0.92),
                "y": self.random.uniform(0.10, 0.90),
                "phase": self.random.uniform(0, math.tau),
            }
            for _ in range(node_count)
        ]
        self.lines = []
        self.packets = []
        self.make_lines()
        for _ in range(8):
            self.add_packet()
    def make_lines(self):
        for i in range(len(self.nodes)):
            for j in range(i + 1, len(self.nodes)):
                dx = self.nodes[i]["x"] - self.nodes[j]["x"]
                dy = self.nodes[i]["y"] - self.nodes[j]["y"]
                if math.hypot(dx, dy) < 0.30:
                    self.lines.append((i, j))
    def add_packet(self):
        if self.lines:
            self.packets.append({
                "line": self.random.randrange(len(self.lines)),
                "t": self.random.random(),
                "speed": self.random.uniform(0.12, 0.35),
            })
    def update(self, dt):
        self.time += dt
        for packet in self.packets:
            packet["t"] += packet["speed"] * dt
            if packet["t"] > 1:
                packet["line"] = self.random.randrange(len(self.lines))
                packet["t"] = 0
    def draw(self, screen):
        self.width, self.height = screen.get_size()
        screen.fill((8, 12, 20))
        points = [(n["x"] * self.width, n["y"] * self.height) for n in self.nodes]
        for a, b in self.lines:
            pygame.draw.aaline(screen, (25, 55, 70), points[a], points[b])
        for packet in self.packets:
            a, b = self.lines[packet["line"]]
            x1, y1 = points[a]
            x2, y2 = points[b]
            x = x1 + (x2 - x1) * packet["t"]
            y = y1 + (y2 - y1) * packet["t"]
            pygame.draw.circle(screen, (90, 160, 150), (int(x), int(y)), 2)
        for node, (x, y) in zip(self.nodes, points):
            pulse = math.sin(self.time * 2 + node["phase"])
            color = 70 + int(pulse * 20)
            pygame.draw.circle(screen, (color, 120, 130), (int(x), int(y)), 3)

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

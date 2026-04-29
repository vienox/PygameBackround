"""
Subtle blockchain network background for pygame simulations.

Idea:
    The background shows a calm peer-to-peer blockchain network. Small nodes
    are connected by dim lines, while faint packets move between them like
    propagated transactions or blocks.

Animated elements:
    - nodes slowly pulse with independent phases,
    - data packets travel along random network connections,
    - optional block/fork events create a gentle wave through the graph.

Best fit:
    Blockchain, consensus, block propagation, fork, mempool, and distributed
    network simulations where the foreground should stay readable.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import math
import random
from typing import List, Tuple

import pygame


Color = Tuple[int, int, int]
Point = Tuple[float, float]


class AbstractBackground(ABC):
    """Base class compatible with simple pygame simulation backgrounds."""

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update animation state.

        Args:
            dt: Time in seconds since the previous frame.
        """

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the background on the target surface."""


@dataclass
class NetworkNode:
    x_ratio: float
    y_ratio: float
    phase: float
    pulse_speed: float
    base_radius: float


@dataclass
class DataPacket:
    connection_index: int
    progress: float
    speed: float
    radius: float


@dataclass
class WaveEvent:
    origin: Point
    age: float
    speed: float
    max_radius: float
    color: Color


class MyBackground(AbstractBackground):
    """Animated, low-contrast blockchain network background."""

    def __init__(
        self,
        width: int,
        height: int,
        node_count: int = 36,
        seed: int = 21,
    ) -> None:
        self.width = width
        self.height = height
        self.node_count = node_count
        self.seed = seed
        self.random = random.Random(seed)

        self.nodes: List[NetworkNode] = []
        self.connections: List[Tuple[int, int]] = []
        self.packets: List[DataPacket] = []
        self.waves: List[WaveEvent] = []

        self.time = 0.0
        self.spawn_timer = 0.0
        self.mode = "network"

        self.background_color = (8, 13, 20)
        self.line_color = (34, 76, 94)
        self.node_color = (74, 132, 145)
        self.packet_color = (110, 190, 175)
        self.fork_color = (140, 105, 170)

        self._build_graph()

    def update(self, dt: float) -> None:
        dt = max(0.0, min(dt, 0.05))
        self.time += dt
        self.spawn_timer -= dt

        if self.spawn_timer <= 0.0 and self.connections:
            self._spawn_packet()
            self.spawn_timer = self.random.uniform(0.18, 0.55)

        for packet in self.packets:
            packet.progress += packet.speed * dt
        self.packets = [packet for packet in self.packets if packet.progress <= 1.0]

        for wave in self.waves:
            wave.age += dt
        self.waves = [
            wave for wave in self.waves if wave.age * wave.speed <= wave.max_radius
        ]

    def draw(self, screen: pygame.Surface) -> None:
        size = screen.get_size()
        if size != (self.width, self.height):
            self.resize(*size)

        screen.fill(self.background_color)
        self._draw_vignette(screen)

        layer = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        positions = [self._node_position(node) for node in self.nodes]

        self._draw_connections(layer, positions)
        self._draw_waves(layer)
        self._draw_packets(layer, positions)
        self._draw_nodes(layer, positions)

        screen.blit(layer, (0, 0))

    def resize(self, width: int, height: int) -> None:
        """Adjust drawing dimensions without changing the graph structure."""

        self.width = max(1, width)
        self.height = max(1, height)

    def trigger_block_event(self) -> None:
        """Bonus hook: call when a new block appears in the simulation."""

        if not self.nodes:
            return
        node = self.random.choice(self.nodes)
        self._add_wave(self._node_position(node), self.packet_color)

        for _ in range(4):
            self._spawn_packet(speed_boost=1.7)

    def trigger_fork_event(self) -> None:
        """Bonus hook: call when the simulation creates a fork."""

        if not self.nodes:
            return
        for node in self.random.sample(self.nodes, k=min(2, len(self.nodes))):
            self._add_wave(self._node_position(node), self.fork_color)
        for _ in range(7):
            self._spawn_packet(speed_boost=2.0)

    def toggle_mode(self) -> None:
        """Switch between calm network and slightly more active propagation."""

        self.mode = "propagation" if self.mode == "network" else "network"

    def _build_graph(self) -> None:
        self.nodes.clear()
        self.connections.clear()

        for _ in range(self.node_count):
            self.nodes.append(
                NetworkNode(
                    x_ratio=self.random.uniform(0.06, 0.94),
                    y_ratio=self.random.uniform(0.08, 0.92),
                    phase=self.random.uniform(0.0, math.tau),
                    pulse_speed=self.random.uniform(0.45, 1.1),
                    base_radius=self.random.uniform(2.0, 3.6),
                )
            )

        pairs: set[Tuple[int, int]] = set()
        for index, node in enumerate(self.nodes):
            distances = []
            for other_index, other in enumerate(self.nodes):
                if index == other_index:
                    continue
                dx = node.x_ratio - other.x_ratio
                dy = node.y_ratio - other.y_ratio
                distances.append((math.hypot(dx, dy), other_index))

            for _, other_index in sorted(distances)[:2]:
                pairs.add(tuple(sorted((index, other_index))))

            for distance, other_index in distances:
                if distance < 0.18 and self.random.random() < 0.38:
                    pairs.add(tuple(sorted((index, other_index))))

        self.connections = sorted(pairs)

    def _node_position(self, node: NetworkNode) -> Point:
        return (node.x_ratio * self.width, node.y_ratio * self.height)

    def _draw_vignette(self, screen: pygame.Surface) -> None:
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        max_radius = max(self.width, self.height)
        center = (self.width // 2, self.height // 2)

        for radius in range(max_radius, 0, -42):
            alpha = int(34 * (radius / max_radius) ** 2)
            pygame.draw.circle(overlay, (0, 0, 0, alpha), center, radius)

        screen.blit(overlay, (0, 0))

    def _draw_connections(self, layer: pygame.Surface, positions: List[Point]) -> None:
        for connection_index, (start_index, end_index) in enumerate(self.connections):
            start = positions[start_index]
            end = positions[end_index]
            line_alpha = 28 + int(8 * math.sin(self.time * 0.7 + connection_index))
            pygame.draw.aaline(
                layer,
                (*self.line_color, max(16, line_alpha)),
                start,
                end,
            )

    def _draw_packets(self, layer: pygame.Surface, positions: List[Point]) -> None:
        for packet in self.packets:
            start_index, end_index = self.connections[packet.connection_index]
            start = positions[start_index]
            end = positions[end_index]
            eased = self._smooth_step(packet.progress)
            x = start[0] + (end[0] - start[0]) * eased
            y = start[1] + (end[1] - start[1]) * eased

            fade = math.sin(packet.progress * math.pi)
            alpha = int(90 * fade)
            radius = packet.radius + 1.0 * fade
            pygame.draw.circle(
                layer,
                (*self.packet_color, alpha),
                (round(x), round(y)),
                max(1, round(radius)),
            )

    def _draw_nodes(self, layer: pygame.Surface, positions: List[Point]) -> None:
        for node, position in zip(self.nodes, positions):
            pulse = math.sin(self.time * node.pulse_speed + node.phase)
            radius = node.base_radius + 0.8 * pulse
            alpha = 52 + int(26 * (pulse + 1.0) * 0.5)

            pygame.draw.circle(
                layer,
                (*self.node_color, 22),
                (round(position[0]), round(position[1])),
                round(radius + 4),
            )
            pygame.draw.circle(
                layer,
                (*self.node_color, alpha),
                (round(position[0]), round(position[1])),
                max(2, round(radius)),
            )

    def _draw_waves(self, layer: pygame.Surface) -> None:
        for wave in self.waves:
            radius = wave.age * wave.speed
            fade = max(0.0, 1.0 - radius / wave.max_radius)
            alpha = int(42 * fade)
            if alpha <= 0:
                continue
            pygame.draw.circle(
                layer,
                (*wave.color, alpha),
                (round(wave.origin[0]), round(wave.origin[1])),
                round(radius),
                width=1,
            )

    def _spawn_packet(self, speed_boost: float = 1.0) -> None:
        if not self.connections:
            return

        base_speed = self.random.uniform(0.15, 0.32)
        if self.mode == "propagation":
            base_speed *= 1.45

        self.packets.append(
            DataPacket(
                connection_index=self.random.randrange(len(self.connections)),
                progress=0.0,
                speed=base_speed * speed_boost,
                radius=self.random.uniform(1.2, 2.0),
            )
        )

    def _add_wave(self, origin: Point, color: Color) -> None:
        self.waves.append(
            WaveEvent(
                origin=origin,
                age=0.0,
                speed=max(self.width, self.height) * 0.34,
                max_radius=max(self.width, self.height) * 0.55,
                color=color,
            )
        )

    @staticmethod
    def _smooth_step(value: float) -> float:
        value = max(0.0, min(1.0, value))
        return value * value * (3.0 - 2.0 * value)


def run_demo() -> None:
    pygame.init()
    pygame.display.set_caption("MyBackground - blockchain network")

    screen = pygame.display.set_mode((1100, 700), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    background = MyBackground(*screen.get_size())

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_SPACE:
                    background.trigger_block_event()
                elif event.key == pygame.K_f:
                    background.trigger_fork_event()
                elif event.key == pygame.K_TAB:
                    background.toggle_mode()

        background.update(dt)
        background.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run_demo()

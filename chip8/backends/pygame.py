from typing import Iterator

import enum
import time

import pygame

from .base import WIDTH, HEIGHT
from .events import Event, EventType

import logging

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


class PyGameBackend(Backend):
    def __init__(self, hertz: int = 60):
        self.hertz = hertz
        # Time in ms when throttle was last called
        self.tick = 0

    def get(self) -> Iterator[Event]:
        """Yield a bridged Event object for pygame events we're interested in."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                yield Event(type=EventType.QUIT)
            if event.type == pygame.KEYDOWN:
                yield Event(keycode=event.key, type=EventType.KEYDOWN)
            if event.type == pygame.KEYUP:
                yield Event(keycode=event.key, type=EventType.KEYUP)

    def throttle(self):
        """Ensure event loop runs at an even cadence.

         - If throttle is called early, pygame.time.delay is used to delay
           execution until it's expected.

         - If throttle is called late, event loop is executed as quickly as
        possible.
        """
        now = time.perf_counter()

        expected_time_to_render = self.tick + 1.0 / self.hertz
        if expected_time_to_render > now:
            # Enforce a delay if we're running too quickly
            delay = int(1000 * (expected_time_to_render - now))
            pygame.time.delay(delay)
            self.tick = expected_time_to_render
        else:
            self.tick = now


class Color(enum.Enum):
    BLACK = pygame.Color(0, 0, 0)
    WHITE = pygame.Color(255, 255, 255)


class Display:

    width: int = WIDTH

    height: int = HEIGHT

    def __init__(self, scale):
        self.size = self.width, self.height
        self.scale = scale

        self.window = pygame.display.set_mode(
            (self.width * self.scale, self.height * self.scale), vsync=1
        )

        self.screen = pygame.Surface(self.size)

    def set_pixel(self, x, y) -> bool:
        is_pixel_already_rendered = self.screen.get_at((x, y)) == Color.WHITE.value
        color = Color.BLACK.value if is_pixel_already_rendered else Color.WHITE.value
        self.screen.set_at((x, y), color)

        return is_pixel_already_rendered

    def draw_sprite(self, sprite, x, y) -> bool:

        does_sprite_overlap = False

        for line_count, line in enumerate(sprite):
            for char_count, character in enumerate(format(line, "0bb")):
                if character == "1":

                    wrapped_x = (x + char_count) % self.width
                    wrapped_y = (y + line_count) % self.height

                    is_pixel_already_rendered = self.set_pixel(wrapped_x, wrapped_y)
                    if is_pixel_already_rendered:
                        does_sprite_overlap = True

        self.update()

        return does_sprite_overlap

    def update(self):
        self.window.blit(
            pygame.transform.scale(self.screen, self.window.get_rect().size), (0, 0)
        )
        pygame.display.flip()

    def clear(self):
        self.screen.fill(Color.BLACK.value)

from typing import Iterator

import enum

import pygame

from .events import Event, EventType

import logging

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")



class PyGameBackend:
    def get(self) -> Iterator[Event]:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                yield Event(keycode=event.key, type=EventType.KEYDOWN)
            if event.type == pygame.KEYUP:
                yield Event(keycode=event.key, type=EventType.KEYUP)


class Color(enum.Enum):
    BLACK = pygame.Color(0, 0, 0)
    WHITE = pygame.Color(255, 255, 255)


class Display:
    def __init__(self, width, height, scale):
        self.size = self.width, self.height = width, height
        self.scale = scale

        self.window = pygame.display.set_mode(
            (self.width * self.scale, self.height * self.scale), pygame.SCALED, vsync=1
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
            for char_count, character in enumerate(format(line, "b")):
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

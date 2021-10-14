from enum import Enum

import pygame

import logging

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


class Color(Enum):
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

    def set_pixel(self, x, y):

        if x > self.width - 1 or y > self.height - 1:
            logger.debug(f"Width or height exceeded. Exiting...")
            return

        if self.screen.get_at((x, y)) == Color.WHITE.value:
            self.screen.set_at((x, y), Color.BLACK.value)
        else:
            self.screen.set_at((x, y), Color.WHITE.value)

    def draw_sprite(self, sprite, x, y):

        adjusted_x = x if x <= self.width else (x % self.width + 1)
        adjusted_y = y if y <= self.height else (y % self.height + 1)

        set_y = adjusted_y
        for line in sprite:
            set_x = adjusted_x
            for character in format(line, "08b"):
                if character == "1":
                    self.set_pixel(set_x, set_y)
                set_x = set_x + 1
                logger.debug(f"draw_sprite: x: {set_x}, y: {set_y}")
            set_y = set_y + 1

        self.update()

    def update(self):
        self.window.blit(
            pygame.transform.scale(self.screen, self.window.get_rect().size), (0, 0)
        )
        pygame.display.flip()
        logger.error(f"draw")

    def clear(self):
        self.screen.fill(Color.BLACK.value)

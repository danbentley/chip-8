import enum
import time
from typing import Iterator

import pygame

from .base import Backend, Renderable, Sprite, WIDTH, HEIGHT
from .events import Event, EventType

import logging

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


class PyGameBackend(Backend):
    def __init__(self, hertz: int = 60):
        self.hertz: int = hertz
        # Time in ms when throttle was last called
        self.tick: float = 0

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
    """Pygame-specific colour settings for display.

    On/off values can be changed to theme the display's output.

    Defaulted to ON: White, OFF: Black
    """

    ON = pygame.Color(255, 255, 255)
    OFF = pygame.Color(0, 0, 0)


class Display(Renderable):

    width: int = WIDTH

    height: int = HEIGHT

    def __init__(self, scale):
        """Set up pygame surfaces for drawing.

        Create a pygame window, a display surface to render the game to
        and an additional surface to use as a scratch area.
        """
        self.display = pygame.display.set_mode(
            (self.width * scale, self.height * scale),
        )
        self.surface = pygame.Surface((self.width, self.height))

    def set_pixel(self, x, y) -> bool:
        """Enable/disable a specific pixel.

        raises IndexError if pixel is queried outside of surface bounds.

        Using pygame.Surface.set_at/get_at is slow. Manipulating a pygame.PixelArray
        in memory may be a better approach.

        https://www.pygame.org/docs/ref/surface.html#pygame.Surface.get_at
        """
        is_pixel_already_rendered = self.surface.get_at((x, y)) == Color.ON.value
        color = Color.OFF.value if is_pixel_already_rendered else Color.ON.value
        self.surface.set_at((x, y), color)

        return is_pixel_already_rendered

    def draw_sprite(self, sprite: Sprite, x, y) -> bool:
        """Draw sprite to surface."""

        does_sprite_overlap = False

        for line_count, line in enumerate(sprite):
            for char_count, character in enumerate(format(line, "04b")):
                if character == "1":

                    wrapped_x = (x + char_count) % self.width
                    wrapped_y = (y + line_count) % self.height

                    is_pixel_already_rendered = self.set_pixel(wrapped_x, wrapped_y)
                    if is_pixel_already_rendered:
                        does_sprite_overlap = True

        self.update()

        return does_sprite_overlap

    def update(self):
        """Bilt to the display to reflect changes made to a surface's pixels.

        This is sub-optimal. Since we know where the size of a sprite and where
        it's drawn, performance may be improved by only blitting the affected
        pixels.
        """
        # Transfer the changes made to the surface to the main display
        # https://www.pygame.org/docs/ref/display.html#pygame.display.blit
        self.display.blit(
            pygame.transform.scale(self.surface, self.display.get_rect().size), (0, 0)
        )
        # Render a surface's surface to display
        # https://www.pygame.org/docs/ref/display.html#pygame.display.flip
        pygame.display.flip()

    def clear(self):
        """Clear surface. Used by opcode 0x00E0

        https://www.pygame.org/docs/ref/surface.html?highlight=fill#pygame.Surface.fill
        """
        self.surface.fill(Color.OFF.value)

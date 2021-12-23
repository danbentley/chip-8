import enum
import time

from typing import Iterator

import sdl2
import sdl2.ext

from .events import Event, EventType
from .base import Backend, Renderable, Sprite, WIDTH, HEIGHT


class PySDLBackend(Backend):
    def __init__(self, hertz: int = 60):
        self.hertz: int = hertz
        # Time in ms when throttle was last called
        self.tick: float = 0

    def get(self) -> Iterator[Event]:
        """Yield a bridged Event object for sdl2 events we're interested in."""
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                sdl2.ext.quit()
                yield Event(type=EventType.QUIT)
            if event.type == sdl2.SDL_KEYDOWN:
                keycode = event.key.keysym.sym
                yield Event(keycode=keycode, type=EventType.KEYDOWN)
            if event.type == sdl2.SDL_KEYUP:
                keycode = event.key.keysym.sym
                yield Event(keycode=keycode, type=EventType.KEYUP)

    def throttle(self):
        """Ensure event loop runs at an even cadence.

         - If throttle is called early, SDL_Delay is used to delay execution until
        it's expected.

         - If throttle is called late, event loop is executed as quickly as
        possible.
        """
        now = time.perf_counter()

        expected_time_to_render = self.tick + 1.0 / self.hertz
        if expected_time_to_render > now:
            # Enforce a delay if we're running too quickly
            delay = int(1000 * (expected_time_to_render - now))
            sdl2.SDL_Delay(delay)
            self.tick = expected_time_to_render
        else:
            self.tick = now


class Color(enum.Enum):
    """SDL2-specific colour settings for display.

    On/off values can be changed to theme the display's output.

    Defaulted to ON: White, OFF: Black
    """

    ON = sdl2.ext.Color(255, 255, 255)
    OFF = sdl2.ext.Color(0, 0, 0)


class Display(Renderable):

    width: int = WIDTH
    height: int = HEIGHT

    def __init__(self, scale):
        """
        - Surface: A collection of pixels for rendering
        - Renderer: Handles drawing pixels to a window
        - Window: Interface for graphics

         - https://wiki.libsdl.org/SDL_Surface
         - https://wiki.libsdl.org/SDL_Renderer
         - https://wiki.libsdl.org/SDL_Window
        """
        self.scale = scale

        self.window = sdl2.ext.Window(
            b"",
            size=(self.width * self.scale, self.height * self.scale),
            flags=sdl2.SDL_WINDOW_ALLOW_HIGHDPI,
        )
        self.window.show()

        self.surface = self.window.get_surface()
        self.renderer = sdl2.ext.Renderer(self.surface)
        self.renderer.scale = (self.scale, self.scale)

    def set_pixel(self, x: int, y: int) -> bool:
        """
        Draw pixel to screen. Chip-8 has no framebuffer so pixels are drawn
        immediately.

        Before drawing a pixel we check for whether the pixel has already been
        drawn to report back to draw_sprite for basic collision detection.

        https://pysdl2.readthedocs.io/en/latest/modules/sdl2ext_pixelaccess.html#sdl2.ext.PixelView
        """
        pixel_view = sdl2.ext.PixelView(self.surface)

        is_pixel_already_rendered = (
            sdl2.ext.ARGB(pixel_view[y * self.scale][x * self.scale]) == Color.ON.value
        )
        color = Color.OFF.value if is_pixel_already_rendered else Color.ON.value
        self.renderer.draw_point((x, y), color=color)
        self.renderer.present()

        return is_pixel_already_rendered

    def draw_sprite(self, sprite: Sprite, x: int, y: int) -> bool:
        """Draw sprite to renderer."""
        does_sprite_overlap = False

        for line_count, line in enumerate(sprite):
            for char_count, character in enumerate(format(line, "08b")):

                if character == "1":

                    wrapped_x = (x + char_count) % self.width
                    wrapped_y = (y + line_count) % self.height

                    is_pixel_already_rendered = self.set_pixel(wrapped_x, wrapped_y)
                    if is_pixel_already_rendered:
                        does_sprite_overlap = True

        self.update()

        return does_sprite_overlap

    def update(self):
        """Draw changes made to renderer to screen."""
        self.window.refresh()

    def clear(self):
        """Clear the display by setting all pixels to 'off'."""
        sdl2.ext.fill(self.surface, Color.OFF.value)

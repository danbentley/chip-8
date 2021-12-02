import enum

from typing import Iterator

import sdl2
import sdl2.ext

from .events import Event, EventType
from .base import Backend


class PySDLBackend(Backend):
    def get(self) -> Iterator[Event]:
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                ...
            if event.type == sdl2.SDL_KEYDOWN:
                keycode = event.key.keysym.sym
                yield Event(keycode=keycode, type=EventType.KEYDOWN)
            if event.type == sdl2.SDL_KEYUP:
                keycode = event.key.keysym.sym
                yield Event(keycode=keycode, type=EventType.KEYUP)


class Color(enum.Enum):
    BLACK = sdl2.ext.Color(0, 0, 0)
    WHITE = sdl2.ext.Color(255, 255, 255)


class Display:
    def __init__(self, width, height, scale):
        self.size = self.width, self.height = width, height
        self.scale = scale

        # TODO remove
        self.scale = 8

        self.window = sdl2.ext.Window(
            b"",
            size=(self.width * self.scale, self.height * self.scale),
            flags=sdl2.SDL_WINDOW_ALLOW_HIGHDPI,
        )
        self.window.show()

        self.screen = self.window.get_surface()
        # self.renderer = sdl2.SDL_CreateSoftwareRenderer(self.screen)
        self.renderer = sdl2.ext.Renderer(self.screen)
        # self.renderer.logical_size = (self.width * 4, self.height * 4)
        self.renderer.scale = (self.scale, self.scale)

    def set_pixel(self, x, y) -> bool:
        # https://stackoverflow.com/questions/20579658/how-to-draw-pixels-in-sdl-2-0
        pixel_view = sdl2.ext.PixelView(self.screen)

        is_pixel_already_rendered = sdl2.ext.ARGB(pixel_view[y * self.scale][x * self.scale]) == Color.WHITE.value
        color = Color.BLACK.value if is_pixel_already_rendered else Color.WHITE.value
        # SDL_RenderReadPixels
        self.renderer.draw_point((x, y), color=color)
        self.renderer.present()

        # color = Color.BLACK.value if is_pixel_already_rendered else Color.WHITE.value
        # pixel_view[y][x] = color

        return is_pixel_already_rendered

    def draw_sprite(self, sprite, x, y) -> bool:

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
        self.window.refresh()
        # self.renderer.present()
        # sdl2.surface.SDL_BlitSurface(None, None, self.screen, None)
        # self.screen.SDL_BlitSurface(
        # pygame.transform.scale(self.screen, self.window.get_rect().size), (0, 0)
        # )
        # pygame.display.flip()

    def clear(self):
        self.screen.fill(Color.BLACK.value)

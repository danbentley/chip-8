from typing import Protocol, Iterator

from .events import Event

WIDTH = 64
HEIGHT = 32


class Backend(Protocol):
    """Bridge for a common protocol for common Python game backends.

    Bridged protocols should convert the Python-specific backend event
    to a more general Event object.

    See EventType for a list of events that should be handled.
    """

    def get(self) -> Iterator[Event]:
        """yield the next event on the backend's stack."""

    def throttle(self):
        """Ensure event loop runs at an even cadence."""


class Renderable(Protocol):
    """A common protocol to display CHIP-8 games.

    Because of the small dimensions of a CHIP-8 game, the
    window should support scaling.
    """

    def draw_sprite(self, sprite: list[int], x: int, y: int) -> bool:
        """Render the sprite to screen at the given coordinates.

        Sprites are lists containing 8-bit integers. Each int is converted to
        its binary representation. A 1 being a pixel that's on, a 0 being a
        pixel that's off.

        Sprites that exceed the bounds of the screen will wrap.

        Method returns True if any part of the sprite overlaps an existing
        sprite (a basic form of collision detection).

        Required to support opcode 0xDXYN
        """

    def update(self):
        """Render updates"""

    def clear(self):
        """Clear the screen's contents.

        Required to support opcode 0x0E0
        """

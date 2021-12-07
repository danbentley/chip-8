from typing import Optional

import enum

from .backends.events import EventType
from .cpu import FONT_ADDRESS_START, FONT_ADDRESS_END
from .fonts import Font


class Keyboard(enum.Enum):
    """
    Tuple of mappings, the first value being the keyboard's keycode and the
    second the value passed to the interpreter.

    A CHIP-8 interpreter should support 16 keys:

    +–+–+–+–+
    |1|2|3|C|
    +–+–+–+–+
    |4|5|6|D|
    +–+–+–+–+
    |7|8|9|E|
    +–+–+–+–+
    |A|0|B|F|
    +–+–+–+–+

    Which are mapped to:

    +–+–+–+–+
    |1|2|3|4|
    +–+–+–+–+
    |Q|W|E|R|
    +–+–+–+–+
    |A|S|D|F|
    +–+–+–+–+
    |Z|X|C|V|
    +–+–+–+–+

    https://wiki.libsdl.org/SDLKeycodeLookup
    """

    ONE = (49, 0x1)
    TWO = (50, 0x2)
    THREE = (51, 0x3)
    C = (99, 0xC)

    FOUR = (113, 0x4)
    FIVE = (119, 0x5)
    SIX = (101, 0x6)
    D = (114, 0xD)

    SEVEN = (97, 0x7)
    EIGHT = (115, 0x8)
    NINE = (100, 0x9)
    E = (102, 0xE)

    A = (122, 0xA)
    ZERO = (120, 0x0)
    B = (98, 0xB)
    F = (118, 0xF)

    @classmethod
    def value_for_keycode(cls, keycode) -> Optional[int]:
        """Return a key's mapping for a given SDL keycode."""
        return next((k.value[1] for k in cls if k.value[0] == keycode), None)


class Interpreter:
    def __init__(self, backend, cpu):
        self.backend = backend
        self.cpu = cpu

    def boot(self):
        fonts = Font.__members__.values()
        for font, location in zip(
            fonts, range(FONT_ADDRESS_START, FONT_ADDRESS_END, 5)
        ):
            self.cpu.memory[location : location + 5] = font.value

    def load_rom(self, path):
        with open(path, "rb") as f:
            rom = f.read()
            for instruction, location in zip(rom, range(0x200, 0xFFF)):
                self.cpu.memory[location] = instruction

    def run(self):
        while True:
            for event in self.backend.get():
                if event.type == EventType.KEYDOWN:
                    self.cpu.keycode = Keyboard.value_for_keycode(event.keycode)
                if event.type == EventType.KEYUP:
                    self.cpu.keycode = None
            self.cpu.cycle()

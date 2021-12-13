from typing import Optional

import enum

from .backends.base import Backend
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
    """The interpreter ties together the CPU with the game backend.

    Responsible for setting up the initial environment and running the both the
    event loop and executing a CPU cycle.
    """

    def __init__(self, backend: Backend, cpu):
        self.backend = backend
        self.cpu = cpu

    def boot(self):
        """Load system fonts into memory."""
        fonts = Font.__members__.values()
        for font, location in zip(
            fonts, range(FONT_ADDRESS_START, FONT_ADDRESS_END, 5)
        ):
            self.cpu.memory[location : location + 5] = font.value

    def load_rom(self, path):
        """Load a ROM file into memory."""
        with open(path, "rb") as f:
            rom = f.read()
            for instruction, location in zip(rom, range(0x200, 0xFFF)):
                self.cpu.memory[location] = instruction

    def run(self):
        """Start the event loop and execute CPU cycle."""
        running = True

        while running:
            self.backend.throttle()

            for event in self.backend.get():
                if event.type == EventType.KEYDOWN:
                    self.cpu.keycode = Keyboard.value_for_keycode(event.keycode)
                if event.type == EventType.KEYUP:
                    self.cpu.keycode = None
                if event.type == EventType.QUIT:
                    running = False
            self.cpu.cycle()

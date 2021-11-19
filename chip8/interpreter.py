from .backends.events import EventType
from .backends.pygame import PyGameBackend, Keyboard
from .cpu import CPU, Registers, FONT_ADDRESS_START, FONT_ADDRESS_END
from .display import Display
from .fonts import Font
from .memory import Memory


class Interpreter:
    def __init__(self):
        self.memory = Memory()
        self.display = Display(width=64, height=32, scale=4)
        self.cpu = CPU(self.memory, self.display, Registers())
        self.backend = PyGameBackend()

    def boot(self):
        fonts = Font.__members__.values()
        for font, location in zip(
            fonts, range(FONT_ADDRESS_START, FONT_ADDRESS_END, 5)
        ):
            self.memory[location : location + 5] = font.value

    def load_rom(self, path):
        with open(path, "rb") as f:
            rom = f.read()
            for instruction, location in zip(rom, range(0x200, 0xFFF)):
                self.memory[location] = instruction

    def run(self):
        while True:
            for event in self.backend.get():
                if event.type == EventType.KEYDOWN:
                    keycode = None
                    for c in Keyboard:
                        if c.value[0] == event.keycode:
                            keycode = c.value[1]
                    self.cpu.keycode = keycode
                if event.type == EventType.KEYUP:
                    self.cpu.keycode = None
            self.cpu.cycle()

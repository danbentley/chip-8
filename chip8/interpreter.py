import pygame

from chip8.memory import Memory
from chip8.fonts import Font
from chip8.display import Display
from chip8.cpu import CPU, Registers, FONT_ADDRESS_START, FONT_ADDRESS_END


class Keyboard(enum.Enum):
    ONE = (pygame.K_1, 0x1)
    TWO = (pygame.K_2, 0x2)
    THREE = (pygame.K_3, 0x3)
    FOUR = (pygame.K_4, 0xC)
    Q = (pygame.K_q, 0x4)
    W = (pygame.K_w, 0x5)
    E = (pygame.K_e, 0x6)
    R = (pygame.K_r, 0xD)
    A = (pygame.K_a, 0x7)
    S = (pygame.K_s, 0x8)
    D = (pygame.K_d, 0x9)
    F = (pygame.K_f, 0xE)
    Z = (pygame.K_z, 0xA)
    X = (pygame.K_x, 0x0)
    C = (pygame.K_c, 0xB)
    V = (pygame.K_v, 0xF)


class Interpreter:
    def __init__(self):
        self.memory = Memory()
        self.display = Display(width=64, height=32, scale=4)
        self.cpu = CPU(self.memory, self.display, Registers())

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
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    keycode = None
                    for c in Keyboard:
                        if c.value[0] == event.key:
                            keycode = c.value[1]
                    self.cpu.keycode = keycode
                if event.type == pygame.KEYUP:
                    self.cpu.keycode = None
            self.cpu.cycle()

import pygame

from chip8.memory import Memory
from chip8.fonts import Font
from chip8.display import Display
from chip8.cpu import CPU, Registers, FONT_ADDRESS_START, FONT_ADDRESS_END


class Interpreter:
    def __init__(self):
        self.memory = Memory()
        self.display = Display(width=64, height=32, scale=4)
        self.cpu = CPU(self.memory, self.display, Registers())

    def boot(self):
        fonts = Font.__members__.values()
        for font, location in zip(fonts, range(FONT_ADDRESS_START, FONT_ADDRESS_END, 5)):
            self.memory[location: location + 5] = font.value

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
            self.cpu.cycle()

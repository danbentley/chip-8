import argparse

from chip8.interpreter import Interpreter
from chip8.memory import Memory
from chip8.backends.pygame import PyGameBackend, Display as PyGameDisplay
from chip8.backends.pysdl import PySDLBackend, Display as SDLDisplay
from chip8.cpu import CPU, Registers


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to rom file")
    args = parser.parse_args()

    memory = Memory()

    # display = PyGameDisplay(width=64, height=32, scale=4)
    # backend = PyGameBackend()

    display = SDLDisplay(width=64, height=32, scale=4)
    backend = PySDLBackend()

    cpu = CPU(memory, display, Registers())

    interpreter = Interpreter(memory, display, backend, cpu)
    interpreter.boot()
    interpreter.load_rom(args.path)
    interpreter.run()


if __name__ == "__main__":
    main()

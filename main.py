import argparse

from chip8.interpreter import Interpreter
from chip8.memory import Memory
from chip8.backends.pygame import PyGameBackend, Display as PyGameDisplay
from chip8.backends.pysdl import PySDLBackend, Display as SDLDisplay
from chip8.cpu import CPU, Registers


def main(rom_path, backend_name, scale):
    memory = Memory()

    if backend_name == "pygame":
        display = PyGameDisplay(scale=scale)
        backend = PyGameBackend()
    else:
        display = SDLDisplay(scale=scale)
        backend = PySDLBackend()

    cpu = CPU(memory, display, Registers())

    interpreter = Interpreter(backend, cpu)
    interpreter.boot()
    interpreter.load_rom(rom_path)
    interpreter.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="Path to rom file")
    parser.add_argument(
        "--backend",
        help="Backend used to run the interpreter",
        choices=["pygame", "sdl"],
        default="pygame",
    )
    parser.add_argument(
        "--scale",
        type=int,
        help="Scale the 64x32 display for better rendering on modern monitors",
        default=8,
    )
    args = parser.parse_args()

    main(args.path, args.backend, args.scale)

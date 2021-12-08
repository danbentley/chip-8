from ctypes import c_uint8

import pytest

from chip8.cpu import (
    Registers,
    CPU,
)
from chip8.memory import Memory
from chip8.interpreter import Interpreter
from chip8.backends.pygame import PyGameBackend


@pytest.fixture
def memory(request):
    memory = Memory()

    # Optionally run this fixture with a rom to load into memory.
    # https://docs.pytest.org/en/6.2.x/parametrize.html
    try:
        rom = request.param
    except AttributeError:
        rom = []

    for instruction, location in zip(rom, range(0x200, 0xFFF)):
        memory[location] = instruction

    return memory


@pytest.fixture
def registers(request):
    registers = Registers()
    try:
        for key, value in request.param:
            registers[key] = c_uint8(value)
    except TypeError:
        raise pytest.UsageError("Make sure fixture data for registers is iterable.")
    except AttributeError:
        # No params on request object, skip
        ...
    return registers


@pytest.fixture
def cpu(memory, display, registers):
    return CPU(memory, display, registers)


@pytest.fixture
def display():
    class Display:
        def __init__(self, *args, **kwargs):
            pass

        def draw_sprite(self, *args, **kwargs):
            self.draw_sprite_called = True
            # Always return False to report no collision
            return False

        draw_sprite_called = False

        def clear(self, *args, **kwargs):
            self.clear_called = True

        clear_called = False

    return Display(width=64, height=45, scale=4)


@pytest.fixture
def interpreter(cpu):
    return Interpreter(PyGameBackend(), cpu)

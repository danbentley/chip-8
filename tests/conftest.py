from ctypes import c_uint8

import pytest

from chip8.cpu import (
    Registers,
    CPU,
)
from chip8.memory import Memory
from chip8.interpreter import Interpreter
from chip8.backends.pygame import PyGameBackend


@pytest.fixture(autouse=True)
def pygame(monkeypatch):
    """Patch pygame to prevent it from running during testing."""

    def noop(*args, **kwargs):
        ...

    monkeypatch.setattr("pygame.event", noop)
    monkeypatch.setattr("pygame.display.set_mode", noop)
    monkeypatch.setattr("pygame.Surface", noop)


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
            return self.draw_sprite_called

        draw_sprite_called = False

        def clear(self, *args, **kwargs):
            self.clear_called = True
            return self.clear_called

        clear_called = False

    return Display(width=64, height=45, scale=4)


@pytest.fixture
def interpreter(cpu):
    return Interpreter(PyGameBackend(), cpu)

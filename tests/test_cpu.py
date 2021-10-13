import pytest

from chip8.cpu import (
    Registers,
    InvalidRegisterError,
    Operation,
)
from chip8.memory import Memory, InvalidMemoryAddressError


@pytest.fixture
def registers():
    return Registers()


class TestRegisters:
    def test_set(self, registers):
        registers["0"] = 0b00001111
        assert registers["0"] == 0b00001111

    def test_set_invalid_register(self, registers):
        with pytest.raises(InvalidRegisterError):
            registers["invalid"] = 0b00001111

    def test_access_invalid_register(self, registers):
        with pytest.raises(InvalidRegisterError):
            registers["invalid"]

    def test_direct_access(self, registers):
        registers["0"] = 0b00001111
        assert registers.V0 == 0b00001111

    def test_direct_access_get(self, registers):
        registers.V0 = 0b00001111
        assert registers["0"] == 0b00001111


class TestOperation:
    def test_clear_screen(self):
        opcode = 0xE0

        operation = Operation.decode(opcode)

        assert operation.low == Operation.CLEAR_SCREEN
        assert operation.nibble == 0x0

    def test_jump(self):
        opcode = 0x1228

        operation = Operation.decode(opcode)

        assert operation.nibble == Operation.JUMP
        assert operation.nnn == 0x228

    def test_set_register(self):
        opcode = 0x600C

        operation = Operation.decode(opcode)

        assert operation.nibble == Operation.SET_REGISTER
        assert operation.x == 0x0
        assert operation.nn == 0xC

    def test_add(self):
        opcode = 0x7009

        operation = Operation.decode(opcode)

        assert operation.nibble == Operation.ADD
        assert operation.x == 0x0
        assert operation.nn == 0x9

    def test_set_index(self):
        opcode = 0xA22A

        operation = Operation.decode(opcode)

        assert operation.nibble == Operation.SET_INDEX
        assert operation.nn == 0x2A

    def test_display(self):
        opcode = 0xD01F

        operation = Operation.decode(opcode)

        assert operation.nibble == Operation.DISPLAY
        assert operation.x == 0x0
        assert operation.y == 0x1
        assert operation.n == 0xF

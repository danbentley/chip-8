import pytest

from chip8.cpu import Registers, InvalidRegisterError


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

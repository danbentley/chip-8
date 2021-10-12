import pytest

from chip8.memory import Memory, InvalidMemoryAddressError


@pytest.fixture
def memory():
    return Memory()


class TestMemory:
    def test_set(self, memory):
        memory[0b0] = 0b00001111
        assert memory[0b0] == 0b00001111

    def test_set_invalid_address(self, memory):
        with pytest.raises(InvalidMemoryAddressError):
            memory[0b1000000000001] = 0b00001111

    def test_get_invalid_address(self, memory):
        with pytest.raises(InvalidMemoryAddressError):
            memory[0b1000000000001]

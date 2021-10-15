import pytest

from chip8.cpu import (
    Registers,
    InvalidRegisterError,
    Operation,
    CPU,
    UnhandledOperationError,
)
from chip8.display import Display
from chip8.memory import Memory


@pytest.fixture
def memory(request):
    rom = request.param
    memory = Memory()
    for instruction, location in zip(rom, range(0x200, 0xFFF)):
        memory[location] = instruction
    return memory


@pytest.fixture
def registers(request):
    registers = Registers()
    try:
        registers[request.param[0]] = request.param[1]
    except AttributeError:
        ...
    return registers


@pytest.fixture
def cpu(memory, display, registers):
    return CPU(memory, display, registers)


class TestRegisters:
    def test_set(self, registers):
        registers[0x0] = 0b00001111
        assert registers[0x0] == 0b00001111

    def test_set_invalid_register(self, registers):
        with pytest.raises(InvalidRegisterError):
            registers["invalid"] = 0b00001111

    def test_access_invalid_register(self, registers):
        with pytest.raises(InvalidRegisterError):
            registers["invalid"]

    def test_direct_access_get(self, registers):
        registers[0x0] = 0b00001111
        assert registers.V0 == 0b00001111

    def test_direct_access_set(self, registers):
        registers.V0 = 0b00001111
        assert registers[0x0] == 0b00001111

    def test_non_numeric_hex_value_set(self, registers):
        registers[0xA] = 0b00001111
        assert registers.VA == 0b00001111

    def test_non_numeric_hex_value_get(self, registers):
        registers.VA = 0b00001111
        assert registers[0xA] == 0b00001111


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

    def test_skip_if_vx_and_nn_are_equal(self):
        opcode = 0x362B

        operation = Operation.decode(opcode)

        assert operation.nibble == Operation.SKIP_IF_VX_AND_NN_ARE_EQUAL
        assert operation.nn == 0x2B
        assert operation.x == 0x6

    def test_skip_if_vx_and_nn_are_not_equal(self):
        opcode = 0x452A

        operation = Operation.decode(opcode)

        assert operation.nibble == Operation.SKIP_IF_VX_AND_NN_ARE_NOT_EQUAL
        assert operation.nn == 0x2A
        assert operation.x == 0x5

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


@pytest.fixture
def display(monkeypatch):
    def mock_draw_sprite(*aargs, **kwargs):
        mock_draw_sprite.called = True
        return mock_clear.called

    mock_draw_sprite.called = False

    def mock_clear(self, *aargs, **kwargs):
        mock_clear.called = True
        return mock_clear.called

    mock_clear.called = False

    monkeypatch.setattr(Display, "draw_sprite", mock_draw_sprite)
    monkeypatch.setattr(Display, "clear", mock_clear)

    return Display(width=64, height=45, scale=4)


class TestCPUExecute:
    @pytest.mark.parametrize("memory", [[0xF0, 0x1F]], indirect=True)
    def test_raises_unhandled_operation(self, cpu):
        with pytest.raises(UnhandledOperationError):
            cpu.cycle()

    @pytest.mark.parametrize("memory", [[0x0, 0xE0]], indirect=True)
    def test_clear_screen(self, cpu):
        cpu.cycle()

        assert cpu.display.clear.called is True

    @pytest.mark.parametrize("memory", [[0x12, 0x28]], indirect=True)
    def test_jump(self, cpu):
        cpu.cycle()

        assert cpu.program_counter == 0x228

    @pytest.mark.parametrize("memory", [[0x36, 0x2B]], indirect=True)
    @pytest.mark.parametrize("registers", [(0x6, 0x2B)], indirect=True)
    def test_skip_if_vx_and_nn_are_equal_true(self, cpu):
        cpu.cycle()

        assert cpu.program_counter == 0x204

    @pytest.mark.parametrize("memory", [[0x36, 0x2B]], indirect=True)
    @pytest.mark.parametrize("registers", [(0x6, 0x0)], indirect=True)
    def test_skip_if_vx_and_nn_are_equal_false(self, cpu):
        cpu.cycle()

        assert cpu.program_counter == 0x202

    @pytest.mark.parametrize("memory", [[0x45, 0x2A]], indirect=True)
    @pytest.mark.parametrize("registers", [(0x6, 0x0)], indirect=True)
    def test_skip_if_vx_and_nn_are_not_equal_true(self, cpu):
        cpu.cycle()

        assert cpu.program_counter == 0x204

    @pytest.mark.parametrize("memory", [[0x45, 0x2A]], indirect=True)
    @pytest.mark.parametrize("registers", [(0x5, 0x2A)], indirect=True)
    def test_skip_if_vx_and_nn_are_not_equal_false(self, cpu):
        cpu.cycle()

        assert cpu.program_counter == 0x202

    @pytest.mark.parametrize("memory", [[0x60, 0x0C]], indirect=True)
    def test_set_register(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x0] == 0xC

    @pytest.mark.parametrize("memory", [[0x70, 0x09]], indirect=True)
    def test_add(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x0] == 0x9

    @pytest.mark.parametrize("memory", [[0xA2, 0x2A]], indirect=True)
    def test_set_index(self, cpu):
        cpu.cycle()

        assert cpu.index == 0x22A

    @pytest.mark.parametrize("memory", [[0xD0, 0x1F]], indirect=True)
    def test_display(self, cpu):
        cpu.cycle()

        assert cpu.display.draw_sprite.called is True

from ctypes import c_uint8
import pytest

from chip8.cpu import (
    Registers,
    InvalidRegisterError,
    Operation,
    OperationType,
    CPU,
    UnhandledOperationError,
    FONT_ADDRESS_START,
)
from chip8.fonts import Font
from chip8.memory import Memory


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
        opcode = 0x0E0

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.CLEAR_SCREEN

    def test_return(self):
        opcode = 0x0EE

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.RETURN

    def test_jump(self):
        opcode = 0x1228

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.JUMP

    def test_call(self):
        opcode = 0x2428

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.CALL

    def test_skip_if_vx_and_nn_are_equal(self):
        opcode = 0x362B

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SKIP_IF_VX_AND_NN_ARE_EQUAL

    def test_skip_if_vx_and_nn_are_not_equal(self):
        opcode = 0x452A

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SKIP_IF_VX_AND_NN_ARE_NOT_EQUAL

    def test_skip_if_vx_and_vy_are_equal(self):
        opcode = 0x5420

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SKIP_IF_VX_AND_VY_ARE_EQUAL

    def test_set_register(self):
        opcode = 0x600C

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SET_REGISTER

    def test_add(self):
        opcode = 0x7009

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.ADD

    def test_set_vx(self):
        opcode = 0x8560

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SET_VX

    def test_set_vx_to_vx_or_vy(self):
        opcode = 0x8561

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SET_VX_TO_VX_OR_VY

    def test_set_vx_to_vx_and_vy(self):
        opcode = 0x8562

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SET_VX_TO_VX_AND_VY

    def test_set_vx_to_vx_xor_vy(self):
        opcode = 0x8563

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SET_VX_TO_VX_XOR_VY

    def test_set_vx_to_vx_add_vy(self):
        opcode = 0x8564

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SET_VX_TO_VX_ADD_VY

    def test_set_vx_to_vx_sub_vx(self):
        opcode = 0x8565

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SET_VX_TO_VX_SUB_VY

    def test_shift_vx_right(self):
        opcode = 0x8566

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SHIFT_VX_RIGHT

    def test_set_vx_to_vy_sub_vx(self):
        opcode = 0x8567

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SET_VX_TO_VY_SUB_VX

    def test_shift_vx_left(self):
        opcode = 0x856E

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SHIFT_VX_LEFT

    def test_skip_if_vx_and_vy_are_not_equal(self):
        opcode = 0x9560

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SKIP_IF_VX_AND_VY_ARE_NOT_EQUAL

    def test_set_index(self):
        opcode = 0xA22A

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SET_INDEX

    def test_random(self):
        opcode = 0xC22A

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.RANDOM

    def test_display(self):
        opcode = 0xD01F

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.DISPLAY

    def test_skip_if_vx_and_keycode_are_equal(self):
        opcode = 0xE59E

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SKIP_IF_VX_AND_KEYCODE_ARE_EQUAL

    def test_skip_if_vx_and_keycode_are_not_equal(self):
        opcode = 0xE5A1

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SKIP_IF_VX_AND_KEYCODE_ARE_NOT_EQUAL

    def test_wait_for_key_press(self):
        opcode = 0xF50A

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.WAIT_FOR_KEY_PRESS

    def test_set_delay_timer_to_vx(self):
        opcode = 0xF515

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SET_DELAY_TIMER_TO_VX

    def test_set_sound_timer_to_vx(self):
        opcode = 0xF518

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SET_SOUND_TIMER_TO_VX

    def test_set_vx_to_delay_timer(self):
        opcode = 0xF507

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.SET_VX_TO_DELAY_TIMER

    def test_add_vx_to_index(self):
        opcode = 0xF51E

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.ADD_VX_TO_INDEX

    def test_font(self):
        opcode = 0xF329

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.FONT

    def test_binary_coded_decimal(self):
        opcode = 0xF233

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.STORE_BINARY_CODED_DECIMAL

    def test_load_registers(self):
        opcode = 0xF355

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.LOAD_REGISTERS

    def test_store_registers(self):
        opcode = 0xF365

        operation = Operation.decode(opcode)

        assert operation.type == OperationType.STORE_REGISTERS


class TestCPUExecute:
    @pytest.mark.parametrize("memory", [[0xF0, 0x1F]], indirect=True)
    def test_raises_unhandled_operation(self, cpu):
        with pytest.raises(UnhandledOperationError):
            cpu.cycle()

    @pytest.mark.parametrize("memory", [[0x0, 0xE0]], indirect=True)
    def test_clear_screen(self, cpu):
        cpu.cycle()

        assert cpu.display.clear_called is True

    # fmt: off
    @pytest.mark.parametrize(
        "memory", [[
                0x22, 0x02, # Operation.CALL to populate stack, call jumps to next item in memory
                0x22, 0x04, # Operation.CALL to populate stack, call jumps to next item in memory
                0x00, 0xEE, # Operation.RETURN to set the PC to the first address
        ]], indirect=True,
    )
    # fmt: on
    def test_return(self, cpu):
        cpu.cycle()
        cpu.cycle()
        cpu.cycle()

        assert cpu.stack_pointer == 0x1
        assert [0x202, 0x204] == list(cpu.stack.values())
        assert cpu.program_counter == 0x204

    @pytest.mark.parametrize("memory", [[0x12, 0x28]], indirect=True)
    def test_jump(self, cpu):
        cpu.cycle()

        assert cpu.program_counter == 0x228

    @pytest.mark.parametrize("memory", [[0x24, 0x28]], indirect=True)
    def test_call(self, cpu):
        cpu.cycle()

        assert cpu.stack_pointer == 0x1
        assert 0x202 in cpu.stack.values()
        assert cpu.program_counter == 0x428

    @pytest.mark.parametrize("memory", [[0x36, 0x2B]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x6, 0x2B)]], indirect=True)
    def test_skip_if_vx_and_nn_are_equal_true(self, cpu):
        cpu.cycle()

        assert cpu.program_counter == 0x204

    @pytest.mark.parametrize("memory", [[0x36, 0x2B]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x6, 0x0)]], indirect=True)
    def test_skip_if_vx_and_nn_are_equal_false(self, cpu):
        cpu.cycle()

        assert cpu.program_counter == 0x202

    @pytest.mark.parametrize("memory", [[0x45, 0x2A]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x6, 0x0)]], indirect=True)
    def test_skip_if_vx_and_nn_are_not_equal_true(self, cpu):
        cpu.cycle()

        assert cpu.program_counter == 0x204

    @pytest.mark.parametrize("memory", [[0x45, 0x2A]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x5, 0x2A)]], indirect=True)
    def test_skip_if_vx_and_nn_are_not_equal_false(self, cpu):
        cpu.cycle()

        assert cpu.program_counter == 0x202

    @pytest.mark.parametrize("memory", [[0x54, 0x20]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x4, 0x1), (0x2, 0x1)]], indirect=True)
    def test_skip_if_vx_and_vy_are_equal_true(self, cpu):
        cpu.cycle()

        assert cpu.program_counter == 0x204

    @pytest.mark.parametrize("memory", [[0x54, 0x20]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x4, 0x1), (0x2, 0x0)]], indirect=True)
    def test_skip_if_vx_and_vy_are_equal_false(self, cpu):
        cpu.cycle()

        assert cpu.program_counter == 0x202

    @pytest.mark.parametrize("memory", [[0x60, 0x0C]], indirect=True)
    def test_set_register(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x0].value == c_uint8(0xC).value

    @pytest.mark.parametrize("memory", [[0x70, 0x09]], indirect=True)
    def test_add(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x0].value == c_uint8(0x9).value

    @pytest.mark.parametrize("memory", [[0x85, 0x60]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x5, 0x1), (0x6, 0x0)]], indirect=True)
    def test_set_vx(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x5] == cpu.registers[0x6]

    @pytest.mark.parametrize("memory", [[0x85, 0x61]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x5, 0x1), (0x6, 0x0)]], indirect=True)
    def test_set_vx_to_vx_or_vy(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x5].value == c_uint8(0x1).value

    @pytest.mark.parametrize("memory", [[0x85, 0x62]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x5, 0x1), (0x6, 0x0)]], indirect=True)
    def test_set_vx_to_vx_and_vy(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x5].value == c_uint8(0x0).value

    @pytest.mark.parametrize("memory", [[0x85, 0x63]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x5, 0x1), (0x6, 0x0)]], indirect=True)
    def test_set_vx_to_vx_xor_vy(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x5].value == c_uint8(0x1).value

    @pytest.mark.parametrize("memory", [[0x85, 0x64]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x5, 0xFF), (0x6, 0x1)]], indirect=True)
    def test_set_vx_to_vx_add_vy_true(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x5].value == c_uint8(0x0).value
        assert cpu.registers[0xF].value == c_uint8(1).value

    @pytest.mark.parametrize("memory", [[0x85, 0x64]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x5, 0x0), (0x6, 0x1)]], indirect=True)
    def test_set_vx_to_vx_add_vy_false(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x5].value == c_uint8(0x1).value
        assert cpu.registers[0xF].value == c_uint8(0).value

    @pytest.mark.parametrize("memory", [[0x85, 0x65]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x5, 0xFF), (0x6, 0x1)]], indirect=True)
    def test_set_vx_to_vx_sub_vy_true(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x5].value == c_uint8(0xFE).value
        assert cpu.registers[0xF].value == c_uint8(1).value

    @pytest.mark.parametrize("memory", [[0x85, 0x65]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x5, 0x1), (0x6, 0xFF)]], indirect=True)
    def test_set_vx_to_vx_sub_vy_false(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x5].value == c_uint8(0x2).value
        assert cpu.registers[0xF].value == c_uint8(0).value

    @pytest.mark.parametrize("memory", [[0x85, 0x66]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x5, 0x1), (0x6, 0x3)]], indirect=True)
    def test_shift_vx_right_with_odd_number(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x5].value == c_uint8(0x1).value
        assert cpu.registers[0xF].value == c_uint8(1).value

    @pytest.mark.parametrize("memory", [[0x85, 0x66]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x5, 0x2), (0x6, 0x2)]], indirect=True)
    def test_shift_vx_right_with_event_number(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x5].value == c_uint8(0x1).value
        assert cpu.registers[0xF].value == c_uint8(0).value

    @pytest.mark.parametrize("memory", [[0x85, 0x67]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x5, 0x1), (0x6, 0xFF)]], indirect=True)
    def test_set_vx_to_vy_sub_vx_true(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x5].value == c_uint8(0xFE).value
        assert cpu.registers[0xF].value == c_uint8(1).value

    @pytest.mark.parametrize("memory", [[0x85, 0x67]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x5, 0xFF), (0x6, 0x1)]], indirect=True)
    def test_set_vx_to_vy_sub_vx_false(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x5].value == c_uint8(0x2).value
        assert cpu.registers[0xF].value == c_uint8(0).value

    @pytest.mark.parametrize("memory", [[0x85, 0x6E]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x5, 0xFF), (0x6, 0x3)]], indirect=True)
    def test_shift_vx_left_with_most_significant_bit_set(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x5].value == c_uint8(0x6).value
        assert cpu.registers[0xF].value == c_uint8(1).value

    @pytest.mark.parametrize("memory", [[0x85, 0x6E]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x5, 0x1), (0x6, 0x2)]], indirect=True)
    def test_shift_vx_left_with_most_significant_bit_not_set(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x5].value == c_uint8(0x4).value
        assert cpu.registers[0xF].value == c_uint8(0).value

    @pytest.mark.parametrize("memory", [[0x95, 0x60]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x5, 0x1), (0x6, 0x0)]], indirect=True)
    def test_skip_if_vx_and_vy_are_not_equal_true(self, cpu):
        cpu.cycle()

        assert cpu.program_counter == 0x204

    @pytest.mark.parametrize("memory", [[0x95, 0x60]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x5, 0x1), (0x6, 0x1)]], indirect=True)
    def test_skip_if_vx_and_vy_are_not_equal_false(self, cpu):
        cpu.cycle()

        assert cpu.program_counter == 0x202

    @pytest.mark.parametrize("memory", [[0xA2, 0x2A]], indirect=True)
    def test_set_index(self, cpu):
        cpu.cycle()

        assert cpu.index == 0x22A

    @pytest.mark.parametrize("memory", [[0xC2, 0x2A]], indirect=True)
    def test_random(self, cpu):
        cpu.cycle()

        assert cpu.registers != 0x0

    @pytest.mark.parametrize("memory", [[0xD0, 0x1F]], indirect=True)
    def test_display(self, cpu):
        cpu.cycle()

        assert cpu.display.draw_sprite_called is True
        assert cpu.registers[0xF].value == 0x0

    @pytest.mark.parametrize("memory", [[0xE3, 0x9E]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x3, 0x5)]], indirect=True)
    def test_skip_if_vx_and_keycode_are_equal_true(self, cpu):
        cpu.keycode = 0x5

        cpu.cycle()

        assert cpu.program_counter == 0x204

    @pytest.mark.parametrize("memory", [[0xE3, 0x9E]], indirect=True)
    def test_skip_if_vx_and_keycode_are_equal_false(self, cpu):
        cpu.cycle()

        assert cpu.program_counter == 0x202

    @pytest.mark.parametrize("memory", [[0xE3, 0xA1]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x3, 0x5)]], indirect=True)
    def test_skip_if_vx_and_keycode_are_not_equal_true(self, cpu):
        cpu.keycode = 0x5

        cpu.cycle()

        assert cpu.program_counter == 0x202

    @pytest.mark.parametrize("memory", [[0xE3, 0xA1]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x3, 0x5)]], indirect=True)
    def test_skip_if_vx_and_keycode_are_not_equal_false(self, cpu):
        cpu.keycode = 0x0

        cpu.cycle()

        assert cpu.program_counter == 0x204

    @pytest.mark.parametrize("memory", [[0xF5, 0x0A]], indirect=True)
    def test_wait_for_key_press_true(self, cpu):
        cpu.keycode = 0x01

        cpu.cycle()

        assert cpu.registers[0x5].value == 0x01
        assert cpu.program_counter == 0x204

    @pytest.mark.parametrize("memory", [[0xF5, 0x0A]], indirect=True)
    def test_wait_for_key_press_false(self, cpu):
        cpu.cycle()

        # If no key is pressed, program_counter shouldn't change
        assert cpu.program_counter == 0x202

    @pytest.mark.parametrize("registers", [[(0x3, 0x5)]], indirect=True)
    @pytest.mark.parametrize("memory", [[0xF3, 0x15]], indirect=True)
    def test_set_delay_timer_to_vx(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x3].value == 5
        # delay timer is decreased after being set
        assert cpu.delay_timer.value == 4

    @pytest.mark.parametrize("registers", [[(0x3, 0x5)]], indirect=True)
    @pytest.mark.parametrize("memory", [[0xF3, 0x18]], indirect=True)
    def test_set_sound_timer_to_vx(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x3].value == 5
        # sound timer is decreased after being set
        assert cpu.sound_timer.value == 4

    @pytest.mark.parametrize("memory", [[0xF5, 0x07]], indirect=True)
    def test_set_vx_to_delay_timer(self, cpu):
        cpu.cycle()

        assert cpu.registers[0x5].value == cpu.delay_timer.value

    @pytest.mark.parametrize("memory", [[0xF3, 0x1E]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x3, 0x1)]], indirect=True)
    def test_add_vx_to_index(self, cpu):
        cpu.index = 0x5

        cpu.cycle()

        assert cpu.index == 6

    @pytest.mark.parametrize("memory", [[0xF3, 0x29]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x3, 0x1), (0x6, 0x1)]], indirect=True)
    def test_font(self, cpu):
        cpu.memory[FONT_ADDRESS_START : FONT_ADDRESS_START + 5] = Font.ONE.value

        cpu.cycle()

        assert cpu.index == FONT_ADDRESS_START

    @pytest.mark.parametrize("memory", [[0xF3, 0x33]], indirect=True)
    @pytest.mark.parametrize("registers", [[(0x3, 0xFD)]], indirect=True)
    def test_binary_coded_decimal(self, cpu):
        cpu.index = 0x0

        cpu.cycle()

        assert cpu.memory[0x0] == 2
        assert cpu.memory[0x1] == 5
        assert cpu.memory[0x2] == 3

    @pytest.mark.parametrize("memory", [[0xF3, 0x55]], indirect=True)
    @pytest.mark.parametrize(
        "registers", [[(0x0, 0x9), (0x1, 0x8), (0x2, 0x7), (0x3, 0x6)]], indirect=True
    )
    def test_load_registers(self, cpu):

        cpu.index = 0x0

        cpu.cycle()

        assert cpu.memory[0x0] == 0x9
        assert cpu.memory[0x1] == 0x8
        assert cpu.memory[0x2] == 0x7
        assert cpu.memory[0x3] == 0x6
        assert cpu.memory[0x4] == 0x0

    @pytest.mark.parametrize("memory", [[0xF3, 0x65]], indirect=True)
    def test_store_registers(self, cpu):

        cpu.index = 0x0
        cpu.memory[0x0] = 0x9
        cpu.memory[0x1] = 0x8
        cpu.memory[0x2] = 0x7
        cpu.memory[0x3] = 0x6

        cpu.cycle()

        assert cpu.registers[0x0].value == 0x9
        assert cpu.registers[0x1].value == 0x8
        assert cpu.registers[0x2].value == 0x7
        assert cpu.registers[0x3].value == 0x6
        assert cpu.registers[0x4].value == 0x0

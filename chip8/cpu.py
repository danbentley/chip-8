from ctypes import c_uint8

from collections import deque

from dataclasses import dataclass

from chip8.fonts import Font


FONT_ADDRESS_START = 0x050
FONT_ADDRESS_END = 0x0A0


class InvalidRegisterError(Exception):
    ...


class Registers:
    """Class managing Chip-8's 16 general purpose regisers.

    Referenced as Vx where x is a hex number. Registers are accessed using
    subscription, passing the register's hex number. Stored values should be
    one byte in length.

    VF is used by the intepretor as a flag.
    """

    V0: c_uint8 = c_uint8(0b0)
    V1: c_uint8 = c_uint8(0b0)
    V2: c_uint8 = c_uint8(0b0)
    V3: c_uint8 = c_uint8(0b0)
    V4: c_uint8 = c_uint8(0b0)
    V5: c_uint8 = c_uint8(0b0)
    V6: c_uint8 = c_uint8(0b0)
    V7: c_uint8 = c_uint8(0b0)
    V8: c_uint8 = c_uint8(0b0)
    V9: c_uint8 = c_uint8(0b0)
    VA: c_uint8 = c_uint8(0b0)
    VB: c_uint8 = c_uint8(0b0)
    VC: c_uint8 = c_uint8(0b0)
    VD: c_uint8 = c_uint8(0b0)
    VE: c_uint8 = c_uint8(0b0)
    VF: c_uint8 = c_uint8(0b0)

    def __getitem__(self, index: int) -> c_uint8:
        try:
            return getattr(self, f"V{index:X}")
        except (AttributeError, ValueError) as e:
            raise InvalidRegisterError(f"Attempt to get value from {index}") from e

    def __setitem__(self, index: int, value: c_uint8):
        try:
            setattr(self, f"V{index:X}", value)
        except (AttributeError, ValueError) as e:
            raise InvalidRegisterError(f"Attempt to set value in {index}") from e


@dataclass(frozen=True)
class Operation:
    CLEAR_SCREEN = (0x0, 0xE0)
    RETURN = (0x0, 0xEE)
    JUMP = 0x1
    CALL = 0x2
    SKIP_IF_VX_AND_NN_ARE_EQUAL = 0x3
    SKIP_IF_VX_AND_NN_ARE_NOT_EQUAL = 0x4
    SKIP_IF_VX_AND_VY_ARE_EQUAL = 0x5
    SET_REGISTER = 0x6
    ADD = 0x7
    SET_VX = (0x8, 0x0)
    SET_VX_TO_VX_OR_VY = (0x8, 0x1)
    SET_VX_TO_VX_AND_VY = (0x8, 0x2)
    SET_VX_TO_VX_XOR_VY = (0x8, 0x3)
    SET_VX_TO_VX_ADD_VY = (0x8, 0x4)
    SET_VX_TO_VX_SUB_VY = (0x8, 0x5)
    SHIFT_VX_RIGHT = (0x8, 0x6)
    SET_VX_TO_VY_SUB_VX = (0x8, 0x7)
    SHIFT_VX_LEFT = (0x8, 0xE)
    SKIP_IF_VX_AND_VY_ARE_NOT_EQUAL = 0x9
    SET_INDEX = 0xA
    DISPLAY = 0xD
    SET_DELAY_TIMER_TO_VX = (0xF, 0x15)
    SET_VX_TO_DELAY_TIMER = (0xF, 0x07)
    FONT = (0xF, 0x29)
    STORE_BINARY_CODED_DECIMAL = (0xF, 0x33)
    LOAD_REGISTERS = (0xF, 0x55)
    STORE_REGISTERS = (0xF, 0x65)

    x: int
    y: int
    nibble: int
    high: int
    low: int
    n: int
    nn: c_uint8
    nnn: int
    opcode: int

    @classmethod
    def decode(cls, opcode):
        high, low = opcode >> 8, opcode & 0x0F0

        nibble = high >> 4
        y = low >> 4
        x = high & 0xF
        n = opcode & 0x0F
        nn = c_uint8(opcode & 0x0FF)
        nnn = opcode & 0x0FFF

        return cls(
            x=x,
            y=y,
            nibble=nibble,
            high=high,
            low=low,
            n=n,
            nn=nn,
            nnn=nnn,
            opcode=opcode,
        )


class UnhandledOperationError(Exception):
    def __init__(self, *args, operation=None):
        super().__init__(*args)
        self.operation = operation


class CPU:
    program_counter = 0x200
    index = 0
    stack = deque()

    def __init__(self, memory, display, registers):
        self.memory = memory
        self.display = display
        self.registers = registers
        self.stack_pointer = 0x0
        self.delay_timer = c_uint8(0x0)

    def fetch(self):
        instruction = self.memory[self.program_counter]
        self.program_counter += 1
        instruction2 = self.memory[self.program_counter]
        self.program_counter += 1

        return instruction << 8 | instruction2

    def decode(self, opcode):
        return Operation.decode(opcode)

    def execute(self, operation):
        if (
            operation.nibble == Operation.CLEAR_SCREEN[0]
            and operation.nn.value == Operation.CLEAR_SCREEN[1]
        ):
            self.display.clear()
        elif (
            operation.nibble == Operation.RETURN[0]
            and operation.nn.value == Operation.RETURN[1]
        ):
            self.program_counter = self.stack.popleft()
            self.stack_pointer -= 1
        elif operation.nibble == Operation.JUMP:
            self.program_counter = operation.nnn
        elif operation.nibble == Operation.CALL:
            self.stack_pointer += 1
            self.stack.append(self.program_counter)
            self.program_counter = operation.nnn
        elif operation.nibble == Operation.SKIP_IF_VX_AND_NN_ARE_EQUAL:
            if self.registers[operation.x].value == operation.nn.value:
                self.program_counter += 2
        elif operation.nibble == Operation.SKIP_IF_VX_AND_NN_ARE_NOT_EQUAL:
            if self.registers[operation.x].value != operation.nn.value:
                self.program_counter += 2
        elif operation.nibble == Operation.SKIP_IF_VX_AND_VY_ARE_EQUAL:
            if self.registers[operation.x].value == self.registers[operation.y].value:
                self.program_counter += 2
        elif operation.nibble == Operation.SET_REGISTER:
            self.registers[operation.x] = operation.nn
        elif operation.nibble == Operation.ADD:
            self.registers[operation.x] = c_uint8(
                self.registers[operation.x].value + operation.nn.value
            )
        elif (
            operation.nibble == Operation.SET_VX[0]
            and operation.n == Operation.SET_VX[1]
        ):
            self.registers[operation.x] = self.registers[operation.y]
        elif (
            operation.nibble == Operation.SET_VX_TO_VX_OR_VY[0]
            and operation.n == Operation.SET_VX_TO_VX_OR_VY[1]
        ):
            self.registers[operation.x] = c_uint8(
                self.registers[operation.x].value | self.registers[operation.y].value
            )
        elif (
            operation.nibble == Operation.SET_VX_TO_VX_AND_VY[0]
            and operation.n == Operation.SET_VX_TO_VX_AND_VY[1]
        ):
            self.registers[operation.x] = c_uint8(
                self.registers[operation.x].value & self.registers[operation.y].value
            )
        elif (
            operation.nibble == Operation.SET_VX_TO_VX_XOR_VY[0]
            and operation.n == Operation.SET_VX_TO_VX_XOR_VY[1]
        ):
            self.registers[operation.x] = c_uint8(
                self.registers[operation.x].value ^ self.registers[operation.y].value
            )
        elif (
            operation.nibble == Operation.SET_VX_TO_VX_ADD_VY[0]
            and operation.n == Operation.SET_VX_TO_VX_ADD_VY[1]
        ):
            total = (
                self.registers[operation.x].value + self.registers[operation.y].value
            )
            self.registers[operation.x] = c_uint8(total)
            if total >= 255:
                self.registers[0xF] = c_uint8(1)
            else:
                self.registers[0xF] = c_uint8(0)
        elif (
            operation.nibble == Operation.SET_VX_TO_VX_SUB_VY[0]
            and operation.n == Operation.SET_VX_TO_VX_SUB_VY[1]
        ):

            if self.registers[operation.x].value > self.registers[operation.y].value:
                self.registers[0xF] = c_uint8(1)
            else:
                self.registers[0xF] = c_uint8(0)
            self.registers[operation.x] = c_uint8(
                self.registers[operation.x].value - self.registers[operation.y].value
            )
        elif (
            operation.nibble == Operation.SHIFT_VX_RIGHT[0]
            and operation.n == Operation.SHIFT_VX_RIGHT[1]
        ):
            self.registers[0xF] = c_uint8(self.registers[operation.x].value & 0x1)
            self.registers[operation.x] = c_uint8(
                self.registers[operation.y].value >> 1
            )
        elif (
            operation.nibble == Operation.SET_VX_TO_VY_SUB_VX[0]
            and operation.n == Operation.SET_VX_TO_VY_SUB_VX[1]
        ):
            if self.registers[operation.y].value > self.registers[operation.x].value:
                self.registers[0xF] = c_uint8(1)
            else:
                self.registers[0xF] = c_uint8(0)
            self.registers[operation.x] = c_uint8(
                self.registers[operation.y].value - self.registers[operation.x].value
            )
        elif (
            operation.nibble == Operation.SHIFT_VX_LEFT[0]
            and operation.n == Operation.SHIFT_VX_LEFT[1]
        ):
            self.registers[0xF] = c_uint8(self.registers[operation.x].value >> 7 & 1)
            self.registers[operation.x] = c_uint8(
                self.registers[operation.y].value << 1
            )
        elif operation.nibble == Operation.SKIP_IF_VX_AND_VY_ARE_NOT_EQUAL:
            if self.registers[operation.x].value != self.registers[operation.y].value:
                self.program_counter += 2
        elif operation.nibble == Operation.SET_INDEX:
            self.index = operation.nnn
        elif operation.nibble == Operation.DISPLAY:
            sprite = [
                self.memory[i] for i in range(self.index, self.index + operation.n)
            ]
            self.display.draw_sprite(
                sprite,
                self.registers[operation.x].value,
                self.registers[operation.y].value,
            )
        elif (
            operation.nibble == Operation.SET_DELAY_TIMER_TO_VX[0]
            and operation.nn.value == Operation.SET_DELAY_TIMER_TO_VX[1]
        ):
            self.delay_timer = self.registers[operation.x]
        elif (
            operation.nibble == Operation.SET_VX_TO_DELAY_TIMER[0]
            and operation.nn.value == Operation.SET_VX_TO_DELAY_TIMER[1]
        ):
            self.registers[operation.x] = self.delay_timer
        elif (
            operation.nibble == Operation.FONT[0]
            and operation.nn.value == Operation.FONT[1]
        ):
            character = self.registers[operation.x].value
            sprite = Font.mapping_for_character(character)
            self.index = next(
                location
                for location in range(FONT_ADDRESS_START, FONT_ADDRESS_END, 5)
                if self.memory[location : location + 5] == sprite
            )
        elif (
            operation.nibble == Operation.STORE_BINARY_CODED_DECIMAL[0]
            and operation.nn.value == Operation.STORE_BINARY_CODED_DECIMAL[1]
        ):
            value = self.registers[operation.x].value
            self.memory[self.index : self.index + 3] = [
                c_uint8(int(i)) for i in str(value)
            ]
        elif (
            operation.nibble == Operation.LOAD_REGISTERS[0]
            and operation.nn.value == Operation.LOAD_REGISTERS[1]
        ):
            for i in range(0x0, operation.x + 1):
                self.memory[self.index + i] = self.registers[i]
            self.index = self.index + operation.x
        elif (
            operation.nibble == Operation.STORE_REGISTERS[0]
            and operation.nn.value == Operation.STORE_REGISTERS[1]
        ):
            for i in range(0x0, operation.x + 1):
                self.registers[i] = self.memory[self.index + i]
            self.index = self.index + operation.x
        else:
            raise UnhandledOperationError(
                f"Unhandled operation for opcode: {hex(operation.opcode)}",
                operation=operation,
            )

    def cycle(self):
        self.delay_timer = c_uint8(self.delay_timer.value - 1)

        opcode = self.fetch()
        operation = self.decode(opcode)
        self.execute(operation)

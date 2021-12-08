from ctypes import c_uint8
from random import random
from typing import Optional
import enum
import math

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


class OperationType(enum.Enum):
    CLEAR_SCREEN = enum.auto()
    RETURN = enum.auto()
    JUMP = enum.auto()
    CALL = enum.auto()
    SKIP_IF_VX_AND_NN_ARE_EQUAL = enum.auto()
    SKIP_IF_VX_AND_NN_ARE_NOT_EQUAL = enum.auto()
    SKIP_IF_VX_AND_VY_ARE_EQUAL = enum.auto()
    SET_REGISTER = enum.auto()
    ADD = enum.auto()
    SET_VX = enum.auto()
    SET_VX_TO_VX_OR_VY = enum.auto()
    SET_VX_TO_VX_AND_VY = enum.auto()
    SET_VX_TO_VX_XOR_VY = enum.auto()
    SET_VX_TO_VX_ADD_VY = enum.auto()
    SET_VX_TO_VX_SUB_VY = enum.auto()
    SHIFT_VX_RIGHT = enum.auto()
    SET_VX_TO_VY_SUB_VX = enum.auto()
    SHIFT_VX_LEFT = enum.auto()
    SKIP_IF_VX_AND_VY_ARE_NOT_EQUAL = enum.auto()
    SET_INDEX = enum.auto()
    RANDOM = enum.auto()
    DISPLAY = enum.auto()
    SKIP_IF_VX_AND_KEYCODE_ARE_EQUAL = enum.auto()
    SKIP_IF_VX_AND_KEYCODE_ARE_NOT_EQUAL = enum.auto()
    SET_DELAY_TIMER_TO_VX = enum.auto()
    SET_SOUND_TIMER_TO_VX = enum.auto()
    SET_VX_TO_DELAY_TIMER = enum.auto()
    ADD_VX_TO_INDEX = enum.auto()
    FONT = enum.auto()
    STORE_BINARY_CODED_DECIMAL = enum.auto()
    LOAD_REGISTERS = enum.auto()
    STORE_REGISTERS = enum.auto()


@dataclass(frozen=True)
class OperationMatchRule:
    type: OperationType

    nibble: int

    n: Optional[int] = None
    nn: Optional[int] = None

    def match(self, operation) -> bool:

        if self.nibble != operation.nibble:
            return False

        if self.n is not None and self.n != operation.n:
            return False

        if self.nn is not None and self.nn != operation.nn.value:
            return False

        return True


# fmt: off
rules = [
    OperationMatchRule(nibble=0x0, nn=0xE0, type=OperationType.CLEAR_SCREEN),
    OperationMatchRule(nibble=0x0, nn=0xEE, type=OperationType.RETURN),
    OperationMatchRule(nibble=0x1, type=OperationType.JUMP),
    OperationMatchRule(nibble=0x2, type=OperationType.CALL),
    OperationMatchRule(nibble=0x3, type=OperationType.SKIP_IF_VX_AND_NN_ARE_EQUAL),
    OperationMatchRule(nibble=0x4, type=OperationType.SKIP_IF_VX_AND_NN_ARE_NOT_EQUAL),
    OperationMatchRule(nibble=0x5, type=OperationType.SKIP_IF_VX_AND_VY_ARE_EQUAL),
    OperationMatchRule(nibble=0x6, type=OperationType.SET_REGISTER),
    OperationMatchRule(nibble=0x7, type=OperationType.ADD),
    OperationMatchRule(nibble=0x8, n=0x0, type=OperationType.SET_VX),
    OperationMatchRule(nibble=0x8, n=0x1, type=OperationType.SET_VX_TO_VX_OR_VY),
    OperationMatchRule(nibble=0x8, n=0x2, type=OperationType.SET_VX_TO_VX_AND_VY),
    OperationMatchRule(nibble=0x8, n=0x3, type=OperationType.SET_VX_TO_VX_XOR_VY),
    OperationMatchRule(nibble=0x8, n=0x4, type=OperationType.SET_VX_TO_VX_ADD_VY),
    OperationMatchRule(nibble=0x8, n=0x5, type=OperationType.SET_VX_TO_VX_SUB_VY),
    OperationMatchRule(nibble=0x8, n=0x6, type=OperationType.SHIFT_VX_RIGHT),
    OperationMatchRule(nibble=0x8, n=0x7, type=OperationType.SET_VX_TO_VY_SUB_VX),
    OperationMatchRule(nibble=0x8, n=0xE, type=OperationType.SHIFT_VX_LEFT),
    OperationMatchRule(nibble=0x9, type=OperationType.SKIP_IF_VX_AND_VY_ARE_NOT_EQUAL),
    OperationMatchRule(nibble=0xA, type=OperationType.SET_INDEX),
    OperationMatchRule(nibble=0xC, type=OperationType.RANDOM),
    OperationMatchRule(nibble=0xD, type=OperationType.DISPLAY),
    OperationMatchRule(nibble=0xE, nn=0x9E, type=OperationType.SKIP_IF_VX_AND_KEYCODE_ARE_EQUAL),
    OperationMatchRule(nibble=0xE, nn=0xA1, type=OperationType.SKIP_IF_VX_AND_KEYCODE_ARE_NOT_EQUAL),
    OperationMatchRule(nibble=0xF, nn=0x15, type=OperationType.SET_DELAY_TIMER_TO_VX),
    OperationMatchRule(nibble=0xF, nn=0x18, type=OperationType.SET_SOUND_TIMER_TO_VX),
    OperationMatchRule(nibble=0xF, nn=0x07, type=OperationType.SET_VX_TO_DELAY_TIMER),
    OperationMatchRule(nibble=0xF, nn=0x1E, type=OperationType.ADD_VX_TO_INDEX),
    OperationMatchRule(nibble=0xF, nn=0x29, type=OperationType.FONT),
    OperationMatchRule(nibble=0xF, nn=0x33, type=OperationType.STORE_BINARY_CODED_DECIMAL),
    OperationMatchRule(nibble=0xF, nn=0x55, type=OperationType.LOAD_REGISTERS),
    OperationMatchRule(nibble=0xF, nn=0x65, type=OperationType.STORE_REGISTERS),
]
# fmt: on


@dataclass(frozen=True)
class Operation:

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

    @property
    def type(self):
        try:
            rule = next(r for r in rules if r.match(self))
        except StopIteration as e:
            raise UnhandledOperationError(
                f"Unhandled operation for opcode: {hex(self.opcode)}",
                operation=self,
            ) from e

        return rule.type


class UnhandledOperationError(Exception):
    def __init__(self, *args, operation=None):
        super().__init__(*args)
        self.operation = operation


class CPU:
    def __init__(self, memory, display, registers):
        self.memory = memory
        self.display = display
        self.registers = registers
        self.stack_pointer = 0x0
        self.delay_timer = c_uint8(0x0)
        self.sound_timer = c_uint8(0x0)
        self.program_counter = 0x200
        self.index = 0
        self.stack = {}
        self.keycode = None

    def fetch(self):
        instruction = self.memory[self.program_counter]
        self.program_counter += 1
        instruction2 = self.memory[self.program_counter]
        self.program_counter += 1

        return instruction << 8 | instruction2

    def decode(self, opcode):
        return Operation.decode(opcode)

    def execute(self, operation):
        print(
            f"{operation.type} {self.index=} VX={self.registers[operation.x]} VY={self.registers[operation.y]} {self.program_counter=} {self.keycode=} {self.delay_timer=} {hex(operation.opcode)=}"
        )
        if operation.type == OperationType.CLEAR_SCREEN:
            self.display.clear()
        elif operation.type == OperationType.RETURN:
            self.program_counter = self.stack[self.stack_pointer]
            self.stack_pointer -= 1
        elif operation.type == OperationType.JUMP:
            self.program_counter = operation.nnn
        elif operation.type == OperationType.CALL:
            self.stack_pointer += 1
            self.stack[self.stack_pointer] = self.program_counter
            self.program_counter = operation.nnn
        elif operation.type == OperationType.SKIP_IF_VX_AND_NN_ARE_EQUAL:
            if self.registers[operation.x].value == operation.nn.value:
                self.program_counter += 2
        elif operation.type == OperationType.SKIP_IF_VX_AND_NN_ARE_NOT_EQUAL:
            if self.registers[operation.x].value != operation.nn.value:
                self.program_counter += 2
        elif operation.type == OperationType.SKIP_IF_VX_AND_VY_ARE_EQUAL:
            if self.registers[operation.x].value == self.registers[operation.y].value:
                self.program_counter += 2
        elif operation.type == OperationType.SET_REGISTER:
            self.registers[operation.x] = operation.nn
        elif operation.type == OperationType.ADD:
            self.registers[operation.x] = c_uint8(
                self.registers[operation.x].value + operation.nn.value
            )
        elif operation.type == OperationType.SET_VX:
            self.registers[operation.x] = self.registers[operation.y]
        elif operation.type == OperationType.SET_VX_TO_VX_OR_VY:
            self.registers[operation.x] = c_uint8(
                self.registers[operation.x].value | self.registers[operation.y].value
            )
        elif operation.type == OperationType.SET_VX_TO_VX_AND_VY:
            self.registers[operation.x] = c_uint8(
                self.registers[operation.x].value & self.registers[operation.y].value
            )
        elif operation.type == OperationType.SET_VX_TO_VX_XOR_VY:
            self.registers[operation.x] = c_uint8(
                self.registers[operation.x].value ^ self.registers[operation.y].value
            )
        elif operation.type == OperationType.SET_VX_TO_VX_ADD_VY:
            total = (
                self.registers[operation.x].value + self.registers[operation.y].value
            )
            self.registers[operation.x] = c_uint8(total)
            if total >= 255:
                self.registers[0xF] = c_uint8(1)
            else:
                self.registers[0xF] = c_uint8(0)
        elif operation.type == OperationType.SET_VX_TO_VX_SUB_VY:

            if self.registers[operation.x].value > self.registers[operation.y].value:
                self.registers[0xF] = c_uint8(1)
            else:
                self.registers[0xF] = c_uint8(0)
            self.registers[operation.x] = c_uint8(
                self.registers[operation.x].value - self.registers[operation.y].value
            )
        elif operation.type == OperationType.SHIFT_VX_RIGHT:
            self.registers[0xF] = c_uint8(self.registers[operation.x].value & 0x1)
            self.registers[operation.x] = c_uint8(
                self.registers[operation.y].value >> 1
            )
        elif operation.type == OperationType.SET_VX_TO_VY_SUB_VX:
            if self.registers[operation.y].value > self.registers[operation.x].value:
                self.registers[0xF] = c_uint8(1)
            else:
                self.registers[0xF] = c_uint8(0)
            self.registers[operation.x] = c_uint8(
                self.registers[operation.y].value - self.registers[operation.x].value
            )
        elif operation.type == OperationType.SHIFT_VX_LEFT:
            self.registers[0xF] = c_uint8(self.registers[operation.x].value >> 7 & 1)
            self.registers[operation.x] = c_uint8(
                self.registers[operation.y].value << 1
            )
        elif operation.type == OperationType.SKIP_IF_VX_AND_VY_ARE_NOT_EQUAL:
            if self.registers[operation.x].value != self.registers[operation.y].value:
                self.program_counter += 2
        elif operation.type == OperationType.SET_INDEX:
            self.index = operation.nnn
        elif operation.type == OperationType.RANDOM:
            self.registers[operation.x] = c_uint8(
                math.ceil(random() * 255) & operation.nn.value
            )
        elif operation.type == OperationType.DISPLAY:
            sprite = [
                self.memory[i] for i in range(self.index, self.index + operation.n)
            ]
            collision = self.display.draw_sprite(
                sprite,
                self.registers[operation.x].value,
                self.registers[operation.y].value,
            )
            self.registers[0xF] = c_uint8(collision)
        elif operation.type == OperationType.SKIP_IF_VX_AND_KEYCODE_ARE_EQUAL:
            if self.registers[operation.x].value == self.keycode:
                self.program_counter += 2
        elif operation.type == OperationType.SKIP_IF_VX_AND_KEYCODE_ARE_NOT_EQUAL:
            if self.registers[operation.x].value != self.keycode:
                self.program_counter += 2
        elif operation.type == OperationType.SET_DELAY_TIMER_TO_VX:
            self.delay_timer = self.registers[operation.x]
        elif operation.type == OperationType.SET_SOUND_TIMER_TO_VX:
            self.sound_timer = self.registers[operation.x]
        elif operation.type == OperationType.SET_VX_TO_DELAY_TIMER:
            self.registers[operation.x] = self.delay_timer
        elif operation.type == OperationType.ADD_VX_TO_INDEX:
            self.index = self.index + self.registers[operation.x].value
        elif operation.type == OperationType.FONT:
            character = self.registers[operation.x].value
            sprite = Font.mapping_for_character(character)
            self.index = next(
                location
                for location in range(FONT_ADDRESS_START, FONT_ADDRESS_END, 5)
                if self.memory[location : location + 5] == sprite
            )
        elif operation.type == OperationType.STORE_BINARY_CODED_DECIMAL:
            value = self.registers[operation.x].value
            self.memory[self.index : self.index + 3] = [int(i) for i in str(value)]
        elif operation.type == OperationType.LOAD_REGISTERS:
            for i in range(0x0, operation.x + 1):
                self.memory[self.index + i] = self.registers[i].value
        elif operation.type == OperationType.STORE_REGISTERS:
            for i in range(0x0, operation.x + 1):
                self.registers[i] = c_uint8(self.memory[self.index + i])
        else:
            import logging

            logger = logging.getLogger(__name__)
            logger.warn(f"unabled operation {operation}")

    def cycle(self):
        opcode = self.fetch()
        operation = self.decode(opcode)
        self.execute(operation)

        if self.delay_timer.value > 0:
            self.delay_timer = c_uint8(self.delay_timer.value - 1)

        if self.sound_timer.value > 0:
            self.sound_timer = c_uint8(self.sound_timer.value - 1)

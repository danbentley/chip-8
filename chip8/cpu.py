from ctypes import c_uint8
from dataclasses import dataclass
from functools import cached_property
from random import random
from typing import Optional
import enum
import math

from .backends.base import Renderable
from .fonts import Font

FONT_ADDRESS_START = 0x050
FONT_ADDRESS_END = 0x0A0


class InvalidRegisterError(Exception):
    """Exception raised if invalid register is accessed or mutated."""


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
        """Fetch item from register or raise InvalidRegisterError."""
        try:
            return getattr(self, f"V{index:X}")
        except (AttributeError, ValueError) as e:
            raise InvalidRegisterError(f"Attempt to get value from {index}") from e

    def __setitem__(self, index: int, value: c_uint8):
        """Set item from register or raise InvalidRegisterError."""
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
    WAIT_FOR_KEY_PRESS = enum.auto()
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
    """A collection of rules to match a given OperationType.

    Operations are checked at exection with its type being the first matched
    rule.
    """

    type: OperationType

    nibble: int

    n: Optional[int] = None
    nn: Optional[int] = None

    def match(self, operation) -> bool:
        """Check with the rule matches a given operation.

        If definied in the rule, an operation needs to match:
         - n: 4-bit number, the last nibble. For the opcode 0x1234 n is 0x4
         - nn: 8-bit number, the second byte. For the opcode 0x1234 nn is 0x34
         - nibble: 4-bit number, the first nibble. For the opcode 0x1234 nn is 0x1
        """

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
    OperationMatchRule(nibble=0xF, nn=0x0A, type=OperationType.WAIT_FOR_KEY_PRESS),
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
    """An operation for the CPU to execute.

    Operations are decoded from CHIP-8 opcodes, a 16-bit
    integer created from two successive bytes from memory.
    """

    # Second nibble in the high bit. 0x2 in 0x1234
    x: int
    # First nibble in the low bit. 0x3 in 0x1234
    y: int
    # First nibble in the high bit. 0x1 in 0x1234
    nibble: int
    # last nibble in the opcode. 0x4 in 0x1234
    n: int
    # last byte in the opcode. 0x34 in 0x1234
    nn: c_uint8
    # 12-bit integer. Second, third and four nibble in the opcode. 0x234 in 0x1234
    nnn: int
    # Original opcode.
    opcode: int

    @classmethod
    def decode(cls, opcode: int):
        """Decode the opcode into its constituent parts."""

        high, low = opcode >> 8, opcode & 0x0F0

        nibble = high >> 4
        y = low >> 4
        x = high & 0xF
        n = opcode & 0x0F
        nn = c_uint8(opcode & 0x0FF)
        nnn = opcode & 0x0FFF

        return cls(x=x, y=y, nibble=nibble, n=n, nn=nn, nnn=nnn, opcode=opcode)

    @cached_property
    def type(self):
        try:
            rule = next(r for r in rules if r.match(self))
        except StopIteration as e:
            raise UnhandledOperationError(
                f"Unhandled operation for opcode: {hex(self.opcode)}", operation=self,
            ) from e

        return rule.type

    def __repr__(self):
        return (
            f"Operation("
            f"x={self.x}, "
            f"y={self.y}, "
            f"nibble={self.nibble}, "
            f"n={self.n}, "
            f"nn={self.nn}, "
            f"nnn={self.nnn}, "
            f"opcode={self.opcode:#4x}, "
            f")"
        )


class UnhandledOperationError(Exception):
    """Exception raised if OperationType isn't matched for Operation."""

    def __init__(self, *args, operation=None):
        super().__init__(*args)
        self.operation = operation


class CPU:
    def __init__(self, memory, display: Renderable, registers):
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

    def fetch(self) -> int:
        """Fetch next opcode from memory.

        Chip-8 opcodes are two bytes in length, combined to a 16-bit integer
        for convenience.
        """
        instruction = self.memory[self.program_counter]
        self.program_counter += 1
        instruction2 = self.memory[self.program_counter]
        self.program_counter += 1

        return instruction << 8 | instruction2

    def decode(self, opcode: int) -> Operation:
        """Decode opcode into an Operation."""
        return Operation.decode(opcode)

    def execute(self, operation: Operation):
        """Execute opcode."""
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

        elif operation.type == OperationType.WAIT_FOR_KEY_PRESS:
            # Only advance if a key is pressed
            if not self.keycode:
                return

            self.registers[operation.x] = c_uint8(self.keycode)
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
                if self.memory[location : location + len(sprite)] == sprite
            )

        elif operation.type == OperationType.STORE_BINARY_CODED_DECIMAL:
            value = self.registers[operation.x].value
            self.memory[self.index : self.index + len(str(value))] = [
                int(i) for i in str(value)
            ]

        elif operation.type == OperationType.LOAD_REGISTERS:
            for i in range(0x0, operation.x + 1):
                self.memory[self.index + i] = self.registers[i].value

        elif operation.type == OperationType.STORE_REGISTERS:
            for i in range(0x0, operation.x + 1):
                self.registers[i] = c_uint8(self.memory[self.index + i])

    def cycle(self):
        """Emulate a single CPU cycle.

        Called once per cycle of the Event loop
        """
        opcode = self.fetch()
        operation = self.decode(opcode)
        self.execute(operation)

        if self.delay_timer.value > 0:
            self.delay_timer = c_uint8(self.delay_timer.value - 1)

        if self.sound_timer.value > 0:
            self.sound_timer = c_uint8(self.sound_timer.value - 1)

    def shutdown(self):
        """Called when backend emits QUIT event."""
        pass

    def __str__(self):
        return f'{self.program_counter=}'

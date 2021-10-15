from dataclasses import dataclass


class InvalidRegisterError(Exception):
    ...


class Registers:
    V0 = 0b0
    V1 = 0b0
    V2 = 0b0
    V3 = 0b0
    V4 = 0b0
    V5 = 0b0
    V6 = 0b0
    V7 = 0b0
    V8 = 0b0
    V9 = 0b0
    VA = 0b0
    VB = 0b0
    VC = 0b0
    VD = 0b0
    VE = 0b0
    VF = 0b0

    def __getitem__(self, index: int) -> int:
        try:
            return getattr(self, f"V{index:X}")
        except (AttributeError, ValueError) as e:
            raise InvalidRegisterError(f"Attempt to get value from {index}") from e

    def __setitem__(self, index: int, value: int):
        try:
            setattr(self, f"V{index:X}", value)
        except (AttributeError, ValueError) as e:
            raise InvalidRegisterError(f"Attempt to set value in {index}") from e


@dataclass(frozen=True)
class Operation:
    CLEAR_SCREEN = 0xE0
    JUMP = 0x1
    SET_REGISTER = 0x6
    ADD = 0x7
    SET_INDEX = 0xA
    DISPLAY = 0xD

    x: int
    y: int
    nibble: int
    high: int
    low: int
    n: int
    nn: int
    nnn: int
    opcode: int

    @classmethod
    def decode(cls, opcode):
        high, low = opcode >> 8, opcode & 0x0F0

        nibble = high >> 4
        y = low >> 4
        x = high & 0xF
        n = opcode & 0x0F
        nn = opcode & 0x0FF
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

    def __init__(self, memory, display):
        self.memory = memory
        self.display = display
        self.registers = Registers()

    def fetch(self):
        instruction = self.memory[self.program_counter]
        self.program_counter += 1
        instruction2 = self.memory[self.program_counter]
        self.program_counter += 1

        return instruction << 8 | instruction2

    def decode(self, opcode):
        return Operation.decode(opcode)

    def execute(self, operation):
        if operation.low == Operation.CLEAR_SCREEN:
            self.display.clear()
        elif operation.nibble == Operation.JUMP:
            self.program_counter = operation.nnn
        elif operation.nibble == Operation.SET_REGISTER:
            self.registers[operation.x] = operation.nn
        elif operation.nibble == Operation.ADD:
            self.registers[operation.x] += operation.nn
        elif operation.nibble == Operation.DISPLAY:
            sprite = [
                self.memory[i] for i in range(self.index, self.index + operation.n)
            ]
            self.display.draw_sprite(
                sprite, self.registers[operation.x], self.registers[operation.y]
            )
        elif operation.nibble == Operation.SET_INDEX:
            self.index = operation.nnn
        else:
            raise UnhandledOperationError(
                f"Unhandled operation for opcode: {hex(operation.opcode)}",
                operation=operation,
            )

    def cycle(self):
        opcode = self.fetch()
        operation = self.decode(opcode)
        self.execute(operation)

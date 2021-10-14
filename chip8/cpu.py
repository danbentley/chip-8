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

    def __getitem__(self, index: str) -> int:
        try:
            return getattr(self, f"V{index}")
        except AttributeError as e:
            raise InvalidRegisterError from e

    def __setitem__(self, index: str, value: int):
        if not hasattr(self, f"V{index}"):
            raise InvalidRegisterError
        setattr(self, f"V{index}", value)


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

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

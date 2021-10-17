from enum import Enum


class FontLookup(Enum):
    ZERO = "0"
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"

    @classmethod
    def key_for_character(cls, character: str) -> str:
        try:
            return next(k for k, v in cls.__members__.items() if v.value == character)
        except StopIteration as e:
            raise Exception(f'Unable to find key for "{character}"') from e


class Font(Enum):
    """Preloaded font font CHIP-8 intepretor.

    The font contains 16 hex digits to be loaded in to memory
    in the first 512 bytes.

    Each character is four pixels wide by five pixels high

    Font data is often documented as hex values with the intention that the
    individual bits are rendered to screen.
    """

    ZERO = [0xF0, 0x90, 0x90, 0x90, 0xF0]
    ONE = [0x20, 0x60, 0x20, 0x20, 0x70]
    TWO = [0xF0, 0x10, 0xF0, 0x80, 0xF0]
    THREE = [0xF0, 0x10, 0xF0, 0x10, 0xF0]
    FOUR = [0x90, 0x90, 0xF0, 0x10, 0x10]
    FIVE = [0xF0, 0x80, 0xF0, 0x10, 0xF0]
    SIX = [0xF0, 0x80, 0xF0, 0x90, 0xF0]
    SEVEN = [0xF0, 0x10, 0x20, 0x40, 0x40]
    EIGHT = [0xF0, 0x90, 0xF0, 0x90, 0xF0]
    NINE = [0xF0, 0x90, 0xF0, 0x10, 0xF0]
    A = [0xF0, 0x90, 0xF0, 0x90, 0x90]
    B = [0xE0, 0x90, 0xE0, 0x90, 0xE0]
    C = [0xF0, 0x80, 0x80, 0x80, 0xF0]
    D = [0xE0, 0x90, 0x90, 0x90, 0xE0]
    E = [0xF0, 0x80, 0xF0, 0x80, 0xF0]
    F = [0xF0, 0x80, 0xF0, 0x80, 0x80]

    @classmethod
    def to_sprite(cls, font) -> list[str]:
        return [f"{n:08b}" for n in font.value]

    @classmethod
    def mapping_for_character(cls, character: int) -> list[str]:
        key = FontLookup.key_for_character(f"{character:X}")
        return cls[key].value

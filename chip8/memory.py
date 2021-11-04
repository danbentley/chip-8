from ctypes import c_uint8

class InvalidMemoryAddressError(Exception):
    ...


class Memory:
    """The RAM of the Chip-8 intepretor.

    Creates an empty list of 4KB. Subscription used to access memory with
    InvalidMemoryAddressError raised if attempt is made to access memory
    outside of the bounds of RAM.

    From the spec:

    The Chip-8 language is capable of accessing up to 4KB (4,096 bytes) of RAM,
    from location 0x000 (0) to 0xFFF (4095). The first 512 bytes, from 0x000 to
    0x1FF, are where the original interpreter was located, and should not be
    used by programs.

    Most Chip-8 programs start at location 0x200 (512), but some begin at 0x600
    (1536). Programs beginning at 0x600 are intended for the ETI 660 computer.

    Memory Map:
    +---------------+= 0xFFF (4095) End of Chip-8 RAM
    |               |
    |               |
    |               |
    |               |
    |               |
    | 0x200 to 0xFFF|
    |     Chip-8    |
    | Program / Data|
    |     Space     |
    |               |
    |               |
    |               |
    +- - - - - - - -+= 0x600 (1536) Start of ETI 660 Chip-8 programs
    |               |
    |               |
    |               |
    +---------------+= 0x200 (512) Start of most Chip-8 programs
    | 0x000 to 0x1FF|
    | Reserved for  |
    |  interpreter  |
    +---------------+= 0x000 (0) Start of Chip-8 RAM

    Source: http://devernay.free.fr/hacks/chip8/C8TECH10.HTM#2.1
    """

    def __init__(self, size=4096):
        self.memory: list = [0x0] * size

    def __getitem__(self, address: int) -> c_uint8:
        try:
            return self.memory[address]
        except IndexError as e:
            raise InvalidMemoryAddressError from e

    def __setitem__(self, address: int, value: c_uint8):
        try:
            self.memory[address] = value
        except IndexError as e:
            raise InvalidMemoryAddressError from e


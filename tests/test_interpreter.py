import pytest

from chip8.interpreter import Keyboard


class TestBoot:
    def test_interpreter_ram_is_empty_post_boot(self, interpreter):
        interpreter.boot()

        assert all([n for n in range(0x000, 0x1FF) if interpreter.cpu.memory[n]])

    def test_work_ram_is_empty_post_boot(self, interpreter):
        interpreter.boot()

        assert all([n for n in range(0x200, 0xFFF) if interpreter.cpu.memory[n]])


class TestLoadRom:
    def test_load_rom(self, interpreter):
        with pytest.raises(FileNotFoundError):
            interpreter.load_rom("missing.chip8")

class TestKeyboard:
    def test_one(self):
        assert Keyboard.value_for_keycode(49) == 0x1

    def test_two(self):
        assert Keyboard.value_for_keycode(50) == 0x2

    def test_three(self):
        assert Keyboard.value_for_keycode(51) == 0x3

    def test_c(self):
        assert Keyboard.value_for_keycode(99) == 0xC

    def test_four(self):
        assert Keyboard.value_for_keycode(113) == 0x4

    def test_five(self):
        assert Keyboard.value_for_keycode(119) == 0x5

    def test_six(self):
        assert Keyboard.value_for_keycode(101) == 0x6

    def test_d(self):
        assert Keyboard.value_for_keycode(114) == 0xD

    def test_seven(self):
        assert Keyboard.value_for_keycode(97) == 0x7

    def test_eight(self):
        assert Keyboard.value_for_keycode(115) == 0x8

    def test_nine(self):
        assert Keyboard.value_for_keycode(100) == 0x9

    def test_e(self):
        assert Keyboard.value_for_keycode(102) == 0xE

    def test_a(self):
        assert Keyboard.value_for_keycode(122) == 0xA

    def test_zero(self):
        assert Keyboard.value_for_keycode(120) == 0x0

    def test_b(self):
        assert Keyboard.value_for_keycode(98) == 0xB

    def test_f(self):
        assert Keyboard.value_for_keycode(118) == 0xF

    def test_unmapped(self):
        assert Keyboard.value_for_keycode(48) is None

    def test_none(self):
        assert Keyboard.value_for_keycode(None) is None

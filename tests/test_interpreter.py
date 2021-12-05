import pytest


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

# Chip-8 interpreter 

> CHIP-8 is an interpreted programming language, developed by Joseph Weisbecker.
> It was initially used on the COSMAC VIP and Telmac 1800 8-bit microcomputers in
> the mid-1970s. CHIP-8 programs are run on a CHIP-8 virtual machine.

[CHIP-8 - Wikipedia](https://en.wikipedia.org/wiki/CHIP-8)

## Install

To simplify dependency resolution inside a virtual environment, I recommend using [poetry](https://python-poetry.org/docs/#installation).

### Install dependencies

```poetry install```

### Run intepreter

```poetry run python main.py```

## Usage

```bash
positional arguments:
  path                  Path to rom file

optional arguments:
  -h, --help            show this help message and exit
  --backend {pygame,sdl}
                        Backend used to run the interpreter
  --scale SCALE         Scale the 64x32 display for better rendering on modern monitors
  --hertz HERTZ, --hz HERTZ, --speed HERTZ
                        Number of instructions to execute per second. Some games require
                        adjustments to improve playability.
  --profile, --no-profile
                        Profile CPU cycles. Outputs results on exit
```

## Key bindings

### Gameplay

A CHIP-8 interpreter supports 16 keys:

```
Chip-8 keyboard  QWERTY Keyboard

+–+–+–+–+        +–+–+–+–+
|1|2|3|C|        |1|2|3|4|             
+–+–+–+–+        +–+–+–+–+
|4|5|6|D|        |q|w|e|r|
+–+–+–+–+        +–+–+–+–+
|7|8|9|E|        |a|s|d|f|             
+–+–+–+–+        +–+–+–+–+
|A|0|B|F|        |z|x|c|v|
+–+–+–+–+        +–+–+–+–+
```

### Debug keys

 - `F5` Stop execution
 - `F6` Execute next opcode 
 - `F8` Resume execution

## Screenshots

![Tetris](/docs/images/tetris.png)
![Breakout](/docs/images/breakout.png)
![Space Invaders](/docs/images/space-invaders.png)
![BC Test](/docs/images/bc-test.png)
![Opcode Test](/docs/images/opcode-test.png)

## References

 - [Cowgod's Chip-8 Technical Reference](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM#4.0)
 - [Awesome CHIP-8 - CHIP-8](https://chip-8.github.io/links/)
 - [johnearnest.github.io/Octo/docs/chip8ref.pdf](http://johnearnest.github.io/Octo/docs/chip8ref.pdf)
 - [mattmikolay/chip-8: A collection of CHIP-8 programs and documentation](https://github.com/mattmikolay/chip-8)
 - [Jackson S - Chip 8 Instruction Scheduling and Frequency](https://jackson-s.me/2019/07/13/Chip-8-Instruction-Scheduling-and-Frequency.html)
 - [BC_test error codes](https://slack-files.com/T3CH37TNX-F3RKEUKL4-b05ab4930d)
 - [Byte Magazine Volume 03 Number 12 - An Easy Programming System](https://archive.org/details/byte-magazine-1978-12/page/n109/mode/2up)

import argparse

from chip8.interpreter import Interpreter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to rom file")
    args = parser.parse_args()

    interpreter = Interpreter()
    interpreter.boot()
    interpreter.load_rom(args.path)
    interpreter.run()


if __name__ == "__main__":
    main()

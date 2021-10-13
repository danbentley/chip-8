from chip8.fonts import Font


def test_zero():
    output = [
        "1111",
        "1001",
        "1001",
        "1001",
        "1111",
    ]

    assert output == Font.to_sprite(Font.ZERO)


def test_one():
    output = [
        "0010",
        "0110",
        "0010",
        "0010",
        "0111",
    ]

    assert output == Font.to_sprite(Font.ONE)


def test_two():
    output = [
        "1111",
        "0001",
        "1111",
        "1000",
        "1111",
    ]

    assert output == Font.to_sprite(Font.TWO)


def test_three():
    output = [
        "1111",
        "0001",
        "1111",
        "0001",
        "1111",
    ]

    assert output == Font.to_sprite(Font.THREE)


def test_four():
    output = [
        "1001",
        "1001",
        "1111",
        "0001",
        "0001",
    ]

    assert output == Font.to_sprite(Font.FOUR)


def test_five():
    output = [
        "1111",
        "1000",
        "1111",
        "0001",
        "1111",
    ]

    assert output == Font.to_sprite(Font.FIVE)


def test_six():
    output = [
        "1111",
        "1000",
        "1111",
        "1001",
        "1111",
    ]

    assert output == Font.to_sprite(Font.SIX)


def test_seven():
    output = [
        "1111",
        "0001",
        "0010",
        "0100",
        "0100",
    ]

    assert output == Font.to_sprite(Font.SEVEN)


def test_eight():
    output = [
        "1111",
        "1001",
        "1111",
        "1001",
        "1111",
    ]

    assert output == Font.to_sprite(Font.EIGHT)


def test_nine():
    output = [
        "1111",
        "1001",
        "1111",
        "0001",
        "1111",
    ]

    assert output == Font.to_sprite(Font.NINE)


def test_a():
    output = [
        "1111",
        "1001",
        "1111",
        "1001",
        "1001",
    ]

    assert output == Font.to_sprite(Font.A)


def test_b():
    output = [
        "1110",
        "1001",
        "1110",
        "1001",
        "1110",
    ]

    assert output == Font.to_sprite(Font.B)


def test_c():
    output = [
        "1111",
        "1000",
        "1000",
        "1000",
        "1111",
    ]

    assert output == Font.to_sprite(Font.C)


def test_d():
    output = [
        "1110",
        "1001",
        "1001",
        "1001",
        "1110",
    ]

    assert output == Font.to_sprite(Font.D)


def test_e():
    output = [
        "1111",
        "1000",
        "1111",
        "1000",
        "1111",
    ]

    assert output == Font.to_sprite(Font.E)


def test_f():
    output = [
        "1111",
        "1000",
        "1111",
        "1000",
        "1000",
    ]

    assert output == Font.to_sprite(Font.F)

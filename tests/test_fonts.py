from chip8.fonts import Font


class TestSprite:
    def test_zero(self):
        output = [
            "11110000",
            "10010000",
            "10010000",
            "10010000",
            "11110000",
        ]

        assert output == Font.to_sprite(Font.ZERO)

    def test_one(self):
        output = [
            "00100000",
            "01100000",
            "00100000",
            "00100000",
            "01110000",
        ]

        assert output == Font.to_sprite(Font.ONE)

    def test_two(self):
        output = [
            "11110000",
            "00010000",
            "11110000",
            "10000000",
            "11110000",
        ]

        assert output == Font.to_sprite(Font.TWO)

    def test_three(self):
        output = [
            "11110000",
            "00010000",
            "11110000",
            "00010000",
            "11110000",
        ]

        assert output == Font.to_sprite(Font.THREE)

    def test_four(self):
        output = [
            "10010000",
            "10010000",
            "11110000",
            "00010000",
            "00010000",
        ]

        assert output == Font.to_sprite(Font.FOUR)

    def test_five(self):
        output = [
            "11110000",
            "10000000",
            "11110000",
            "00010000",
            "11110000",
        ]

        assert output == Font.to_sprite(Font.FIVE)

    def test_six(self):
        output = [
            "11110000",
            "10000000",
            "11110000",
            "10010000",
            "11110000",
        ]

        assert output == Font.to_sprite(Font.SIX)

    def test_seven(self):
        output = [
            "11110000",
            "00010000",
            "00100000",
            "01000000",
            "01000000",
        ]

        assert output == Font.to_sprite(Font.SEVEN)

    def test_eight(self):
        output = [
            "11110000",
            "10010000",
            "11110000",
            "10010000",
            "11110000",
        ]

        assert output == Font.to_sprite(Font.EIGHT)

    def test_nine(self):
        output = [
            "11110000",
            "10010000",
            "11110000",
            "00010000",
            "11110000",
        ]

        assert output == Font.to_sprite(Font.NINE)

    def test_a(self):
        output = [
            "11110000",
            "10010000",
            "11110000",
            "10010000",
            "10010000",
        ]

        assert output == Font.to_sprite(Font.A)

    def test_b(self):
        output = [
            "11100000",
            "10010000",
            "11100000",
            "10010000",
            "11100000",
        ]

        assert output == Font.to_sprite(Font.B)

    def test_c(self):
        output = [
            "11110000",
            "10000000",
            "10000000",
            "10000000",
            "11110000",
        ]

        assert output == Font.to_sprite(Font.C)

    def test_d(self):
        output = [
            "11100000",
            "10010000",
            "10010000",
            "10010000",
            "11100000",
        ]

        assert output == Font.to_sprite(Font.D)

    def test_e(self):
        output = [
            "11110000",
            "10000000",
            "11110000",
            "10000000",
            "11110000",
        ]

        assert output == Font.to_sprite(Font.E)

    def test_f(self):
        output = [
            "11110000",
            "10000000",
            "11110000",
            "10000000",
            "10000000",
        ]

        assert output == Font.to_sprite(Font.F)

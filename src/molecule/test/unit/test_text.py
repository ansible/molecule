from molecule.text import strip_ansi_color, strip_ansi_escape


def test_strip_ansi_escape():
    string = "ls\r\n\x1b[00m\x1b[01;31mfoo\x1b[00m\r\n\x1b[01;31m"

    assert "ls\r\nfoo\r\n" == strip_ansi_escape(string)


def test_strip_ansi_color():
    s = "foo\x1b[0m\x1b[0m\x1b[0m\n\x1b[0m\x1b[0m\x1b[0m\x1b[0m\x1b[0m"

    assert "foo\n" == strip_ansi_color(s)

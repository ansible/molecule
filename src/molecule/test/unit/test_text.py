from molecule.text import (
    camelize,
    strip_ansi_color,
    strip_ansi_escape,
    title,
    underscore,
)


def test_camelize():
    assert "Foo" == camelize("foo")
    assert "FooBar" == camelize("foo_bar")
    assert "FooBarBaz" == camelize("foo_bar_baz")


def test_strip_ansi_color():
    s = "foo\x1b[0m\x1b[0m\x1b[0m\n\x1b[0m\x1b[0m\x1b[0m\x1b[0m\x1b[0m"

    assert "foo\n" == strip_ansi_color(s)


def test_strip_ansi_escape():
    string = "ls\r\n\x1b[00m\x1b[01;31mfoo\x1b[00m\r\n\x1b[01;31m"

    assert "ls\r\nfoo\r\n" == strip_ansi_escape(string)


def test_title():
    assert "Foo" == title("foo")
    assert "Foo Bar" == title("foo_bar")


def test_underscore():
    assert "foo" == underscore("Foo")
    assert "foo_bar" == underscore("FooBar")
    assert "foo_bar_baz" == underscore("FooBarBaz")

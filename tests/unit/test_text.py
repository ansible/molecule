"""Test the molecule text module."""

from __future__ import annotations

from molecule.text import (
    camelize,
    strip_ansi_color,
    strip_ansi_escape,
    title,
    underscore,
)


def test_camelize():  # type: ignore[no-untyped-def]  # noqa: ANN201
    assert camelize("foo") == "Foo"  # type: ignore[no-untyped-call]
    assert camelize("foo_bar") == "FooBar"  # type: ignore[no-untyped-call]
    assert camelize("foo_bar_baz") == "FooBarBaz"  # type: ignore[no-untyped-call]


def test_strip_ansi_color():  # type: ignore[no-untyped-def]  # noqa: ANN201
    s = "foo\x1b[0m\x1b[0m\x1b[0m\n\x1b[0m\x1b[0m\x1b[0m\x1b[0m\x1b[0m"

    assert strip_ansi_color(s) == "foo\n"  # type: ignore[no-untyped-call]


def test_strip_ansi_escape():  # type: ignore[no-untyped-def]  # noqa: ANN201
    string = "ls\r\n\x1b[00m\x1b[01;31mfoo\x1b[00m\r\n\x1b[01;31m"

    assert strip_ansi_escape(string) == "ls\r\nfoo\r\n"  # type: ignore[no-untyped-call]


def test_title():  # type: ignore[no-untyped-def]  # noqa: ANN201
    assert title("foo") == "Foo"
    assert title("foo_bar") == "Foo Bar"


def test_underscore():  # type: ignore[no-untyped-def]  # noqa: ANN201
    assert underscore("Foo") == "foo"  # type: ignore[no-untyped-call]
    assert underscore("FooBar") == "foo_bar"  # type: ignore[no-untyped-call]
    assert underscore("FooBarBaz") == "foo_bar_baz"  # type: ignore[no-untyped-call]

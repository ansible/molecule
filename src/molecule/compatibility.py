# ruff: noqa: ANN001, D102
# pylint: disable=missing-function-docstring,missing-return-doc,missing-param-doc
"""Compatibility module for Python 3.10+."""

from __future__ import annotations

import enum


class StrEnum(str, enum.Enum):
    """Enum where members are also (and must be) strings.

    This is a vendored copy of Python 3.11's enum.StrEnum for use on Python 3.10.
    On Python 3.11+, you should use the built-in enum.StrEnum instead.
    """

    def __new__(cls, value):
        if type(value) is str:
            return str.__new__(cls, value)
        return str.__new__(cls, str(value))

    def __str__(self):
        return str.__str__(self)

    def __format__(self, format_spec):
        return str.__format__(self, format_spec)

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        """Return the lower-cased version of the member name."""
        return name.lower()

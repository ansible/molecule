"""Compatibility module for Python 3.10+."""

from __future__ import annotations

import enum

from sys import version_info


class _StrEnum(str, enum.Enum):
    """An enum that behaves both as a string and an enum.

    Compatible with Python 3.10+.
    """

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"

    @classmethod
    def list(cls) -> list[str]:
        return [c.value for c in cls]

    @classmethod
    def from_str(cls, value: str) -> _StrEnum:
        """Get enum member from string value.

        Args:
            value: String value to convert to enum member.

        Returns:
            The matching enum member.

        Raises:
            ValueError: If value is not found in enum.
        """
        for member in cls:
            if member.value == value:
                return member
        msg = f"{value!r} is not a valid {cls.__name__}"
        raise ValueError(msg)


if version_info >= (3, 11):
    StrEnum = enum.StrEnum  # type: ignore[attr-defined] # pylint: disable=no-member
else:
    StrEnum = _StrEnum

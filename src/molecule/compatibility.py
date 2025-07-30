"""Compatibility module for Python 3.10+."""

from __future__ import annotations

import enum

from sys import version_info
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Any


class _StrEnum(str, enum.Enum):
    """An enum that behaves both as a string and an enum.
    Compatible with Python 3.10+.

    This implementation mimics Python 3.11's enum.StrEnum behavior:
    - Members are also strings and can be used like strings
    - auto() produces lowercase member names as values
    - Uses str.__str__ and str.__format__ for string operations
    """

    def __str__(self) -> str:
        """Use str.__str__ for compatibility with Python 3.11 StrEnum."""
        return str.__str__(self)

    def __format__(self, format_spec: str) -> str:
        """Use str.__format__ for compatibility with Python 3.11 StrEnum."""
        return str.__format__(self, format_spec)

    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[Any]) -> str:
        """Generate the next value for auto() - returns lowercase member name.

        This matches Python 3.11's StrEnum behavior where auto() produces
        the lowercase member name as the value.

        Args:
            name: The name of the enum member.
            start: The starting value (unused).
            count: The count of members (unused).
            last_values: List of previous values (unused).

        Returns:
            The lowercase member name.
        """
        return name.lower()

    @classmethod
    def list(cls) -> list[str]:
        """Return a list of all enum values.

        Returns:
            List of string values for all enum members.
        """
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

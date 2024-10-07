"""Text utils."""

from __future__ import annotations

import re

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import AnyStr


def camelize(string: str) -> str:
    """Format string as camel-case.

    Args:
        string: The string to be formatted.

    Returns:
        The formatted string.
    """
    # NOTE(retr0h): Taken from jpvanhal/inflection
    # https://github.com/jpvanhal/inflection
    return re.sub(r"(?:^|_)(.)", lambda m: m.group(1).upper(), string)


def underscore(string: str) -> str:
    """Format string to underlined notation.

    Args:
        string: The string to be formatted.

    Returns:
        The formatted string.
    """
    # NOTE(retr0h): Taken from jpvanhal/inflection
    # https://github.com/jpvanhal/inflection
    string = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", string)
    string = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", string)
    string = string.replace("-", "_")

    return string.lower()


def title(word: str) -> str:
    """Format title.

    Args:
        word: The string to be formatted.

    Returns:
        The formatted string.
    """
    return " ".join(x.capitalize() or "_" for x in word.split("_"))


def chomp(text: str) -> str:
    """Remove any training spaces from a multiline string.

    Args:
        text: Block of text to strip.

    Returns:
        Text with trailing spaces stripped from newlines.
    """
    return "\n".join([x.rstrip() for x in text.splitlines()])


def strip_ansi_escape(data: AnyStr) -> str:
    """Remove all ANSI escapes from string or bytes.

    Args:
        data: Text to clean in string or bytes.

    Returns:
        String cleaned of ANSI escape sequences.
    """
    text = _to_unicode(data)
    return re.sub(r"\x1b[^m]*m", "", text)


def strip_ansi_color(data: AnyStr) -> str:
    """Remove ANSI colors from string or bytes.

    Args:
        data: Text to clean in string or bytes.

    Returns:
        String cleaned of ANSI colors.
    """
    # Taken from tabulate
    invisible_codes = re.compile(r"\x1b\[\d*m")

    text = _to_unicode(data)
    return re.sub(invisible_codes, "", text)


def _to_unicode(data: AnyStr) -> str:
    """Ensure data is a UTF-8 string.

    Args:
        data: A string that can be bytes or str.

    Returns:
        A UTF-8 string.
    """
    if isinstance(data, bytes):
        return data.decode("utf-8")
    return data

"""Text utils."""
import re


def chomp(text: str) -> str:
    """Remove any training spaces from string."""
    return "\n".join([x.rstrip() for x in text.splitlines()])


def strip_ansi_escape(data):
    """Remove all ANSI escapes from string or bytes.

    If bytes is passed instead of string, it will be converted to string
    using UTF-8.
    """
    if isinstance(data, bytes):
        data = data.decode("utf-8")

    return re.sub(r"\x1b[^m]*m", "", data)


def strip_ansi_color(data):
    """Remove ANSI colors from string or bytes."""
    if isinstance(data, bytes):
        data = data.decode("utf-8")

    # Taken from tabulate
    invisible_codes = re.compile(r"\x1b\[\d*m")

    return re.sub(invisible_codes, "", data)

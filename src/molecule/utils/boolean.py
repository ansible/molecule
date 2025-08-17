"""Boolean utility functions."""

from __future__ import annotations


def to_bool(a: object) -> bool:
    """Return a bool for the arg.

    Args:
        a: A value to coerce to bool.

    Returns:
        A bool representation of a.
    """
    if a is None or isinstance(a, bool):
        return bool(a)
    if isinstance(a, str):
        a = a.lower()
    return a in ("yes", "on", "1", "true", 1)

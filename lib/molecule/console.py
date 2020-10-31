"""Console and terminal utilities."""
import os
import sys
from typing import Any

from rich.console import Console
from rich.theme import Theme

theme = Theme(
    {
        "info": "dim cyan",
        "warning": "magenta",
        "danger": "bold red",
        "scenario": "green",
        "action": "green",
    }
)


# Based on Ansible implementation
def to_bool(a: Any) -> bool:
    """Return a bool for the arg."""
    if a is None or isinstance(a, bool):
        return bool(a)
    if isinstance(a, str):
        a = a.lower()
    if a in ("yes", "on", "1", "true", 1):
        return True
    return False


def should_do_markup() -> bool:
    """Decide about use of ANSI colors."""
    py_colors = None

    # https://xkcd.com/927/
    for v in ["PY_COLORS", "CLICOLOR", "FORCE_COLOR", "ANSIBLE_FORCE_COLOR"]:
        value = os.environ.get(v, None)
        if value is not None:
            py_colors = to_bool(value)
            break

    # If deliverately disabled colors
    if os.environ.get("NO_COLOR", None):
        return False

    # User configuration requested colors
    if py_colors is not None:
        return to_bool(py_colors)

    # Using tty detection logic
    return sys.stdout.isatty() and os.environ.get("TERM") != "dumb"


console = Console(force_terminal=should_do_markup(), theme=theme)

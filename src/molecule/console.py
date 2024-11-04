"""Console and terminal utilities."""

from __future__ import annotations

import os
import sys

from typing import Any

from enrich.console import Console
from rich.style import Style
from rich.theme import Theme


theme = Theme(
    {
        "info": "dim cyan",
        "warning": "magenta",
        "danger": "bold red",
        "scenario": "green",
        "action": "green",
        "section_title": "bold cyan",
        "logging.level.notset": Style(dim=True),
        "logging.level.debug": Style(color="white", dim=True),
        "logging.level.info": Style(color="blue"),
        "logging.level.warning": Style(color="red"),
        "logging.level.error": Style(color="red", bold=True),
        "logging.level.critical": Style(color="red", bold=True),
        "logging.level.success": Style(color="green", bold=True),
    },
)


# Based on Ansible implementation
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


def should_do_markup() -> bool:
    """Decide about use of ANSI colors.

    Returns:
        Whether the output should be colored.
    """
    py_colors = None

    # https://xkcd.com/927/
    for v in ["PY_COLORS", "CLICOLOR", "FORCE_COLOR", "ANSIBLE_FORCE_COLOR"]:
        value = os.environ.get(v, None)
        if value is not None:
            py_colors = to_bool(value)
            break

    # If deliberately disabled colors
    if os.environ.get("NO_COLOR", None):
        return False

    # User configuration requested colors
    if py_colors is not None:
        return to_bool(py_colors)

    term = os.environ.get("TERM", "")
    if "xterm" in term:
        return True

    if term == "dumb":
        return False

    # Use tty detection logic as last resort because there are numerous
    # factors that can make isatty return a misleading value, including:
    # - stdin.isatty() is the only one returning true, even on a real terminal
    # - stderr returning false if user user uses a error stream coloring solution
    return sys.stdout.isatty()


# Define ANSIBLE_FORCE_COLOR if markup is enabled and another value is not
# already given. This assures that Ansible subprocesses are still colored,
# even if they do not run with a real TTY.
if should_do_markup():
    os.environ["ANSIBLE_FORCE_COLOR"] = os.environ.get("ANSIBLE_FORCE_COLOR", "1")

console_options: dict[str, Any] = {"emoji": False, "theme": theme, "soft_wrap": True}

console = Console(
    force_terminal=should_do_markup(),
    theme=theme,
    record=True,
    redirect=True,
)
console_options_stderr = console_options.copy()
console_options_stderr["stderr"] = True
console_stderr: Console = Console(**console_options_stderr)

"""Console and terminal utilities."""

from __future__ import annotations

import os
import sys

from typing import Any

from enrich.console import Console
from rich.style import Style
from rich.theme import Theme

from molecule.ansi_output import should_do_markup


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


# Define ANSIBLE_FORCE_COLOR if markup is enabled and another value is not
# already given. This assures that Ansible subprocesses are still colored,
# even if they do not run with a real TTY.
if should_do_markup():
    os.environ["ANSIBLE_FORCE_COLOR"] = os.environ.get("ANSIBLE_FORCE_COLOR", "1")

# Capture original streams before Rich Console objects hijack them
# These will be used by the logger to write directly to the original streams
original_stdout = sys.stdout
original_stderr = sys.stderr

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

"""ANSI Output formatting and color support for Molecule.

This module provides a reusable class for converting Rich-style markup
to ANSI escape codes while respecting color configuration.

Molecule Output Color Mapping

This color scheme is designed to align closely with Ansible's own terminal color conventions,
providing consistent visual language across Molecule and Ansible output. Key colors such as
GREEN for success (OK), RED for errors, YELLOW for changes, and MAGENTA for warnings reflect
Ansible's defaults as defined in `ansible/config/base.yml`. Other colors—such as CYAN and BLUE—
are used for clarity, neutrality, or emphasis in Molecule-specific output like actions,
scenario names, and commands.

This approach ensures readability, terminal compatibility, and a familiar experience for users
already accustomed to Ansible's interface.
"""

from __future__ import annotations

import os
import re
import sys


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

    # Use tty detection logic as last resort
    return sys.stdout.isatty()


class AnsiOutput:
    """ANSI output formatter with Rich-style markup support.

    Converts Rich-style markup tags to ANSI escape codes while respecting
    color configuration and providing reusable formatting functionality.
    """

    # ANSI Color Constants
    RESET = "\033[0m"

    # Basic Colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright Colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Text Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    # Symbols
    RIGHT_ARROW = "\u279c"

    def __init__(self) -> None:
        """Initialize the ANSI output formatter."""
        self.markup_enabled = should_do_markup()

        # Rich-style markup to ANSI mapping (Ansible-aligned)
        self.markup_map: dict[str, str] = {
            # ─── Message Types ───────────────────────────────
            "info": self.CYAN + self.DIM,  # Matches Ansible skip
            "warning": self.MAGENTA + self.BOLD,  # Matches Ansible warn
            "danger": self.RED + self.BOLD,  # Matches Ansible error
            "scenario": self.GREEN,  # Matches Ansible OK
            "action": self.YELLOW,  # Matches Ansible changed
            "exec_phase": self.BRIGHT_CYAN,  # Execution phase indicator
            "command": self.WHITE,
            "section_title": self.CYAN + self.BOLD,  # Neutral and distinct
            # ─── Logging Levels ──────────────────────────────
            "logging.level.debug": self.DIM + self.BLUE,
            "logging.level.info": self.CYAN + self.DIM,
            "logging.level.success": self.GREEN + self.BOLD,
            "logging.level.warning": self.MAGENTA + self.BOLD,
            "logging.level.error": self.RED + self.BOLD,
            "logging.level.critical": self.RED + self.BOLD + self.UNDERLINE,
            # Basic color names
            "red": self.RED,
            "green": self.GREEN,
            "blue": self.BLUE,
            "yellow": self.YELLOW,
            "magenta": self.MAGENTA,
            "cyan": self.CYAN,
            "white": self.WHITE,
            "black": self.BLACK,
            # Bright colors
            "bright_red": self.BRIGHT_RED,
            "bright_green": self.BRIGHT_GREEN,
            "bright_blue": self.BRIGHT_BLUE,
            "bright_yellow": self.BRIGHT_YELLOW,
            "bright_magenta": self.BRIGHT_MAGENTA,
            "bright_cyan": self.BRIGHT_CYAN,
            "bright_white": self.BRIGHT_WHITE,
            # Text styles
            "bold": self.BOLD,
            "dim": self.DIM,
            "italic": self.ITALIC,
            "underline": self.UNDERLINE,
        }

    def strip_markup(self, text: str) -> str:
        """Strip all Rich-style markup tags from text.

        Args:
            text: Text containing Rich markup tags.

        Returns:
            Text with all markup tags removed.
        """
        return re.sub(r"\[/?[^\]]*\]", "", text)

    def process_markup(self, text: str) -> str:
        """Convert Rich-style markup tags to ANSI escape codes.

        Args:
            text: Text containing Rich markup tags like [red], [bold], [/].

        Returns:
            Text with markup converted to ANSI codes or stripped if disabled.
        """
        if not self.markup_enabled:
            return self.strip_markup(text)

        # Process opening tags first to avoid conflicts with ANSI escape sequences
        def replace_tag(match: re.Match[str]) -> str:
            tag = match.group(1).lower()
            return self.markup_map.get(tag, "")

        # Match tags that don't start with /
        processed = re.sub(r"\[([^/\]]+)\]", replace_tag, text)

        # Process closing tags last (convert [/] to reset)
        result = re.sub(r"\[/\]", self.RESET, processed)
        return str(result)

    def format_log_level(self, level_name: str) -> tuple[str, str]:
        """Format a log level returning both colored and plain versions.

        Args:
            level_name: Name of the log level (e.g., 'INFO', 'WARNING').

        Returns:
            Tuple of (colored_version, plain_version).
        """
        width = 8

        if not self.markup_enabled:
            plain = f"{level_name:<{width}}"
            return plain, plain

        markup_key = f"logging.level.{level_name.lower()}"
        markup_text = f"[{markup_key}]{level_name:<{width}}[/]"
        colored = self.process_markup(markup_text)
        plain = self.strip_markup(markup_text)
        return colored, plain

    def format_scenario(self, scenario_name: str, step: str | None = None) -> tuple[str, str]:
        """Format a scenario name returning both colored and plain versions.

        Args:
            scenario_name: Name of the scenario.
            step: Optional step name (e.g., 'converge', 'create', 'destroy').

        Returns:
            Tuple of (colored_version, plain_version).
        """
        if not self.markup_enabled:
            plain = f"[{scenario_name} > {step}]" if step else f"[{scenario_name}]"
            return plain, plain

        if step:
            markup_text = rf"[scenario]{scenario_name}[/] {self.RIGHT_ARROW} [action]{step}[/]:"
        else:
            markup_text = rf"[scenario]{scenario_name}[/]"

        colored = self.process_markup(markup_text)
        plain = self.strip_markup(markup_text)
        return colored, plain

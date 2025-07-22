"""ANSI Output formatting and color support for Molecule.

This module provides a reusable class for converting Rich-style markup
to ANSI escape codes while respecting color configuration.
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

    def __init__(self) -> None:
        """Initialize the ANSI output formatter."""
        self.markup_enabled = should_do_markup()

        # Rich-style markup to ANSI mapping
        self.markup_map: dict[str, str] = {
            # Basic styles from Molecule's theme
            "info": self.DIM + self.CYAN,
            "warning": self.MAGENTA,
            "danger": self.BOLD + self.RED,
            "scenario": self.GREEN,
            "action": self.GREEN,
            "section_title": self.BOLD + self.CYAN,
            # Log level styles
            "logging.level.debug": self.WHITE + self.DIM,
            "logging.level.info": self.BLUE,
            "logging.level.warning": self.RED,
            "logging.level.error": self.BOLD + self.RED,
            "logging.level.critical": self.BOLD + self.RED,
            "logging.level.success": self.BOLD + self.GREEN,
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

    def format_scenario(self, scenario_name: str) -> str:
        """Format a scenario name with appropriate styling.

        Args:
            scenario_name: Name of the scenario.

        Returns:
            Formatted scenario name with color if markup is enabled.
        """
        if not self.markup_enabled:
            return f"[{scenario_name}]"

        return f"{self.GREEN}[{scenario_name}]{self.RESET}"

    def format_log_level(self, level_name: str, level_no: int) -> str:
        """Format a log level with appropriate color.

        Args:
            level_name: Name of the log level (e.g., 'INFO', 'WARNING').
            level_no: Numeric log level from logging module.

        Returns:
            Formatted log level with color if markup is enabled.
        """
        if not self.markup_enabled:
            return f"{level_name:<8}"

        # Map log levels to colors
        level_colors = {
            10: self.WHITE + self.DIM,  # DEBUG
            20: self.BLUE,  # INFO
            30: self.RED,  # WARNING
            40: self.BOLD + self.RED,  # ERROR
            50: self.BOLD + self.RED,  # CRITICAL
        }

        color = level_colors.get(level_no, "")
        return f"{color}{level_name:<8}{self.RESET}"

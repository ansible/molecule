"""Constants used by molecule."""

from __future__ import annotations

import os

from molecule.compatibility import StrEnum


# Exit codes
RC_SUCCESS = 0
RC_TIMEOUT = 3
RC_SETUP_ERROR = 4  # Broken setup, like missing Ansible
RC_UNKNOWN_ERROR = 5  # Unexpected errors for which we do not have more specific codes, yet

# File and directory patterns
MOLECULE_HEADER = "# Molecule managed"
MOLECULE_GLOB = os.environ.get("MOLECULE_GLOB", "molecule/*/molecule.yml")

# Default values
MOLECULE_DEFAULT_SCENARIO_NAME = "default"
MOLECULE_PLATFORM_NAME = os.environ.get("MOLECULE_PLATFORM_NAME", None)


# ANSI color definitions for terminal output
class ANSICodes(StrEnum):
    """ANSI escape sequences for terminal text formatting and colors.

    Attributes:
        RESET: Reset all formatting.
        BLACK: Black text.
        RED: Red text.
        GREEN: Green text.
        YELLOW: Yellow text.
        BLUE: Blue text.
        MAGENTA: Magenta text.
        CYAN: Cyan text.
        WHITE: White text.
        BRIGHT_BLACK: Bright black text.
        BRIGHT_RED: Bright red text.
        BRIGHT_GREEN: Bright green text.
        BRIGHT_YELLOW: Bright yellow text.
        BRIGHT_BLUE: Bright blue text.
        BRIGHT_MAGENTA: Bright magenta text.
        BRIGHT_CYAN: Bright cyan text.
        BRIGHT_WHITE: Bright white text.
        BOLD: Bold text.
        DIM: Dim text.
        ITALIC: Italic text.
        UNDERLINE: Underline text.
        RIGHT_ARROW: Right arrow.
    """

    # Reset
    RESET = "\033[0m"

    # Basic colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Text formatting
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    # Molecule-specific symbols
    RIGHT_ARROW = "➜"

    @property
    def tag(self) -> str:
        """Return the name of the ANSI code in markdown format.

        Returns:
            The name of the ANSI code in markdown format.
        """
        return self.name.lower()


# Scenario recap display order (reverse rank order - lowest to highest priority)
SCENARIO_RECAP_STATE_ORDER = ("successful", "disabled", "skipped", "missing", "failed")

# Completion state priority order (highest to lowest priority) - used for ActionResult.summary
COMPLETION_STATE_PRIORITY_ORDER = ("failed", "missing", "skipped", "disabled", "successful")

# Mapping of completion state names to their color tags for scenario recap
COMPLETION_STATE_COLORS = {
    "successful": ANSICodes.GREEN,
    "disabled": ANSICodes.CYAN,
    "skipped": ANSICodes.CYAN,
    "missing": ANSICodes.MAGENTA,
    "failed": ANSICodes.RED,
    "partial": ANSICodes.GREEN,
}


# Rich markup to ANSI mapping
MARKUP_MAP: dict[str, str] = {
    "logging.level.debug": ANSICodes.DIM,
    "logging.level.info": ANSICodes.CYAN,
    "logging.level.warning": ANSICodes.MAGENTA,
    "logging.level.error": ANSICodes.RED,
    "logging.level.critical": ANSICodes.RED + ANSICodes.BOLD,
    "logging.level.success": ANSICodes.GREEN,
    "exec_starting": ANSICodes.CYAN,
    "scenario": ANSICodes.GREEN,
    "action": ANSICodes.YELLOW,
}

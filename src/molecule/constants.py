"""Constants used by molecule."""

from __future__ import annotations

import os

from typing import TYPE_CHECKING, Literal, TypedDict

from molecule.compatibility import StrEnum


if TYPE_CHECKING:
    from molecule.types import DefaultConfigData


# Exit codes
RC_SUCCESS = 0
RC_TIMEOUT = 3
RC_SETUP_ERROR = 4  # Broken setup, like missing Ansible
RC_UNKNOWN_ERROR = 5  # Unexpected errors for which we do not have more specific codes, yet

# File and directory patterns
MOLECULE_HEADER = "# Molecule managed"
MOLECULE_ROOT = "molecule"
MOLECULE_GLOB = f"{MOLECULE_ROOT}/*/molecule.yml"
MOLECULE_COLLECTION_ROOT = "extensions/molecule"
MOLECULE_COLLECTION_GLOB = f"{MOLECULE_COLLECTION_ROOT}/*/molecule.yml"

# Default values
MOLECULE_DEFAULT_SCENARIO_NAME = "default"
MOLECULE_PLATFORM_NAME = os.environ.get("MOLECULE_PLATFORM_NAME", None)

# Environment variable to config attribute mapping for CLI options


class EnvVarConfig(TypedDict):
    """Configuration for an environment variable mapping.

    Attributes:
        attr: The config attribute name
        type: The type class for conversion (bool, str, int, etc.)
    """

    attr: Literal["report", "command_borders"]
    type: type


ENV_VAR_CONFIG_MAPPING: dict[str, EnvVarConfig] = {
    "MOLECULE_REPORT": {"attr": "report", "type": bool},
    "MOLECULE_COMMAND_BORDERS": {"attr": "command_borders", "type": bool},
}

# Default molecule configuration (forward-looking)
DEFAULT_CONFIG: DefaultConfigData = {
    "ansible": {
        "cfg": {},
        "executor": {
            "backend": "ansible-playbook",
            "args": {
                "ansible_navigator": [],
                "ansible_playbook": [],
            },
        },
        "env": {},
        "playbooks": {
            "cleanup": "cleanup.yml",
            "create": "create.yml",
            "converge": "converge.yml",
            "destroy": "destroy.yml",
            "prepare": "prepare.yml",
            "side_effect": "side_effect.yml",
            "verify": "verify.yml",
        },
    },
    "dependency": {
        "name": "galaxy",
        "command": None,
        "enabled": True,
        "options": {},
        "env": {},
    },
    "driver": {
        "name": "default",
        "provider": {"name": None},
        "options": {"managed": True},
        "ssh_connection_options": [],
        "safe_files": [],
    },
    "platforms": [],
    "prerun": True,
    "role_name_check": 0,
    "shared_state": False,
    "provisioner": {
        "name": "ansible",
        # Migrated keys removed: ansible_args, config_options, env, playbooks
        "connection_options": {},
        "options": {},
        "inventory": {
            "hosts": {},
            "host_vars": {},
            "group_vars": {},
            "links": {},
        },
        "children": {},
        "log": True,
    },
    "scenario": {
        "name": "default",  # Will be updated dynamically
        "check_sequence": [
            "dependency",
            "cleanup",
            "destroy",
            "create",
            "prepare",
            "converge",
            "check",
            "cleanup",
            "destroy",
        ],
        "cleanup_sequence": ["cleanup"],
        "converge_sequence": ["dependency", "create", "prepare", "converge"],
        "create_sequence": ["dependency", "create", "prepare"],
        "destroy_sequence": ["dependency", "cleanup", "destroy"],
        "test_sequence": [
            # dependency must be kept before lint to avoid errors
            "dependency",
            "cleanup",
            "destroy",
            "syntax",
            "create",
            "prepare",
            "converge",
            "idempotence",
            "side_effect",
            "verify",
            "cleanup",
            "destroy",
        ],
    },
    "verifier": {
        "name": "ansible",
        "enabled": True,
        "options": {},
        "env": {},
        "additional_files_or_dirs": [],
    },
}

# Default ansible.cfg configuration options (used by provisioner for merging)
DEFAULT_ANSIBLE_CFG_OPTIONS = {
    "defaults": {
        "display_failed_stderr": True,
        "forks": 50,
        "retry_files_enabled": False,
        "host_key_checking": False,
        "nocows": 1,
        "interpreter_python": "auto_silent",
    },
    "ssh_connection": {
        "scp_if_ssh": True,
        "control_path": "%(directory)s/%%h-%%p-%%r",
    },
}


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
        NOT_DIM: Turn off bold and dim without affecting colors.
        BOX_TOP_LEFT: Top-left corner box drawing character.
        BOX_TOP_RIGHT: Top-right corner box drawing character.
        BOX_BOTTOM_LEFT: Bottom-left corner box drawing character.
        BOX_BOTTOM_RIGHT: Bottom-right corner box drawing character.
        BOX_HORIZONTAL: Horizontal line box drawing character.
        BOX_VERTICAL: Vertical line box drawing character.
        BOX_TOP_MIDDLE: Top middle junction box drawing character.
        BOX_BOTTOM_MIDDLE: Bottom middle junction box drawing character.
        BOX_LEFT_MIDDLE: Left middle junction box drawing character.
        BOX_RIGHT_MIDDLE: Right middle junction box drawing character.
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

    # Text Style Resets (specific, not full reset)
    NOT_DIM = "\033[22m"  # Turns off bold and dim without affecting colors

    # Box Drawing Constants
    BOX_TOP_LEFT = "\u250c"
    BOX_TOP_RIGHT = "\u2510"
    BOX_BOTTOM_LEFT = "\u2514"
    BOX_BOTTOM_RIGHT = "\u2518"
    BOX_HORIZONTAL = "\u2500"
    BOX_VERTICAL = "\u2502"
    BOX_TOP_MIDDLE = "\u252c"
    BOX_BOTTOM_MIDDLE = "\u2534"
    BOX_LEFT_MIDDLE = "\u251c"
    BOX_RIGHT_MIDDLE = "\u2524"

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
    "exec_executing": ANSICodes.CYAN,
    "scenario": ANSICodes.GREEN,
    "action": ANSICodes.YELLOW,
}

# Border width constant
DEFAULT_BORDER_WIDTH = 83

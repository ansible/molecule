"""Tests for molecule.constants module."""

from __future__ import annotations

# mypy: disable-error-code=comparison-overlap
# Disable comparison-overlap warnings for StrEnum comparisons.
# StrEnum values are strings at runtime, so comparing them to string literals
# is valid and necessary for testing their actual values. Mypy incorrectly
# flags these as non-overlapping comparisons due to literal type inference.
from molecule.compatibility import StrEnum
from molecule.constants import (
    MARKUP_MAP,
    MOLECULE_DEFAULT_SCENARIO_NAME,
    MOLECULE_GLOB,
    MOLECULE_HEADER,
    MOLECULE_PLATFORM_NAME,
    RC_SETUP_ERROR,
    RC_SUCCESS,
    RC_TIMEOUT,
    RC_UNKNOWN_ERROR,
    ANSICodes,
)


# Expected values for testing
EXPECTED_RC_SUCCESS = 0
EXPECTED_RC_TIMEOUT = 3
EXPECTED_RC_SETUP_ERROR = 4
EXPECTED_RC_UNKNOWN_ERROR = 5


def test_exit_codes() -> None:
    """Test exit code constants."""
    assert RC_SUCCESS == EXPECTED_RC_SUCCESS
    assert RC_TIMEOUT == EXPECTED_RC_TIMEOUT
    assert RC_SETUP_ERROR == EXPECTED_RC_SETUP_ERROR
    assert RC_UNKNOWN_ERROR == EXPECTED_RC_UNKNOWN_ERROR


def test_molecule_constants() -> None:
    """Test molecule-specific constants."""
    assert MOLECULE_HEADER == "# Molecule managed"
    assert MOLECULE_DEFAULT_SCENARIO_NAME == "default"
    assert isinstance(MOLECULE_GLOB, str)
    assert "molecule.yml" in MOLECULE_GLOB


def test_molecule_platform_name() -> None:
    """Test MOLECULE_PLATFORM_NAME is imported correctly."""
    # This can be None or a string from environment
    assert MOLECULE_PLATFORM_NAME is None or isinstance(MOLECULE_PLATFORM_NAME, str)


def test_ansi_codes_is_strenum() -> None:
    """Test that ANSICodes is a StrEnum."""
    assert issubclass(ANSICodes, StrEnum)
    assert isinstance(ANSICodes.RED, str)


def test_ansi_codes_basic_colors() -> None:
    """Test basic ANSI color codes."""
    assert ANSICodes.BLACK == "\033[30m"
    assert ANSICodes.RED == "\033[31m"
    assert ANSICodes.GREEN == "\033[32m"
    assert ANSICodes.YELLOW == "\033[33m"
    assert ANSICodes.BLUE == "\033[34m"
    assert ANSICodes.MAGENTA == "\033[35m"
    assert ANSICodes.CYAN == "\033[36m"
    assert ANSICodes.WHITE == "\033[37m"


def test_ansi_codes_bright_colors() -> None:
    """Test bright ANSI color codes."""
    assert ANSICodes.BRIGHT_BLACK == "\033[90m"
    assert ANSICodes.BRIGHT_RED == "\033[91m"
    assert ANSICodes.BRIGHT_GREEN == "\033[92m"
    assert ANSICodes.BRIGHT_YELLOW == "\033[93m"
    assert ANSICodes.BRIGHT_BLUE == "\033[94m"
    assert ANSICodes.BRIGHT_MAGENTA == "\033[95m"
    assert ANSICodes.BRIGHT_CYAN == "\033[96m"
    assert ANSICodes.BRIGHT_WHITE == "\033[97m"


def test_ansi_codes_formatting() -> None:
    """Test ANSI formatting codes."""
    assert ANSICodes.RESET == "\033[0m"
    assert ANSICodes.BOLD == "\033[1m"
    assert ANSICodes.DIM == "\033[2m"
    assert ANSICodes.ITALIC == "\033[3m"
    assert ANSICodes.UNDERLINE == "\033[4m"


def test_ansi_codes_symbols() -> None:
    """Test molecule-specific ANSI symbols."""
    assert ANSICodes.RIGHT_ARROW == "➜"


def test_ansi_codes_tag_property() -> None:
    """Test the tag property returns lowercase name."""
    # Only test if the tag property exists
    if hasattr(ANSICodes.RED, "tag"):
        assert ANSICodes.RED.tag == "red"
        assert ANSICodes.BRIGHT_GREEN.tag == "bright_green"
        assert ANSICodes.BOLD.tag == "bold"
        assert ANSICodes.RIGHT_ARROW.tag == "right_arrow"


def test_ansi_codes_concatenation() -> None:
    """Test that ANSI codes can be concatenated."""
    red_bold = ANSICodes.RED + ANSICodes.BOLD
    assert red_bold == "\033[31m\033[1m"
    assert isinstance(red_bold, str)


def test_markup_map_exists() -> None:
    """Test that MARKUP_MAP is defined and is a dictionary."""
    assert isinstance(MARKUP_MAP, dict)
    assert len(MARKUP_MAP) > 0


def test_markup_map_logging_levels() -> None:
    """Test MARKUP_MAP contains logging level mappings."""
    assert MARKUP_MAP["logging.level.info"] == ANSICodes.CYAN
    assert MARKUP_MAP["logging.level.warning"] == ANSICodes.MAGENTA
    assert MARKUP_MAP["logging.level.error"] == ANSICodes.RED
    assert MARKUP_MAP["logging.level.critical"] == ANSICodes.RED + ANSICodes.BOLD
    assert MARKUP_MAP["logging.level.success"] == ANSICodes.GREEN


def test_markup_map_execution_mappings() -> None:
    """Test MARKUP_MAP contains execution-related mappings."""
    assert MARKUP_MAP["exec_executing"] == ANSICodes.CYAN
    assert MARKUP_MAP["scenario"] == ANSICodes.GREEN
    assert MARKUP_MAP["action"] == ANSICodes.YELLOW


def test_markup_map_values_are_ansi_codes() -> None:
    """Test all MARKUP_MAP values are valid ANSI codes or combinations."""
    for value in MARKUP_MAP.values():
        assert isinstance(value, str)
        assert "\033[" in value or value == "➜"  # ANSI escape or special symbol


def test_ansi_codes_all_values_are_strings() -> None:
    """Test all ANSICodes enum values are strings."""
    for ansi_code in ANSICodes:
        assert isinstance(ansi_code, str)
        assert isinstance(ansi_code.value, str)


def test_ansi_codes_have_expected_attributes() -> None:
    """Test ANSICodes has all expected color and formatting attributes."""
    # Basic colors
    basic_colors = ["BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE"]
    for color in basic_colors:
        assert hasattr(ANSICodes, color)

    # Bright colors
    bright_colors = [
        "BRIGHT_BLACK",
        "BRIGHT_RED",
        "BRIGHT_GREEN",
        "BRIGHT_YELLOW",
        "BRIGHT_BLUE",
        "BRIGHT_MAGENTA",
        "BRIGHT_CYAN",
        "BRIGHT_WHITE",
    ]
    for color in bright_colors:
        assert hasattr(ANSICodes, color)

    # Formatting
    formatting = ["RESET", "BOLD", "DIM", "ITALIC", "UNDERLINE"]
    for fmt in formatting:
        assert hasattr(ANSICodes, fmt)

    # Symbols
    assert hasattr(ANSICodes, "RIGHT_ARROW")


def test_exit_codes_are_integers() -> None:
    """Test all exit codes are integers."""
    assert isinstance(RC_SUCCESS, int)
    assert isinstance(RC_TIMEOUT, int)
    assert isinstance(RC_SETUP_ERROR, int)
    assert isinstance(RC_UNKNOWN_ERROR, int)


def test_exit_codes_are_positive_or_zero() -> None:
    """Test all exit codes are non-negative."""
    assert RC_SUCCESS >= 0
    assert RC_TIMEOUT >= 0
    assert RC_SETUP_ERROR >= 0
    assert RC_UNKNOWN_ERROR >= 0


def test_molecule_glob_format() -> None:
    """Test MOLECULE_GLOB has expected format."""
    assert "molecule" in MOLECULE_GLOB
    assert "yml" in MOLECULE_GLOB
    # Should be a glob pattern with wildcards
    assert "*" in MOLECULE_GLOB or "/" in MOLECULE_GLOB

"""Tests for the ansi_output module."""

from __future__ import annotations

import pytest

from molecule.ansi_output import AnsiOutput, should_do_markup, to_bool


@pytest.mark.parametrize(
    ("input_value", "expected"),
    (
        (None, False),
        (True, True),
        (False, False),
        ("yes", True),
        ("YES", True),
        ("on", True),
        ("ON", True),
        ("1", True),
        ("true", True),
        ("TRUE", True),
        ("no", False),
        ("off", False),
        ("0", False),
        ("false", False),
        ("random", False),
        (1, True),
        (0, False),
        (42, False),
    ),
)
def test_to_bool(input_value: object, expected: bool) -> None:  # noqa: FBT001
    """Test to_bool function with various inputs."""
    assert to_bool(input_value) is expected


@pytest.mark.parametrize(
    ("env_vars", "expected"),
    (
        ({"NO_COLOR": "1"}, False),
        ({"FORCE_COLOR": "1"}, True),
        ({"TERM": "xterm-256color"}, True),
        ({"TERM": "dumb"}, False),
        # New test cases that expose bugs
        ({"NO_COLOR": "1", "FORCE_COLOR": "1"}, False),  # NO_COLOR should override FORCE_COLOR
        ({"PY_COLORS": "0", "TERM": "xterm"}, False),  # PY_COLORS should override TERM
        ({"CLICOLOR": "0", "TERM": "xterm"}, False),  # CLICOLOR should override TERM
        (
            {"ANSIBLE_FORCE_COLOR": "1", "NO_COLOR": "1"},
            False,
        ),  # NO_COLOR should override ANSIBLE_FORCE_COLOR
        ({"NO_COLOR": "", "FORCE_COLOR": "1"}, True),  # Empty NO_COLOR should not disable colors
        (
            {"NO_COLOR": "", "TERM": "xterm"},
            True,
        ),  # Empty NO_COLOR should not disable colors, TERM should enable
    ),
)
def test_should_do_markup(
    env_vars: dict[str, str],
    expected: bool,  # noqa: FBT001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test should_do_markup function with various environment variables."""
    # Clear all color-related environment variables first
    for var in ["NO_COLOR", "FORCE_COLOR", "PY_COLORS", "CLICOLOR", "ANSIBLE_FORCE_COLOR", "TERM"]:
        monkeypatch.delenv(var, raising=False)

    # Set the test environment variables
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    assert should_do_markup() is expected


def test_should_do_markup_tty_detection(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test TTY detection fallback behavior."""
    # Clear all color-related environment variables
    for var in ["NO_COLOR", "FORCE_COLOR", "PY_COLORS", "CLICOLOR", "ANSIBLE_FORCE_COLOR", "TERM"]:
        monkeypatch.delenv(var, raising=False)

    # Mock isatty to return False (non-TTY environment like CI/CD)
    monkeypatch.setattr("sys.stdout.isatty", lambda: False)

    # This should return False since we're not in a TTY, but current implementation may be wrong
    result = should_do_markup()
    assert result is False, (
        "should_do_markup() should return False when not in a TTY and no color env vars set"
    )


def test_ansi_output_initialization() -> None:
    """Test AnsiOutput class initialization."""
    output = AnsiOutput()
    assert hasattr(output, "markup_enabled")
    assert hasattr(output, "markup_map")
    assert isinstance(output.markup_map, dict)


def test_ansi_color_constants() -> None:
    """Test that ANSI color constants are defined."""
    output = AnsiOutput()
    assert output.RESET == "\033[0m"
    assert output.RED == "\033[31m"
    assert output.GREEN == "\033[32m"
    assert output.BLUE == "\033[34m"
    assert output.BOLD == "\033[1m"
    assert output.DIM == "\033[2m"


@pytest.mark.parametrize(
    ("input_text", "expected_output"),
    (
        ("[red]Error message[/] with [bold]bold text[/]", "Error message with bold text"),
        ("Plain text message", "Plain text message"),
        ("[info]Running [scenario]test[/] > [action]create[/][/]", "Running test > create"),
    ),
)
def test_strip_markup(input_text: str, expected_output: str) -> None:
    """Test markup stripping functionality."""
    output = AnsiOutput()
    assert output.strip_markup(input_text) == expected_output


def test_process_markup_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test markup processing when markup is disabled."""
    monkeypatch.setenv("NO_COLOR", "1")
    output = AnsiOutput()

    text_with_markup = "[red]Error message[/] with [bold]bold text[/]"
    expected = "Error message with bold text"
    assert output.process_markup(text_with_markup) == expected


def test_process_markup_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test markup processing when markup is enabled."""
    # Clear NO_COLOR and set a color environment
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")
    output = AnsiOutput()

    text_with_markup = "[red]Error[/] message"
    result = output.process_markup(text_with_markup)

    # Should contain ANSI codes
    assert "\033[31m" in result  # Red color
    assert "\033[0m" in result  # Reset


def test_process_markup_with_unknown_tags(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test markup processing with unknown tags."""
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")
    output = AnsiOutput()

    text_with_unknown = "[unknown_tag]Text[/] with [red]known tag[/]"
    result = output.process_markup(text_with_unknown)

    # Should process known tags and ignore unknown ones
    assert "\033[31m" in result  # Red color for known tag
    assert "\033[0m" in result  # Reset
    assert "Text" in result
    assert "known tag" in result


@pytest.mark.parametrize(
    ("markup_enabled", "scenario_name", "expected_pattern"),
    (
        (False, "test_scenario", "[test_scenario]"),
        (True, "test_scenario", r"\033\[32m.*\[test_scenario\].*\033\[0m"),
    ),
)
def test_format_scenario(
    markup_enabled: bool,  # noqa: FBT001
    scenario_name: str,
    expected_pattern: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test scenario formatting with markup enabled/disabled."""
    if markup_enabled:
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.setenv("FORCE_COLOR", "1")
    else:
        monkeypatch.setenv("NO_COLOR", "1")

    output = AnsiOutput()
    colored, plain = output.format_scenario(scenario_name)

    if markup_enabled:
        assert "\033[32m" in colored  # Green color for scenario tag
        assert "\033[0m" in colored  # Reset
        assert "test_scenario" in colored  # Just check for scenario name, not brackets
        assert "test_scenario" in plain  # Plain version should also contain scenario name
        assert "\033[" not in plain  # No ANSI codes in plain version
    else:
        assert colored == expected_pattern
        assert plain == expected_pattern


def test_format_scenario_with_step(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test scenario formatting with step parameter."""
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")
    output = AnsiOutput()

    # Test with step
    colored, plain = output.format_scenario("test_scenario", "converge")
    assert "\033[32m" in colored  # Green for scenario
    assert "\033[33m" in colored  # Yellow for action (step)
    assert "test_scenario" in colored
    assert "converge" in colored
    assert "➜" in colored  # Right arrow
    assert ":" in colored  # Colon at end

    # Check plain version
    assert "test_scenario" in plain
    assert "converge" in plain
    assert "\033[" not in plain  # No ANSI codes in plain version

    # Test without markup
    monkeypatch.setenv("NO_COLOR", "1")
    output_no_markup = AnsiOutput()
    colored_no_markup, plain_no_markup = output_no_markup.format_scenario(
        "test_scenario",
        "converge",
    )
    assert colored_no_markup == "[test_scenario > converge]"
    assert plain_no_markup == "[test_scenario > converge]"


@pytest.mark.parametrize(
    ("level_name", "expected_ansi"),
    (
        ("DEBUG", "\033[2m"),  # Dim for DEBUG
        ("INFO", "\033[36m"),  # Cyan for INFO (new Ansible-aligned scheme)
        ("WARNING", "\033[35m"),  # Magenta for WARNING
        ("ERROR", "\033[31m"),  # Red for ERROR (new Ansible-aligned scheme)
    ),
)
def test_format_log_level_markup_enabled(
    level_name: str,
    expected_ansi: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test log level formatting when markup is enabled."""
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")
    output = AnsiOutput()

    colored, plain = output.format_log_level(level_name)
    assert expected_ansi in colored
    assert "\033[0m" in colored  # Reset
    assert level_name in plain
    assert "\033[" not in plain  # No ANSI codes in plain version


def test_format_log_level_markup_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test log level formatting when markup is disabled."""
    monkeypatch.setenv("NO_COLOR", "1")
    output = AnsiOutput()

    colored, plain = output.format_log_level("INFO")
    assert colored == "INFO    "  # 8 characters, left-aligned
    assert plain == "INFO    "  # Both should be the same when markup disabled
    assert "\033[" not in colored  # No ANSI codes
    assert "\033[" not in plain  # No ANSI codes


def test_markup_map_contains_expected_styles() -> None:
    """Test that markup_map contains expected style mappings."""
    output = AnsiOutput()

    # Test basic styles from Molecule's theme
    expected_styles = [
        "info",
        "warning",
        "danger",
        "scenario",
        "action",
        "exec_phase",
        "logging.level.info",
        "logging.level.warning",
        "logging.level.error",
        "red",
        "green",
        "blue",
        "bold",
        "dim",
    ]

    for style in expected_styles:
        assert style in output.markup_map


def test_markup_map_values_are_ansi_codes() -> None:
    """Test that markup_map values are valid ANSI escape codes."""
    output = AnsiOutput()

    for ansi_code in output.markup_map.values():
        assert isinstance(ansi_code, str)
        if ansi_code:  # Some might be empty strings
            assert ansi_code.startswith("\033[")


def test_complex_markup_processing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test processing of complex markup with nested tags."""
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")
    output = AnsiOutput()

    complex_markup = "[info]Running [scenario]test[/] > [action]create[/][/]"
    result = output.process_markup(complex_markup)

    # Should contain multiple ANSI codes and resets
    assert result.count("\033[") > 1  # Multiple ANSI sequences
    assert "\033[0m" in result  # Reset codes
    assert "Running" in result
    assert "test" in result
    assert "create" in result


def test_exec_phase_markup_processing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test processing of exec_phase markup."""
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")
    output = AnsiOutput()

    # Test exec_phase markup
    result = output.process_markup("[exec_phase]Starting[/]")

    # Should contain bright cyan for exec_phase
    assert "\033[96m" in result  # Bright cyan for exec_phase
    assert "\033[0m" in result  # Reset code
    assert "Starting" in result

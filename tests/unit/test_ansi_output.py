"""Tests for the ansi_output module."""

from __future__ import annotations

import pytest

from molecule.ansi_output import AnsiOutput, should_do_markup, to_bool
from molecule.constants import ANSICodes as A


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


def test_should_do_markup_basic() -> None:
    """Test should_do_markup function basic functionality."""
    # Test that the function returns a boolean
    result = should_do_markup()
    assert isinstance(result, bool)


def test_process_markup_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test process_markup function when markup is disabled."""
    monkeypatch.setenv("NO_COLOR", "1")
    ansi_output = AnsiOutput()
    assert ansi_output.process_markup("[bold]test[/]") == "test"


def test_process_markup_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test process_markup function when markup is enabled."""
    monkeypatch.setenv("FORCE_COLOR", "1")
    ansi_output = AnsiOutput()
    result = ansi_output.process_markup("[bold]test[/]")
    assert "test" in result
    # When markup is enabled, should contain ANSI codes
    if ansi_output.markup_enabled:
        assert "\x1b[" in result


def test_process_markup_with_unknown_tags(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test process_markup function with unknown tags."""
    monkeypatch.setenv("FORCE_COLOR", "1")
    ansi_output = AnsiOutput()

    # Test with a tag we know exists
    result = ansi_output.process_markup("[scenario]test[/]")
    assert "test" in result

    # Test with completely unknown tags
    result = ansi_output.process_markup("[unknown]test[/unknown]")
    assert "test" in result

    # Test mixed known and unknown
    result = ansi_output.process_markup("[scenario]known[/] [unknown]test[/unknown]")
    assert "known" in result
    assert "test" in result


# New tests for command borders functionality methods
def test_strip_markup_with_rich_tags() -> None:
    """Test strip_markup method with Rich-style tags."""
    ansi_output = AnsiOutput()

    # Test simple tag removal
    assert ansi_output.strip_markup("[bold]text[/]") == "text"
    assert ansi_output.strip_markup("[scenario]test[/]") == "test"
    assert ansi_output.strip_markup("[action]converge[/]") == "converge"

    # Test multiple tags
    assert ansi_output.strip_markup("[scenario]test[/] [action]action[/]") == "test action"

    # Test nested tags
    assert ansi_output.strip_markup("[bold][scenario]nested[/][/]") == "nested"

    # Test text without tags
    assert ansi_output.strip_markup("plain text") == "plain text"

    # Test empty string
    assert ansi_output.strip_markup("") == ""


def test_strip_markup_with_colors() -> None:
    """Test strip_markup method with color tags."""
    ansi_output = AnsiOutput()

    # Test color tags
    assert ansi_output.strip_markup("[red]error[/]") == "error"
    assert ansi_output.strip_markup("[green]success[/]") == "success"
    assert ansi_output.strip_markup("[yellow]warning[/]") == "warning"

    # Test mixed colors and styles
    assert ansi_output.strip_markup("[bold][red]bold red[/][/]") == "bold red"


def test_format_completion_message_with_markup_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test format_completion_message with markup enabled."""
    monkeypatch.setenv("FORCE_COLOR", "1")
    ansi_output = AnsiOutput()

    result = ansi_output.format_completion_message("Completed: Successful", A.GREEN)

    # Should contain the message
    assert "Completed: Successful" in result
    # If markup is enabled, should contain ANSI color codes
    if ansi_output.markup_enabled:
        assert A.GREEN in result
        assert A.RESET in result


def test_format_completion_message_with_markup_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test format_completion_message with markup disabled."""
    monkeypatch.setenv("NO_COLOR", "1")
    ansi_output = AnsiOutput()

    result = ansi_output.format_completion_message("Completed: Successful", A.GREEN)

    # Should be plain text without ANSI codes
    assert result == "Completed: Successful"
    assert A.GREEN not in result
    assert A.RESET not in result


def test_format_completion_note_with_markup_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test format_completion_note with markup enabled."""
    monkeypatch.setenv("FORCE_COLOR", "1")
    ansi_output = AnsiOutput()

    result = ansi_output.format_completion_note("cached")

    # Should contain the note with parentheses
    assert "(cached)" in result
    # If markup is enabled, should contain dim styling
    if ansi_output.markup_enabled:
        assert A.DIM in result
        assert A.RESET in result


def test_format_completion_note_with_markup_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test format_completion_note with markup disabled."""
    monkeypatch.setenv("NO_COLOR", "1")
    ansi_output = AnsiOutput()

    result = ansi_output.format_completion_note("cached")

    # Should be plain text with parentheses
    assert result == " (cached)"
    assert A.DIM not in result
    assert A.RESET not in result


def test_format_full_completion_line_basic() -> None:
    """Test format_full_completion_line basic functionality."""
    ansi_output = AnsiOutput()

    result = ansi_output.format_full_completion_line(
        "default",
        "converge",
        "Completed: Successful",
        "green",
    )

    # Should contain all components
    assert "default" in result
    assert "converge" in result
    assert "Completed: Successful" in result


def test_format_full_completion_line_with_note() -> None:
    """Test format_full_completion_line with note."""
    ansi_output = AnsiOutput()

    result = ansi_output.format_full_completion_line(
        "default",
        "converge",
        "Completed: Successful",
        "green",
        "cached",
    )

    # Should contain note
    assert "(cached)" in result
    assert "default" in result
    assert "converge" in result
    assert "Completed: Successful" in result


def test_format_full_completion_line_with_mock_ansi_object() -> None:
    """Test format_full_completion_line with object that has .tag attribute."""
    ansi_output = AnsiOutput()

    # Test with object that has a .tag attribute
    class MockANSI:
        tag = "red"

    mock_color = MockANSI()
    result = ansi_output.format_full_completion_line(
        "default",
        "converge",
        "Completed: Failed",
        mock_color,  # type: ignore[arg-type]
    )

    # Should handle enum-like objects with .tag attribute
    assert "default" in result
    assert "converge" in result
    assert "Completed: Failed" in result


@pytest.mark.parametrize(
    ("scenario", "action", "message", "color"),
    (
        ("default", "converge", "Completed: Successful", "green"),
        ("integration", "cleanup", "Completed: Skipped", "yellow"),
        ("test-scenario", "verify", "Completed: Failed", "red"),
        ("prod", "destroy", "Completed: Successful", "green"),
    ),
    ids=[
        "default_converge_successful",
        "integration_cleanup_skipped",
        "test_scenario_verify_failed",
        "prod_destroy_successful",
    ],
)
def test_format_full_completion_line_various_inputs(
    scenario: str,
    action: str,
    message: str,
    color: str,
) -> None:
    """Test format_full_completion_line with various input combinations."""
    ansi_output = AnsiOutput()

    result = ansi_output.format_full_completion_line(scenario, action, message, color)

    # All inputs should be present in the result
    assert scenario in result
    assert action in result
    assert message in result


def test_format_scenario_basic() -> None:
    """Test format_scenario method basic functionality."""
    ansi_output = AnsiOutput()

    colored, plain = ansi_output.format_scenario("default")

    # Both should contain the scenario name
    assert "default" in colored
    assert "default" in plain


def test_format_scenario_with_step() -> None:
    """Test format_scenario method with step parameter."""
    ansi_output = AnsiOutput()

    colored, plain = ansi_output.format_scenario("default", "converge")

    # Both should contain scenario and step
    assert "default" in colored
    assert "default" in plain
    assert "converge" in colored
    assert "converge" in plain


def test_format_log_level_basic() -> None:
    """Test format_log_level method basic functionality."""
    ansi_output = AnsiOutput()

    colored, plain = ansi_output.format_log_level("INFO")

    # Both should contain the level name
    assert "INFO" in colored
    assert "INFO" in plain


@pytest.mark.parametrize(
    "level_name",
    (
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
        "DEBUG",
    ),
)
def test_format_log_level_various_levels(level_name: str) -> None:
    """Test format_log_level method with various log levels."""
    ansi_output = AnsiOutput()

    colored, plain = ansi_output.format_log_level(level_name)

    # Both should contain the level name
    assert level_name in colored
    assert level_name in plain


def test_process_markup_complex() -> None:
    """Test processing of complex markup with multiple tags."""
    ansi_output = AnsiOutput()

    # Test nested and sequential markup
    complex_text = "[scenario]test[/] [action]action[/] [bold]bold[/]"
    result = ansi_output.process_markup(complex_text)

    # Should contain the text content
    assert "test" in result
    assert "action" in result
    assert "bold" in result

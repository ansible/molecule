"""Tests for the command borders functionality in ansi_output module."""

from __future__ import annotations

import io
import re
import sys

import pytest

from molecule.ansi_output import (
    AnsiOutput,
    BorderedStream,
    CommandBorders,
    get_line_style,
    split_command_to_strings,
)
from molecule.constants import ANSICodes as A


def test_split_command_to_strings_simple_command() -> None:
    """Test split_command_to_strings with a simple command."""
    command = "ansible-playbook playbook.yml"
    result = split_command_to_strings(command)
    expected = ["ansible-playbook", "playbook.yml"]
    assert result == expected


def test_split_command_to_strings_option_value_merging() -> None:
    """Test split_command_to_strings with option-value pairs (standard shlex behavior)."""
    command = "ansible-playbook -i inventory.yml --extra-vars var=value playbook.yml"
    result = split_command_to_strings(command)
    expected = [
        "ansible-playbook",
        "-i",
        "inventory.yml",
        "--extra-vars",
        "var=value",
        "playbook.yml",
    ]
    assert result == expected


def test_split_command_to_strings_empty_command() -> None:
    """Test split_command_to_strings with empty command."""
    command = ""
    result = split_command_to_strings(command)
    expected: list[str] = []
    assert result == expected


def test_split_command_to_strings_with_equals() -> None:
    """Test split_command_to_strings handles existing equals signs."""
    command = "ansible-playbook --extra-vars=existing=value playbook.yml"
    result = split_command_to_strings(command)
    expected = ["ansible-playbook", "--extra-vars=existing=value", "playbook.yml"]
    assert result == expected


def test_split_command_to_strings_long_options() -> None:
    """Test split_command_to_strings with long options (standard shlex behavior)."""
    command = "ansible-playbook --check --diff --verbose playbook.yml"
    result = split_command_to_strings(command)
    expected = ["ansible-playbook", "--check", "--diff", "--verbose", "playbook.yml"]
    assert result == expected


def test_split_command_to_strings_short_options() -> None:
    """Test split_command_to_strings with short options (standard shlex behavior)."""
    command = "ansible-playbook -v -C playbook.yml"
    result = split_command_to_strings(command)
    expected = ["ansible-playbook", "-v", "-C", "playbook.yml"]
    assert result == expected


@pytest.mark.parametrize(
    ("input_line", "expected"),
    (
        ("", ""),
        ("plain text", ""),
        ("\x1b[1mBold text\x1b[0m", "\x1b[1m"),
        ("\x1b[31mRed text\x1b[0m", "\x1b[31m"),
        ("\x1b[32;1mGreen bold\x1b[0m", "\x1b[32;1m"),
        ("\033[33mYellow\033[0m", "\033[33m"),
        ("\x1b[0mReset only", ""),  # Reset sequences are ignored
    ),
    ids=[
        "empty_string",
        "plain_text_no_ansi",
        "bold_formatting",
        "red_color",
        "green_bold_combination",
        "yellow_octal_escape",
        "reset_sequence_only",
    ],
)
def test_get_line_style(input_line: str, expected: str) -> None:
    """Test get_line_style extracts ANSI escape sequences properly."""
    result = get_line_style(input_line)
    assert result == expected


def test_get_line_style_returns_first_style() -> None:
    """Test get_line_style returns only the first non-reset style."""
    line = "\x1b[1mBold\x1b[0m text \x1b[32mGreen\x1b[0m"
    result = get_line_style(line)
    # Should return the first non-reset style
    assert result == "\x1b[1m"


def test_bordered_stream_init() -> None:
    """Test BorderedStream initialization."""
    ansi = AnsiOutput()
    original_stream = io.StringIO()
    stream = BorderedStream(ansi, original_stream)

    assert stream.ansi is ansi
    assert stream.target_stream is original_stream
    assert stream.buffer.getvalue() == ""


def test_bordered_stream_write_with_ansi_output() -> None:
    """Test BorderedStream.write with AnsiOutput integration."""
    # Test constants
    hello_world_length = 12  # Length of "Hello world\n"

    ansi = AnsiOutput()
    original_stream = io.StringIO()
    stream = BorderedStream(ansi, original_stream)

    result = stream.write("Hello world\n")

    assert result == hello_world_length  # Length of input
    output = original_stream.getvalue()
    assert A.BOX_VERTICAL in output


def test_bordered_stream_write_partial_line() -> None:
    """Test BorderedStream write with partial line (no newline)."""
    ansi = AnsiOutput()
    original_stream = io.StringIO()

    stream = BorderedStream(ansi, original_stream)
    stream.write("Partial")

    # Should buffer partial line
    assert stream.buffer.getvalue() == "Partial"
    assert original_stream.getvalue() == ""


def test_bordered_stream_write_multiple_lines() -> None:
    """Test BorderedStream write with multiple lines."""
    # Test constants
    expected_border_lines = 3  # Number of lines with borders

    ansi = AnsiOutput()
    original_stream = io.StringIO()

    stream = BorderedStream(ansi, original_stream)
    stream.write("Line 1\nLine 2\nLine 3\n")

    output = original_stream.getvalue()
    lines = output.split("\n")

    # Should have 3 lines with borders
    border_lines = [line for line in lines if A.BOX_VERTICAL in line]
    assert len(border_lines) == expected_border_lines

    # Each line should contain the expected text
    assert "Line 1" in output
    assert "Line 2" in output
    assert "Line 3" in output


def test_bordered_stream_flush() -> None:
    """Test BorderedStream flush method."""
    ansi = AnsiOutput()
    original_stream = io.StringIO()

    stream = BorderedStream(ansi, original_stream)
    stream.write("Test")
    stream.flush()

    # Should flush partial line
    output = original_stream.getvalue()
    assert A.BOX_VERTICAL in output
    assert "Test" in output
    assert stream.buffer.getvalue() == ""


def test_bordered_stream_getvalue() -> None:
    """Test BorderedStream getvalue method."""
    ansi = AnsiOutput()
    original_stream = io.StringIO()

    stream = BorderedStream(ansi, original_stream)
    stream.write("Test line\n")

    # getvalue returns the buffer content, not the original stream
    result = stream.getvalue()
    assert "Test line\n" in result


def test_command_borders_basic_functionality(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CommandBorders basic functionality."""
    # Override the autouse _no_color fixture
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")

    original_stderr = io.StringIO()
    borders = CommandBorders("echo hello", original_stderr)

    # Test that streams are captured
    assert borders.stdout_capture is not None
    assert borders.stderr_capture is not None

    # Test finalization - it now returns None
    borders.finalize(0)

    # Check that footer was written
    output = original_stderr.getvalue()
    assert "Return code: 0" in output


def test_command_borders_enabled_when_markup(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CommandBorders redirects streams when markup is enabled."""
    monkeypatch.setattr("molecule.ansi_output.should_do_markup", lambda: True)

    original_stdout = sys.stdout
    original_stderr = sys.stderr

    stderr_mock = io.StringIO()

    # Mock sys.stderr to capture header output
    monkeypatch.setattr(sys, "stderr", stderr_mock)

    _borders = CommandBorders("echo test", stderr_mock)

    # Should have changed stdout/stderr to BorderedStream instances
    assert sys.stdout is not original_stdout
    assert sys.stderr is not original_stderr
    assert isinstance(sys.stdout, BorderedStream)
    assert isinstance(sys.stderr, BorderedStream)

    # Should have printed header during construction
    output = stderr_mock.getvalue()
    assert A.BOX_TOP_LEFT in output
    # Command gets split across lines, so check for both parts
    assert "echo" in output
    assert "test" in output

    # Restore streams
    monkeypatch.setattr(sys, "stdout", original_stdout)
    monkeypatch.setattr(sys, "stderr", original_stderr)


def test_command_borders_finalize_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CommandBorders finalize with successful return code."""
    monkeypatch.setattr("molecule.ansi_output.should_do_markup", lambda: True)

    original_stdout = sys.stdout
    original_stderr = sys.stderr
    stderr_mock = io.StringIO()

    # Mock sys.stderr to capture output
    monkeypatch.setattr(sys, "stderr", stderr_mock)

    borders = CommandBorders("echo test", stderr_mock)

    # Clear the header output to focus on footer
    stderr_mock.seek(0)
    stderr_mock.truncate(0)

    borders.finalize(0)

    # Should restore streams - but finalize restores to what was saved at construction time
    # Since we set stderr_mock before construction, it will restore to stderr_mock
    assert sys.stdout is original_stdout
    # Manually restore stderr for this test
    monkeypatch.setattr(sys, "stderr", original_stderr)

    # Should have printed footer with success
    footer_output = stderr_mock.getvalue()
    assert A.BOX_BOTTOM_LEFT in footer_output
    assert "Return code: 0" in footer_output  # More specific check


def test_command_borders_finalize_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CommandBorders finalize with failure return code."""
    monkeypatch.setattr("molecule.ansi_output.should_do_markup", lambda: True)

    original_stdout = sys.stdout
    original_stderr = sys.stderr
    stderr_mock = io.StringIO()

    # Temporarily replace stderr for the constructor
    monkeypatch.setattr(sys, "stderr", stderr_mock)

    borders = CommandBorders("echo test", stderr_mock)

    # Clear the header output to focus on footer
    stderr_mock.seek(0)
    stderr_mock.truncate(0)

    borders.finalize(1)

    # Should restore streams - but finalize restores to what was saved at construction time
    # Since we set stderr_mock before construction, it will restore to stderr_mock
    assert sys.stdout is original_stdout
    # Manually restore stderr for this test
    monkeypatch.setattr(sys, "stderr", original_stderr)

    # Should have printed footer with failure
    footer_output = stderr_mock.getvalue()
    assert A.BOX_BOTTOM_LEFT in footer_output
    assert "Return code: 1" in footer_output  # More specific check


def test_command_borders_custom_width(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CommandBorders with custom width."""
    # Test constants
    custom_width = 50  # Custom border width for testing

    monkeypatch.setattr("molecule.ansi_output.should_do_markup", lambda: True)

    original_stderr = sys.stderr
    stderr_mock = io.StringIO()

    # Mock sys.stderr to capture output
    monkeypatch.setattr(sys, "stderr", stderr_mock)

    borders = CommandBorders("echo test", stderr_mock, width=custom_width)
    assert borders.width == custom_width

    # Check that header uses custom width
    header_output = stderr_mock.getvalue()
    # Count horizontal characters in the border
    horizontal_count = header_output.count(A.BOX_HORIZONTAL)
    # Should be using custom width (minus corners and spaces)
    assert horizontal_count > 0

    # Restore stderr
    monkeypatch.setattr(sys, "stderr", original_stderr)


def test_command_borders_format_command_lines_simple(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CommandBorders formats simple commands properly."""
    monkeypatch.setattr("molecule.ansi_output.should_do_markup", lambda: True)

    stderr_mock = io.StringIO()
    borders = CommandBorders("echo test", stderr_mock)

    # Test with simple string command
    lines = borders._format_command_lines("echo test", max_width=100)
    assert lines == ["echo test"]

    # Test with simple list command
    lines = borders._format_command_lines(["echo", "test"], max_width=100)
    assert lines == ["echo test"]


def test_command_borders_format_command_lines_flag_value_grouping(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test CommandBorders groups flags with their values intelligently."""
    monkeypatch.setattr("molecule.ansi_output.should_do_markup", lambda: True)

    stderr_mock = io.StringIO()
    borders = CommandBorders("test", stderr_mock)

    # Test flag-value grouping
    cmd = [
        "ansible-playbook",
        "--inventory",
        "/path/to/inventory",
        "--skip-tags",
        "notest",
        "playbook.yml",
    ]
    lines = borders._format_command_lines(cmd, max_width=100)

    # Should group executable with first flag-value pair
    assert lines[0] == "ansible-playbook --inventory /path/to/inventory"
    # Subsequent flag-value pairs should be grouped and indented
    assert "  --skip-tags notest" in lines
    # Positional args should be separate and indented
    assert "  playbook.yml" in lines


def test_command_borders_format_command_lines_line_wrapping(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test CommandBorders handles line wrapping correctly."""
    monkeypatch.setattr("molecule.ansi_output.should_do_markup", lambda: True)

    stderr_mock = io.StringIO()
    borders = CommandBorders("test", stderr_mock)

    # Long command that should wrap
    very_long_path = "/very/long/path/to/some/file/that/exceeds/the/terminal/width.yml"
    cmd = ["ansible-playbook", "--inventory", very_long_path]
    lines = borders._format_command_lines(cmd, max_width=50)

    # Should have multiple lines due to wrapping
    assert len(lines) > 1
    # First line should contain the executable
    assert "ansible-playbook" in lines[0]
    # Subsequent lines should be indented (or be wrapped parts of the first line)
    assert any(line.startswith(("  ", "/")) for line in lines[1:])


def test_command_borders_format_command_lines_multiple_flags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test CommandBorders handles multiple flags and values correctly."""
    monkeypatch.setattr("molecule.ansi_output.should_do_markup", lambda: True)

    stderr_mock = io.StringIO()
    borders = CommandBorders("test", stderr_mock)

    cmd = [
        "ansible-playbook",
        "--inventory",
        "inventory.yml",
        "--extra-vars",
        "key=value",
        "--tags",
        "tag1,tag2",
        "--limit",
        "host1",
        "playbook.yml",
    ]
    lines = borders._format_command_lines(cmd, max_width=200)

    # Should group flags with their values
    combined = " ".join(lines)
    assert "--inventory inventory.yml" in combined
    assert "--extra-vars key=value" in combined
    assert "--tags tag1,tag2" in combined
    assert "--limit host1" in combined
    assert "playbook.yml" in combined


def test_command_borders_format_command_lines_standalone_flags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test CommandBorders handles standalone flags (no values) correctly."""
    monkeypatch.setattr("molecule.ansi_output.should_do_markup", lambda: True)

    stderr_mock = io.StringIO()
    borders = CommandBorders("test", stderr_mock)

    cmd = ["ansible-playbook", "--check", "--diff", "--verbose", "playbook.yml"]
    lines = borders._format_command_lines(cmd, max_width=200)

    # Standalone flags should be on separate lines
    combined = " ".join(lines)
    assert "ansible-playbook" in combined
    assert "--check" in combined
    assert "--diff" in combined
    assert "--verbose" in combined
    assert "playbook.yml" in combined


def test_bordered_stream_handles_ansi_sequences() -> None:
    """Test BorderedStream properly handles ANSI escape sequences."""
    ansi = AnsiOutput()
    original_stream = io.StringIO()

    stream = BorderedStream(ansi, original_stream)
    stream.write("\x1b[31mRed text\x1b[0m\n")

    output = original_stream.getvalue()
    assert A.BOX_VERTICAL in output
    assert "\x1b[31m" in output  # ANSI codes should be preserved
    assert "Red text" in output


def test_bordered_stream_continuation_styling() -> None:
    """Test BorderedStream applies continuation styling correctly."""
    # Test constants
    expected_border_lines = 2  # Number of lines with borders

    ansi = AnsiOutput()
    original_stream = io.StringIO()

    stream = BorderedStream(ansi, original_stream)

    # Write a styled line, then a continuation
    stream.write("\x1b[32mGreen line\x1b[0m\n")
    stream.write("Continuation\n")

    output = original_stream.getvalue()
    lines = output.split("\n")

    # Both lines should have borders
    border_lines = [line for line in lines if A.BOX_VERTICAL in line]
    assert len(border_lines) == expected_border_lines

    # First line has explicit styling
    assert "\x1b[32m" in border_lines[0]
    assert "Green line" in border_lines[0]

    # Second line should have continuation
    assert "Continuation" in border_lines[1]


def test_split_command_to_strings_handles_complex_args() -> None:
    """Test split_command_to_strings with complex arguments (standard shlex behavior)."""
    command = "ansible-playbook -e key=value --tags tag1,tag2 --limit host1:host2 playbook.yml"
    result = split_command_to_strings(command)

    assert "ansible-playbook" in result
    assert "-e" in result
    assert "key=value" in result
    assert "--tags" in result
    assert "tag1,tag2" in result
    assert "--limit" in result
    assert "host1:host2" in result
    assert "playbook.yml" in result


def test_bordered_stream_wraps_long_lines() -> None:
    """Test BorderedStream wraps long lines using textwrap with proper indentation and color preservation."""
    ansi = AnsiOutput()
    original_stream = io.StringIO()

    stream = BorderedStream(ansi, original_stream)

    # Create a very long line with ANSI color that will exceed terminal width
    long_line = "\x1b[32mThis is a very long green line that contains a lot of text and should be wrapped by textwrap when it exceeds the terminal width minus the border characters overhead\x1b[0m"
    stream.write(f"{long_line}\n")

    output = original_stream.getvalue()
    lines = output.split("\n")

    # Should have multiple lines due to wrapping
    border_lines = [line for line in lines if A.BOX_VERTICAL in line]
    assert len(border_lines) > 1

    # All border lines should contain the box vertical character
    for line in border_lines:
        assert A.BOX_VERTICAL in line

    # Check that continuation lines are indented (have 2 extra spaces after the border)
    continuation_lines = border_lines[1:]  # All lines except the first
    for line in continuation_lines:
        # After removing ANSI codes and finding the content after "│ ", it should start with 2 spaces
        clean_line = re.sub(r"\x1b\[[0-9;]*m", "", line)
        if "│" in clean_line:
            content = clean_line.split("│ ", 1)[-1]
            assert content.startswith("  "), (
                f"Continuation line should start with 2 spaces: '{content}'"
            )

    # Check that original color is preserved in all wrapped lines
    for line in border_lines:
        assert "\x1b[32m" in line, "Original green color should be preserved in all wrapped lines"

    # Reconstruct the original text from bordered output (removing indentation)
    reconstructed_parts = []
    for i, line in enumerate(border_lines):
        # First remove ANSI escape codes, then split on the vertical bar
        clean_line = re.sub(r"\x1b\[[0-9;]*m", "", line)
        if "│" in clean_line:
            text_part = clean_line.split("│ ", 1)[-1]
            # Remove the 2-space indentation from continuation lines
            if i > 0 and text_part.startswith("  "):
                text_part = text_part[2:]
            reconstructed_parts.append(text_part)

    # When joined with spaces, should contain the original text content
    reconstructed = " ".join(reconstructed_parts)
    assert "This is a very long green line" in reconstructed
    assert "should be wrapped by textwrap" in reconstructed
    assert "terminal width minus the border characters overhead" in reconstructed

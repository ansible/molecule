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

import io
import os
import re
import shlex
import shutil
import sys

from pathlib import Path
from typing import TYPE_CHECKING

from molecule.constants import DEFAULT_BORDER_WIDTH, MARKUP_MAP, SCENARIO_RECAP_STATE_ORDER
from molecule.constants import ANSICodes as A
from molecule.util import boolean


if TYPE_CHECKING:
    from typing import TextIO

    from typing_extensions import Self

    from molecule.reporting.definitions import ScenariosResults


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
            py_colors = boolean(value, default=False)
            break

    # If deliberately disabled colors
    if os.environ.get("NO_COLOR", None):
        return False

    # User configuration requested colors
    if py_colors is not None:
        return boolean(py_colors)

    term = os.environ.get("TERM", "")
    if "xterm" in term:
        return True

    if term == "dumb":
        return False

    # Use tty detection logic as last resort
    return sys.stdout.isatty()


def split_command_to_strings(cmd: str | list[str]) -> list[str]:
    """Split command into properly formatted strings for display.

    Args:
        cmd: Command as string or list

    Returns:
        List of command argument strings
    """
    if isinstance(cmd, str):
        return shlex.split(cmd)
    return [str(arg) for arg in cmd]


def get_line_style(line: str) -> str:
    """Extract ANSI escape sequences from beginning of line for style preservation.

    Args:
        line: Input line that may contain ANSI codes

    Returns:
        ANSI escape sequence from start of line without reset codes, or empty string if none
    """
    # Match ANSI escape sequences at the start of the line
    # Patterns: \x1b[...m or \033[...m
    match = re.match(r"^(\x1b\[[0-9;]*m|\033\[[0-9;]*m)", line)
    if match:
        escape_seq = match.group(1)

        # Skip pure reset sequences (just \x1b[0m)
        if escape_seq in ["\x1b[0m", "\033[0m"]:
            return ""

        # Extract color from reset+color sequences (e.g., \x1b[0;32m -> \x1b[32m)
        # This prevents reset codes from canceling our DIM formatting
        if ";3" in escape_seq and escape_seq.startswith(("\x1b[0;", "\033[0;")):
            # Extract just the color part (30-37 for standard colors)
            color_match = re.search(r"(3[0-7])m", escape_seq)
            if color_match:
                color_code = color_match.group(1)
                # Use \x1b prefix consistently (most common format)
                return f"\x1b[{color_code}m"

        # Skip other reset sequences (ending with 0m but not just 0m)
        # Length 5 is minimum for reset+color (\x1b[0m = 5 chars)
        min_reset_color_length = 5
        if escape_seq.endswith("0m") and len(escape_seq) > min_reset_color_length:
            return ""

        return escape_seq
    return ""


class AnsiOutput:
    """ANSI output formatter with Rich-style markup support.

    Converts Rich-style markup tags to ANSI escape codes while respecting
    color configuration and providing reusable formatting functionality.
    """

    def __init__(self) -> None:
        """Initialize the ANSI output formatter."""
        # Remove caching - markup_enabled is now a property

    @property
    def markup_enabled(self) -> bool:
        """Check if markup should be enabled, evaluated each time.

        This ensures that environment variable changes (like NO_COLOR=1 in tests)
        are immediately respected without needing to recreate the AnsiOutput instance.
        """
        return should_do_markup()

    def strip_markup(self, text: str) -> str:
        """Strip all Rich-style markup tags from text.

        Args:
            text: Text containing Rich markup tags.

        Returns:
            Text with all markup tags removed.
        """
        return re.sub(r"\[/?[^\]]*\]", "", str(text))

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
            try:
                return MARKUP_MAP[tag]
            except KeyError:
                try:
                    return str(getattr(A, tag.upper()))
                except AttributeError:
                    return ""

        # Match tags that don't start with /
        processed = re.sub(r"\[([^/\]]+)\]", replace_tag, text)

        # Process closing tags last (convert [/] to reset)
        result = re.sub(r"\[/\]", A.RESET, processed)
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
            markup_text = rf"[scenario]{scenario_name}[/] {A.RIGHT_ARROW} [action]{step}[/]:"
        else:
            markup_text = rf"[scenario]{scenario_name}[/]"

        colored = self.process_markup(markup_text)
        plain = self.strip_markup(markup_text)
        return colored, plain

    def format_completion_message(self, message: str, color: str) -> str:
        """Format completion message with conditional colors.

        Low-level formatter for just the completion part.
        Used by both logging and reporting systems.

        Args:
            message: The plain text completion message (e.g., "Executed: Successful")
            color: The ANSI color code (e.g., ANSICodes.GREEN, ANSICodes.RED)

        Returns:
            Formatted message with or without ANSI codes based on markup_enabled setting.
        """
        if not self.markup_enabled:
            return message
        return f"{color}{message}{A.RESET}"

    def format_completion_note(self, note: str) -> str:
        """Format completion note with conditional dim styling.

        Args:
            note: The note text to format

        Returns:
            Formatted note with conditional styling based on markup_enabled setting.
        """
        if not self.markup_enabled:
            return f" ({note})"
        return f" {A.DIM}({note}){A.RESET}"

    def format_full_completion_line(
        self,
        scenario_name: str,
        action_name: str,
        completion_message: str,
        color: str | A,
        note: str | None = None,
    ) -> str:
        """Format complete scenario → action: completion line.

        High-level formatter that combines all parts.
        Used by reporting system and can be used to verify logging output.

        Args:
            scenario_name: Name of the scenario (e.g., "default")
            action_name: Name of the action (e.g., "converge", "cleanup")
            completion_message: The completion message (e.g., "Executed: Successful")
            color: The ANSI color code (string) or ANSICodes enum value
            note: Optional note to append

        Returns:
            Complete formatted line with Rich markup for reporting system.
        """
        if self.markup_enabled:
            # Use Rich markup for reporting system
            scenario_part = (
                f"[scenario]{scenario_name}[/] {A.RIGHT_ARROW} [action]{action_name}[/]:"
            )
            # Handle both string colors and ANSICodes objects
            color_tag = color.tag if hasattr(color, "tag") else color
            completion_part = f"[{color_tag}]{completion_message}[/]"
            result = f"{scenario_part} {completion_part}"
            if note:
                result += f" [dim]({note})[/]"
        else:
            # Use plain text without brackets (brackets would be stripped by strip_markup)
            scenario_part = f"{scenario_name} > {action_name}:"
            result = f"{scenario_part} {completion_message}"
            if note:
                result += f" ({note})"

        return result

    def format_scenario_recap(self, results: ScenariosResults) -> str:
        """Format scenario recap similar to Ansible play recap.

        Args:
            results: The scenario results to format.

        Returns:
            Formatted recap string with ANSI colors if enabled.
        """
        # Import here to avoid circular imports
        from molecule.reporting.definitions import CompletionState  # noqa: PLC0415

        if not results:
            return ""

        lines = []

        # Header with bold and underline styling, padded to 79 characters
        header_text = "SCENARIO RECAP"
        header_padded = f"{header_text:<79}"
        header = self.process_markup(f"[bold][underline]{header_padded}[/]")
        lines.append(header)

        # Process each scenario
        for scenario_result in results:
            if not scenario_result.actions:
                continue

            scenario_name = scenario_result.name

            # Count completion states across all actions
            state_counts = dict.fromkeys(SCENARIO_RECAP_STATE_ORDER, 0)
            total_actions = 0

            for action_result in scenario_result.actions:
                if action_result.states:
                    # Count all individual states for this action
                    for state in action_result.states:
                        if state.state in state_counts:
                            state_counts[state.state] += 1
                total_actions += 1  # One action regardless of how many states it has

            # Create plain text version for length calculations
            scenario_plain = scenario_name

            # Pad scenario name to 26 characters (like Ansible's host field)
            scenario_padded_plain = f"{scenario_plain:<26}"

            # Apply colors to the padded plain text
            scenario_colored = self.process_markup(f"[scenario]{scenario_padded_plain}[/]")

            # Format counts with fixed field widths to ensure alignment
            # Only apply colors if count > 0 (matching Ansible behavior)
            actions_part = (
                self.process_markup(f"[action]actions={total_actions}[/]")
                if total_actions > 0
                else f"actions={total_actions}"
            )

            # Generate state parts dynamically using CompletionState colors
            state_parts = []
            for state_name in SCENARIO_RECAP_STATE_ORDER:
                count = state_counts[state_name]

                # Get the color tag from the CompletionState
                state_obj = getattr(CompletionState, state_name)
                color_tag = state_obj.color.tag

                if count > 0:
                    state_part = self.process_markup(f"[{color_tag}]{state_name}={count}[/]")
                else:
                    state_part = f"{state_name}={count}"

                state_parts.append(state_part)

            # Build line with consistent spacing to match expected format
            line = f"{scenario_colored}: {actions_part}  " + "  ".join(state_parts)
            lines.append(line)

        return "\n".join(lines)


class BorderedStream:
    """Stream wrapper that adds border characters to each line."""

    def __init__(self, ansi: AnsiOutput, target_stream: TextIO) -> None:
        """Initialize stream wrapper.

        Args:
            ansi: AnsiOutput instance for markup processing
            target_stream: Actual stream to write to
        """
        self.ansi = ansi
        self.target_stream = target_stream
        self.buffer = io.StringIO()
        self.partial_line = ""  # Track partial lines for proper concatenation

    def write(self, text: str) -> int:
        """Write text with border prefix.

        Args:
            text: Text to write

        Returns:
            Number of characters written
        """
        if not text:
            return 0

        # Add to buffer first for getvalue()
        self.buffer.write(text)

        # Concatenate new text with existing partial line FIRST, then split
        remaining = self.partial_line + text
        lines = remaining.split("\n")

        # Process all complete lines
        for line in lines[:-1]:
            # Calculate effective width accounting for border prefix
            terminal_width = shutil.get_terminal_size().columns
            border_prefix_width = len("  │ ")  # 4 characters: "  │ "
            continuation_indent_width = 2  # 2 additional spaces for continuation lines

            # Width available for first line
            first_line_width = terminal_width - border_prefix_width
            # Width available for continuation lines (less space due to indentation)
            continuation_width = terminal_width - border_prefix_width - continuation_indent_width

            if len(line) <= first_line_width:
                # Line fits, output directly
                line_style = get_line_style(line)
                styled_prefix = f"{A.DIM}{line_style}{A.BOX_VERTICAL}{A.RESET} "
                self.target_stream.write(f"  {styled_prefix}{line}\n")
            else:
                # Extract original line style to preserve color across wrapped lines
                original_style = get_line_style(line)

                # Strip ANSI codes for accurate width calculation
                clean_line = re.sub(r"\x1b\[[0-9;]*m", "", line)

                # Manual wrapping to handle different widths for first vs continuation lines
                wrapped_lines = []
                remaining_text = clean_line
                is_first = True

                while remaining_text:
                    # Use appropriate width for this line
                    current_width = first_line_width if is_first else continuation_width

                    if len(remaining_text) <= current_width:
                        # Remaining text fits in current line
                        wrapped_lines.append(remaining_text)
                        break
                    # Find best break point within width limit
                    break_point = remaining_text.rfind(" ", 0, current_width)
                    if break_point == -1:
                        # No space found, break at width limit
                        break_point = current_width

                    # Add this segment
                    wrapped_lines.append(remaining_text[:break_point])
                    remaining_text = remaining_text[break_point:].lstrip()
                    is_first = False

                # Output each wrapped line with proper styling and indentation
                for i, wrapped_line in enumerate(wrapped_lines):
                    _wrapped_line = wrapped_line
                    # Add 2 spaces indentation to continuation lines (all except first)
                    if i > 0:
                        _wrapped_line = "  " + _wrapped_line

                    # Apply original line style and color to maintain consistency
                    styled_prefix = f"{A.DIM}{original_style}{A.BOX_VERTICAL}{A.RESET} "
                    # Re-apply original color to the content
                    if original_style:
                        colored_content = f"{original_style}{_wrapped_line}{A.RESET}"
                    else:
                        colored_content = _wrapped_line
                    self.target_stream.write(f"  {styled_prefix}{colored_content}\n")

        # Store the remaining partial line
        self.partial_line = lines[-1]

        return len(text)

    def flush(self) -> None:
        """Flush the stream."""
        # Write any remaining partial line
        if self.partial_line:
            line_style = get_line_style(self.partial_line)
            styled_prefix = f"{A.DIM}{line_style}{A.BOX_VERTICAL}{A.RESET} "
            self.target_stream.write(f"  {styled_prefix}{self.partial_line}\n")
            self.partial_line = ""

        # Clear the buffer after flushing
        self.buffer = io.StringIO()
        self.target_stream.flush()

    def getvalue(self) -> str:
        """Get buffered content."""
        return self.buffer.getvalue()


class CommandBorders:
    """Manages command execution with visual borders."""

    def __init__(
        self,
        cmd: str | list[str],
        original_stderr: TextIO,
        width: int = DEFAULT_BORDER_WIDTH,
    ) -> None:
        """Initialize command borders.

        Args:
            cmd: Command to display
            original_stderr: Original stderr stream
            width: Border width
        """
        if not should_do_markup():
            return

        self.ansi = AnsiOutput()
        self.width = width
        self.runtime_stdout = sys.stdout
        self.runtime_stderr = sys.stderr
        self.original_stderr = original_stderr  # Store for header/footer printing
        self.stdout_capture = BorderedStream(self.ansi, original_stderr)  # Send stdout to stderr
        self.stderr_capture = BorderedStream(self.ansi, original_stderr)  # Keep stderr to stderr
        self._print_header_and_command(cmd)
        sys.stdout = self.stdout_capture
        sys.stderr = self.stderr_capture

    def _print_header_and_command(self, cmd: str | list[str]) -> None:
        """Print header with command details.

        Args:
            cmd: Command to display
        """
        # Print header to stderr (bypassing rich) using ANSI line drawing
        header = self._create_header_line("")
        self.original_stderr.write(f"  {A.DIM}{header}{A.RESET}\n")

        # Format and display command
        command_lines = self._format_command_lines(cmd)
        for line in command_lines:
            self.original_stderr.write(
                f"  {A.DIM}{A.BOX_VERTICAL} {line}{A.RESET}\n",
            )

        # Add blank line with pipe
        self.original_stderr.write(f"  {A.DIM}{A.BOX_VERTICAL}{A.RESET} \n")

    def _format_command_lines(  # noqa: C901, PLR0912
        self,
        cmd: str | list[str],
        max_width: int | None = None,
    ) -> list[str]:
        """Format command for display with proper line breaks.

        Args:
            cmd: Command string or list of command parts
            max_width: Optional maximum width for lines. If None, uses terminal width.

        Returns:
            List of formatted command lines
        """
        indent = "  "
        parts = split_command_to_strings(cmd)
        if not parts:
            return [""]

        decor = len("  | ")

        max_width = (
            shutil.get_terminal_size().columns - decor if max_width is None else max_width - decor
        )

        lines, i = [], 0

        # First line: exec + first param/flag/value
        first = parts[i]
        i += 1
        if i < len(parts):
            if parts[i].startswith("-"):
                first += " " + parts[i]
                i += 1
                if i < len(parts) and not parts[i].startswith("-"):
                    first += " " + parts[i]
                    i += 1
            else:
                first += " " + parts[i]
                i += 1
        lines.append(first)

        # Remaining flags/values and positional args
        while i < len(parts):
            part = parts[i]
            if part.startswith("-") and i + 1 < len(parts) and not parts[i + 1].startswith("-"):
                lines.append(part + " " + parts[i + 1])
                i += 2
            elif not part.startswith("-"):
                lines.append(part)
                i += 1
            else:
                lines.append(part)
                i += 1

        # Now wrap all lines
        wrapped = []
        for i, line in enumerate(lines):
            while len(line) > max_width:
                k = line.rfind(" ", 0, max_width)
                wrapped.append(line[: k if k != -1 else max_width])
                line = line[(k + 1) if k != -1 else max_width :]  # noqa: PLW2901
            if i > 0:
                wrapped.append(indent + line)
            else:
                wrapped.append(line)
        return wrapped

    def _create_header_line(self, text: str) -> str:
        """Create header line with text.

        Args:
            text: Text to include in header

        Returns:
            Formatted header line using ANSI drawing characters
        """
        if text:
            # Calculate padding for centered text
            content_len = len(text) + 2  # Add 2 for spaces around text
            padding = (self.width - content_len - 1) // 2  # -1 for corner
            remaining = self.width - content_len - padding - 1
            return f"{A.BOX_TOP_LEFT}{A.BOX_HORIZONTAL * padding} {text} {A.BOX_HORIZONTAL * remaining}"
        # Header without text
        return f"{A.BOX_TOP_LEFT}{A.BOX_HORIZONTAL * (self.width - 1)}"

    def _create_footer_line(self, return_code: int) -> str:
        """Create footer line with return code.

        Args:
            return_code: Command return code

        Returns:
            Formatted footer line using ANSI drawing characters
        """
        footer_text = f" Return code: {return_code} "
        padding = self.width - len(footer_text) - 2  # 2 = "└" + "─"
        return f"{A.BOX_BOTTOM_LEFT}{A.BOX_HORIZONTAL}{footer_text}" + A.BOX_HORIZONTAL * padding

    def _print_footer(self, return_code: int) -> None:
        """Print footer with return code.

        Args:
            return_code: Command return code
        """
        # Use simple color format to match extracted colors from get_line_style
        footer_color = A.GREEN if return_code == 0 else A.RED

        # Footer line to stderr (bypassing rich) using ANSI line drawing
        footer = self._create_footer_line(return_code)
        self.original_stderr.write(f"  {A.DIM}{footer_color}{footer}{A.RESET}\n")

    def finalize(self, return_code: int) -> None:
        """Finalize borders and restore streams.

        Args:
            return_code: Command return code
        """
        if not should_do_markup():
            return

        # Flush any remaining content
        self.stdout_capture.flush()
        self.stderr_capture.flush()

        # Restore original streams
        sys.stdout = self.runtime_stdout
        sys.stderr = self.runtime_stderr

        # Print footer
        self._print_footer(return_code)

    def __enter__(self) -> Self:
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Context manager exit."""
        return_code = 1 if exc_type else 0
        self.finalize(return_code)


def print_matrix(matrix_data: dict[str, list[str]], config: object | None = None) -> None:
    """Print the test matrix with colored output and file paths.

    Args:
        matrix_data: Dictionary mapping scenario names to their action sequences.
        config: Molecule config object to resolve playbook file paths.
    """
    output = AnsiOutput()

    # Get subcommand name for dynamic header
    subcommand = "test"  # default fallback
    if config and hasattr(config, "subcommand"):
        subcommand = config.subcommand

    header = f"{subcommand.title()} matrix"
    sys.stdout.write(f"\n{header}\n")
    sys.stdout.write("-" * len(header) + "\n")

    for scenario_name, actions in matrix_data.items():
        # Print scenario name in green
        scenario_markup = f"[scenario]{scenario_name}[/]"
        sys.stdout.write(output.process_markup(scenario_markup) + "\n")

        for i, action in enumerate(actions):
            # Use molecule's existing playbook resolution
            playbook_path = None
            if config and hasattr(config, "provisioner") and getattr(config, "provisioner", None):
                # Use public interface via property instead of private method
                provisioner = config.provisioner
                if hasattr(provisioner, "playbooks"):
                    playbook_property = getattr(provisioner.playbooks, action, None)
                    if playbook_property:
                        playbook_path = playbook_property

            # Choose tree character: └─ for last item, ├─ for others
            is_last = i == len(actions) - 1
            tree_char = (
                f"{A.BOX_BOTTOM_LEFT}{A.BOX_HORIZONTAL}"
                if is_last
                else f"{A.BOX_LEFT_MIDDLE}{A.BOX_HORIZONTAL}"
            )

            # Format action with file path or "Missing"
            action_markup = f"[action]{action}[/]"
            if playbook_path and Path(playbook_path).exists():
                # Show file path in dim
                file_info = f"[dim]{playbook_path}[/]"
                line = f"  {tree_char} {output.process_markup(action_markup)} {output.process_markup(file_info)}"
            else:
                # Show missing message consistent with rest of molecule
                subcommand = "test"  # default fallback
                if config and hasattr(config, "subcommand"):
                    subcommand = config.subcommand
                missing_info = (
                    f"[dim]Missing playbook (remove from {subcommand}_sequence to suppress)[/]"
                )
                line = f"  {tree_char} {output.process_markup(action_markup)} {output.process_markup(missing_info)}"

            sys.stdout.write(line + "\n")

        sys.stdout.write("\n")  # Empty line between scenarios

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

from typing import TYPE_CHECKING

from molecule.constants import MARKUP_MAP, SCENARIO_RECAP_STATE_ORDER
from molecule.constants import ANSICodes as A


if TYPE_CHECKING:
    from molecule.reporting import ScenariosResults


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
            message: The plain text completion message (e.g., "Completed: Successful")
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
            completion_message: The completion message (e.g., "Completed: Successful")
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
        from molecule.reporting import CompletionState  # noqa: PLC0415

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

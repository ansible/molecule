"""Rendering and output functionality for reporting."""

from __future__ import annotations

from typing import TYPE_CHECKING

from molecule.ansi_output import AnsiOutput
from molecule.console import original_stderr
from molecule.logger import get_logger


if TYPE_CHECKING:
    from .definitions import ScenariosResults


def report(results: ScenariosResults, *, report_flag: bool) -> None:
    """Report the results of the scenario.

    Args:
        results: The results of the scenario.
        report_flag: Value of the --report flag from user (True = show details, False = summary only).
    """
    if not results:
        return

    # ALWAYS show one-line summary with appropriate log level
    overall_state, summary_line = results.get_overall_summary()

    # Log at the appropriate level based on highest priority completion state
    log = get_logger(__name__)
    getattr(log, overall_state.log_level)(summary_line)

    # Show detailed sections ONLY if --report flag was provided by user
    if report_flag:
        ao = AnsiOutput()

        # Details section header (bold and underlined), padded to 79 characters
        details_text = "DETAILS"
        details_padded = f"{details_text:<79}"
        details_header = f"\n[bold][underline]{details_padded}[/]"
        original_stderr.write(ao.process_markup(details_header))
        original_stderr.write("\n")

        # Details section content - show completion status for each action
        for scenario_result in results:
            if not scenario_result.actions:
                continue
            for action_result in scenario_result.actions:
                line = ao.format_full_completion_line(
                    scenario_name=scenario_result.name,
                    action_name=action_result.action or "unknown",
                    completion_message=action_result.summary.message,
                    color=action_result.summary.color,
                    note=action_result.summary.note,
                )
                original_stderr.write(ao.process_markup(line))
                original_stderr.write("\n")
            original_stderr.write("\n")

        # Scenario recap section - dynamically generated from CompletionState
        recap = ao.format_scenario_recap(results)
        if recap:
            original_stderr.write(recap)
            original_stderr.write("\n\n")

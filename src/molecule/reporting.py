"""All reporting logic for Molecule."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import cast

from molecule.ansi_output import AnsiOutput
from molecule.console import original_stderr
from molecule.constants import ANSICodes as A


def report(results: ScenariosResults) -> None:
    """Report the results of the scenario.

    Args:
        results: The results of the scenario.
    """
    ao = AnsiOutput()
    report_header = "\n[bold][underline]Summary[/][/]"
    original_stderr.write(ao.process_markup(report_header))
    original_stderr.write("\n")
    for scenario_result in results:
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


class CompletionStateInfo:
    """Completion state information with intuitive __call__ interface for custom messages.

    Provides both direct access for standard states and callable syntax for custom messages:
    - CompletionState.successful (standard usage)
    - CompletionState.partial("2 successful, 1 failed") (custom message)
    """

    def __init__(
        self,
        state: str,
        log_level: str,
        color: A,
        message: str | None = None,
        note: str | None = None,
    ) -> None:
        """Initialize completion state info.

        Args:
            state: The state name (e.g., 'successful', 'failed')
            log_level: Logging level ('info', 'warning', 'error')
            color: ANSI color code
            message: Optional custom message (defaults to state.title())
            note: Optional note to add to the completion state
        """
        self.state = state
        self.log_level = log_level
        self.color = color
        self._message = message  # Private storage to avoid recursion
        self._note = note

    @property
    def message(self) -> str:
        """Get the user-facing completion message."""
        return f"Completed: {self._message or self.state.title()}"

    @property
    def note(self) -> str | None:
        """Get the note for the completion state."""
        return self._note

    def __call__(self, message: str | None = None, note: str | None = None) -> CompletionStateInfo:
        """Create new instance with custom message.

        Args:
            message: Optional custom message text
            note: Optional note to add to the completion state
        Returns:
            New CompletionStateInfo instance with the custom message
        """
        if message is None and note is None:
            return self

        return CompletionStateInfo(
            state=self.state,
            log_level=self.log_level,
            color=self.color,
            message=message or self._message,
            note=note,
        )


class CompletionState:
    """Container for all completion states with beautiful __call__ interface.

    Standard usage: CompletionState.successful
    Custom messages: CompletionState.partial("2 successful, 1 failed")

    Attributes:
        disabled: Disabled state.
        failed: Failed state.
        missing: Missing state.
        partial: Partial state.
        skipped: Skipped state.
        successful: Successful state.
    """

    disabled = CompletionStateInfo(state="disabled", log_level="info", color=A.CYAN)
    failed = CompletionStateInfo(state="failed", log_level="error", color=A.RED)
    missing = CompletionStateInfo(state="missing", log_level="warning", color=A.MAGENTA)
    partial = CompletionStateInfo(state="partial", log_level="info", color=A.GREEN)
    skipped = CompletionStateInfo(state="skipped", log_level="info", color=A.CYAN)
    successful = CompletionStateInfo(state="successful", log_level="info", color=A.GREEN)


@dataclass
class ActionResult:
    """Result of a single action execution with flexible state input.

    Attributes:
        action: The action that ran (e.g., 'create', 'converge', 'destroy').
        states: List of completion states from this action execution.
                Most actions have 1 state, verify/side_effect can have multiple.
    """

    action: str | None
    states: list[CompletionStateInfo] = field(default_factory=list)

    def append(self, state: CompletionStateInfo) -> None:
        """Append a new completion state to the list of states.

        Args:
            state: The completion state to append.
        """
        self.states.append(state)

    @property
    def summary(self) -> CompletionStateInfo:
        """Analyze the latest action execution and return appropriate completion state.

        Performs dynamic result analysis based on the most recent ActionResult:
        - 0 results: Success (command completed without issues)
        - 1 state: Use that state directly
        - 2+ states: Multi-state analysis (partial, all failed, etc.)

        Returns:
            CompletionStateInfo instance with appropriate log_level, color, and message
        """
        if not self.states:
            return CompletionState.successful

        if len(self.states) == 1:
            return self.states[0]

        counts = Counter([state.state for state in self.states])
        parts = [f"{number} {name}" for name, number in counts.items()]
        partial_message = f"{', '.join(parts)}"

        ranks = ("failed", "missing", "skipped", "disabled", "successful")
        states = [state.state for state in self.states]
        notes = {state.note for state in self.states if state.note}
        notes = {state.note for state in self.states if state.note}
        note = None if not notes else next(iter(notes)) if len(notes) == 1 else "See details above"

        for rank in ranks:
            if rank in states:
                return cast("CompletionStateInfo", getattr(CompletionState, rank))(
                    message=partial_message,
                    note=note,
                )

        return CompletionState.partial(partial_message)


@dataclass
class ScenarioResults:
    """Dictionary containing results from a single scenario.

    Attributes:
        name: The scenario name.
        actions: All action results from this scenario's execution.
    """

    name: str
    actions: list[ActionResult]

    def add_action_result(self, action: str) -> None:
        """Add a action result to the scenario result.

        Args:
            action: The action to add.
        """
        self.actions.append(ActionResult(action=action, states=[]))

    def add_completion(self, completion: CompletionStateInfo) -> None:
        """Add a completion to the scenario result.

        Args:
            completion: The completion to add.
        """
        self.actions[-1].append(completion)

    @property
    def last_action_summary(self) -> CompletionStateInfo:
        """Get the last completion state from the scenario result.

        Returns:
            The last completion state.
        """
        return self.actions[-1].summary


class ScenariosResults(list[ScenarioResults]):
    """A list of all scenarios and their results."""

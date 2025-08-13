"""Data structures and business logic for reporting."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import cast

from molecule.constants import COMPLETION_STATE_COLORS, COMPLETION_STATE_PRIORITY_ORDER
from molecule.constants import ANSICodes as A


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
        return f"Executed: {self._message or self.state.title()}"

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

    disabled = CompletionStateInfo(
        state="disabled",
        log_level="info",
        color=COMPLETION_STATE_COLORS["disabled"],
    )
    failed = CompletionStateInfo(
        state="failed",
        log_level="error",
        color=COMPLETION_STATE_COLORS["failed"],
    )
    missing = CompletionStateInfo(
        state="missing",
        log_level="warning",
        color=COMPLETION_STATE_COLORS["missing"],
    )
    partial = CompletionStateInfo(
        state="partial",
        log_level="info",
        color=COMPLETION_STATE_COLORS["partial"],
    )
    skipped = CompletionStateInfo(
        state="skipped",
        log_level="info",
        color=COMPLETION_STATE_COLORS["skipped"],
    )
    successful = CompletionStateInfo(
        state="successful",
        log_level="info",
        color=COMPLETION_STATE_COLORS["successful"],
    )


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
        - 0 results: Success (command executed without issues)
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

        states = [state.state for state in self.states]
        notes = {state.note for state in self.states if state.note}
        note = None if not notes else next(iter(notes)) if len(notes) == 1 else "See details above"

        for rank in COMPLETION_STATE_PRIORITY_ORDER:
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

    @property
    def completion_state(self) -> CompletionStateInfo:
        """Get the overall completion state for this scenario.

        Leverages ActionResult.summary logic by treating all actions in this scenario
        as states of a single "meta-action" representing the entire scenario.

        Returns:
            CompletionStateInfo representing this scenario's overall outcome.
        """
        if not self.actions:
            return CompletionState.successful

        # Create a temporary ActionResult containing all states from all actions
        # This lets us reuse the existing summary logic
        meta_action = ActionResult(action="scenario", states=[])

        for action in self.actions:
            # Add each action's summary state to our meta-action
            meta_action.append(action.summary)

        # Let ActionResult.summary handle the priority logic for us
        return meta_action.summary


class ScenariosResults(list[ScenarioResults]):
    """A list of all scenarios and their results."""

    def get_overall_summary(self) -> tuple[CompletionStateInfo, str]:
        """Generate overall summary for entire molecule run.

        Uses each scenario's completion_state to determine overall status
        and generate a concise one-line summary.

        Returns:
            Tuple of (highest_priority_state, one_line_summary)
        """
        if not self:
            return CompletionState.successful, "Molecule executed 0 scenarios"

        # Get completion state for each scenario (let each scenario determine its own state)
        scenario_states = [scenario.completion_state for scenario in self]

        # Find highest priority overall state
        highest_priority_state = CompletionState.successful
        for priority_state in COMPLETION_STATE_PRIORITY_ORDER:
            if any(state.state == priority_state for state in scenario_states):
                highest_priority_state = getattr(CompletionState, priority_state)
                break

        # Count scenario completion states
        state_counts = Counter(state.state for state in scenario_states)

        # Generate colored count parts using PRIORITY order (failed first, etc.)
        count_parts = []
        # Use COMPLETION_STATE_PRIORITY_ORDER to show most important issues first
        for state_name in COMPLETION_STATE_PRIORITY_ORDER:
            count = state_counts.get(state_name, 0)
            if count > 0:
                # Get the CompletionState object and its color tag
                state_obj = getattr(CompletionState, state_name)
                color_tag = state_obj.color.tag

                if state_name == "missing":
                    colored_part = f"[{color_tag}]{count} missing files[/]"
                else:
                    colored_part = f"[{color_tag}]{count} {state_name}[/]"
                count_parts.append(colored_part)

        # Format with proper oxford comma without quotes (oxford_comma adds quotes)
        count_parts_len = len(count_parts)
        if count_parts_len == 0:
            count_summary = "[green]0 successful[/]"
        elif count_parts_len == 1:
            count_summary = count_parts[0]
        elif count_parts_len == 2:  # noqa: PLR2004
            count_summary = f"{count_parts[0]} and {count_parts[1]}"
        else:
            # Multiple items: "item1, item2, and item3"
            front = ", ".join(count_parts[:-1])
            count_summary = f"{front}, and {count_parts[-1]}"

        # Generate final message with colored parts
        total_scenarios = len(self)
        scenario_word = "scenario" if total_scenarios == 1 else "scenarios"

        # Main count in white/default, details in parentheses with colors
        summary = f"Molecule executed {total_scenarios} {scenario_word} ({count_summary})"

        return highest_priority_state, summary

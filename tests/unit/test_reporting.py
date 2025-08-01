"""Tests for molecule.reporting module."""

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    import pytest

from io import StringIO

from molecule.constants import ANSICodes as A
from molecule.reporting import (
    ActionResult,
    CompletionState,
    CompletionStateInfo,
    ScenarioResults,
    ScenariosResults,
    report,
)


def test_completion_state_info_init() -> None:
    """Test CompletionStateInfo initialization."""
    state_info = CompletionStateInfo(
        state="successful",
        log_level="info",
        color=A.GREEN,
        message="Custom message",
        note="Test note",
    )

    assert state_info.state == "successful"
    assert state_info.log_level == "info"
    assert state_info.color == A.GREEN
    assert state_info._message == "Custom message"
    assert state_info._note == "Test note"


def test_completion_state_info_message_property() -> None:
    """Test CompletionStateInfo message property."""
    # Test with custom message
    state_info = CompletionStateInfo("successful", "info", A.GREEN, message="Custom")
    assert state_info.message == "Completed: Custom"

    # Test with default message (from state)
    state_info = CompletionStateInfo("failed", "error", A.RED)
    assert state_info.message == "Completed: Failed"


def test_completion_state_info_note_property() -> None:
    """Test CompletionStateInfo note property."""
    state_info = CompletionStateInfo("missing", "warning", A.MAGENTA, note="Test note")
    assert state_info.note == "Test note"

    state_info_no_note = CompletionStateInfo("successful", "info", A.GREEN)
    assert state_info_no_note.note is None


def test_completion_state_info_call_with_message() -> None:
    """Test CompletionStateInfo callable interface with message."""
    original = CompletionState.partial
    custom = original("2 successful, 1 failed")

    assert custom.state == "partial"
    assert custom.log_level == "info"
    assert custom.color == A.GREEN
    assert custom._message == "2 successful, 1 failed"
    assert custom.message == "Completed: 2 successful, 1 failed"


def test_completion_state_info_call_with_note() -> None:
    """Test CompletionStateInfo callable interface with note."""
    original = CompletionState.missing
    custom = original(note="Remove from sequence")

    assert custom.state == "missing"
    assert custom.note == "Remove from sequence"


def test_completion_state_info_call_with_both() -> None:
    """Test CompletionStateInfo callable interface with message and note."""
    original = CompletionState.failed
    custom = original(message="Connection failed", note="Check network")

    assert custom._message == "Connection failed"
    assert custom.note == "Check network"
    assert custom.message == "Completed: Connection failed"


def test_completion_state_info_call_returns_self_when_no_args() -> None:
    """Test CompletionStateInfo returns self when called with no arguments."""
    original = CompletionState.successful
    same = original()

    assert same is original


def test_completion_state_standard_states() -> None:
    """Test that all standard completion states are defined correctly."""
    assert CompletionState.disabled.state == "disabled"
    assert CompletionState.disabled.log_level == "info"
    assert CompletionState.disabled.color == A.CYAN

    assert CompletionState.failed.state == "failed"
    assert CompletionState.failed.log_level == "error"
    assert CompletionState.failed.color == A.RED

    assert CompletionState.missing.state == "missing"
    assert CompletionState.missing.log_level == "warning"
    assert CompletionState.missing.color == A.MAGENTA

    assert CompletionState.partial.state == "partial"
    assert CompletionState.partial.log_level == "info"
    assert CompletionState.partial.color == A.GREEN

    assert CompletionState.skipped.state == "skipped"
    assert CompletionState.skipped.log_level == "info"
    assert CompletionState.skipped.color == A.CYAN

    assert CompletionState.successful.state == "successful"
    assert CompletionState.successful.log_level == "info"
    assert CompletionState.successful.color == A.GREEN


def test_action_result_initialization() -> None:
    """Test ActionResult initialization."""
    result = ActionResult(action="test")
    assert result.action == "test"
    assert not result.states  # Empty list

    result2 = ActionResult(action="verify", states=[])
    assert result2.action == "verify"
    assert not result2.states  # Empty list


def test_action_result_append() -> None:
    """Test ActionResult append method."""
    result = ActionResult(action="verify")
    state = CompletionState.successful

    result.append(state)
    assert len(result.states) == 1
    assert result.states[0] == state


def test_action_result_summary_no_states() -> None:
    """Test ActionResult summary with no states returns successful."""
    result = ActionResult(action="create")
    summary = result.summary

    assert summary == CompletionState.successful


def test_action_result_summary_single_state() -> None:
    """Test ActionResult summary with single state returns that state."""
    result = ActionResult(action="destroy")
    result.append(CompletionState.failed)

    summary = result.summary
    assert summary == CompletionState.failed


def test_action_result_summary_multiple_states_with_failed() -> None:
    """Test ActionResult summary prioritizes failed states."""
    result = ActionResult(action="verify")
    result.append(CompletionState.successful)
    result.append(CompletionState.failed)
    result.append(CompletionState.successful)

    summary = result.summary
    assert summary.state == "failed"
    assert "2 successful, 1 failed" in summary.message


def test_action_result_summary_multiple_states_partial() -> None:
    """Test ActionResult summary creates partial message for mixed non-failed states."""
    result = ActionResult(action="side_effect")
    result.append(CompletionState.successful)
    result.append(CompletionState.skipped)
    result.append(CompletionState.successful)

    summary = result.summary
    assert summary.state == "skipped"  # highest priority non-failed state
    assert "2 successful, 1 skipped" in summary.message


def test_action_result_summary_with_notes() -> None:
    """Test ActionResult summary handles notes correctly."""
    result = ActionResult(action="prepare")
    result.append(CompletionState.missing(note="File not found"))
    result.append(CompletionState.successful)

    summary = result.summary
    assert summary.note == "File not found"


def test_action_result_summary_multiple_notes() -> None:
    """Test ActionResult summary with multiple different notes."""
    result = ActionResult(action="cleanup")
    result.append(CompletionState.missing(note="File not found"))
    result.append(CompletionState.missing(note="Directory missing"))

    summary = result.summary
    assert summary.note == "See details above"


def test_scenario_results_initialization() -> None:
    """Test ScenarioResults initialization."""
    results = ScenarioResults(name="test", actions=[])
    assert results.name == "test"
    assert not results.actions  # Empty list


def test_scenario_results_add_action_result() -> None:
    """Test ScenarioResults add_action_result method."""
    results = ScenarioResults(name="test", actions=[])
    results.add_action_result("create")

    assert len(results.actions) == 1
    assert results.actions[0].action == "create"
    assert results.actions[0].states == []


def test_scenario_results_add_completion() -> None:
    """Test ScenarioResults add_completion method."""
    results = ScenarioResults(name="test", actions=[])
    results.add_action_result("converge")
    results.add_completion(CompletionState.successful)

    assert len(results.actions[-1].states) == 1
    assert results.actions[-1].states[0] == CompletionState.successful


def test_scenario_results_last_action_summary() -> None:
    """Test ScenarioResults last_action_summary property."""
    results = ScenarioResults(name="test", actions=[])
    results.add_action_result("verify")
    results.add_completion(CompletionState.failed)

    summary = results.last_action_summary
    assert summary == CompletionState.failed


def test_scenarios_results_inheritance() -> None:
    """Test ScenariosResults inherits from list correctly."""
    results = ScenariosResults()
    assert isinstance(results, list)
    assert len(results) == 0

    scenario = ScenarioResults(name="default", actions=[])
    results.append(scenario)
    assert len(results) == 1
    assert results[0] == scenario


def generate_scenarios_results() -> ScenariosResults:
    """Generate comprehensive test scenario data for report testing.

    Returns:
        ScenariosResults with multiple scenarios and various completion states.
    """
    # First scenario with multiple action types
    scenario1_results = ScenarioResults(name="default", actions=[])

    # Add successful action
    create_action = ActionResult(action="create")
    create_action.append(CompletionState.successful)
    scenario1_results.actions.append(create_action)

    # Add failed action with note
    converge_action = ActionResult(action="converge")
    converge_action.append(CompletionState.failed(note="Task failed"))
    scenario1_results.actions.append(converge_action)

    # Add missing action
    verify_action = ActionResult(action="verify")
    verify_action.append(CompletionState.missing(note="Playbook not found"))
    scenario1_results.actions.append(verify_action)

    # Second scenario
    scenario2_results = ScenarioResults(name="docker", actions=[])

    # Add skipped action
    destroy_action = ActionResult(action="destroy")
    destroy_action.append(CompletionState.skipped)
    scenario2_results.actions.append(destroy_action)

    return ScenariosResults([scenario1_results, scenario2_results])


def test_report_function(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test report function output.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    # Ensure predictable output without ANSI codes
    monkeypatch.setenv("NO_COLOR", "1")

    # Mock original_stderr with StringIO
    mock_stderr = StringIO()
    monkeypatch.setattr("molecule.reporting.original_stderr", mock_stderr)

    # Create test data
    action_result = ActionResult(action="create")
    action_result.append(CompletionState.successful)

    scenario_result = ScenarioResults(name="default", actions=[action_result])
    results = ScenariosResults([scenario_result])

    # Call function
    report(results)

    # Verify output was written
    output = mock_stderr.getvalue()
    assert len(output) > 0


def test_report_with_notes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test report function handles action results with notes.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    # Ensure predictable output without ANSI codes
    monkeypatch.setenv("NO_COLOR", "1")

    # Mock original_stderr with StringIO
    mock_stderr = StringIO()
    monkeypatch.setattr("molecule.reporting.original_stderr", mock_stderr)

    # Create action with note
    action_result = ActionResult(action="prepare")
    action_result.append(CompletionState.missing(note="File not found"))

    scenario_result = ScenarioResults(name="test", actions=[action_result])
    results = ScenariosResults([scenario_result])

    report(results)

    # Verify output contains note information
    output = mock_stderr.getvalue()
    assert "File not found" in output


def test_report_comprehensive_no_color(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test report function with comprehensive scenario data and no color.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    # Ensure no color output
    monkeypatch.setenv("NO_COLOR", "1")

    # Mock original_stderr with StringIO
    mock_stderr = StringIO()
    monkeypatch.setattr("molecule.reporting.original_stderr", mock_stderr)

    # Create comprehensive test data
    results = generate_scenarios_results()
    report(results)

    expected_output = (
        "\nSummary\n"
        "default > create: Completed: Successful\n"
        "default > converge: Completed: Failed (Task failed)\n"
        "default > verify: Completed: Missing (Playbook not found)\n"
        "\n"
        "docker > destroy: Completed: Skipped\n"
        "\n"
    )

    output = mock_stderr.getvalue()
    assert output == expected_output


def test_report_comprehensive_with_color(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test report function with comprehensive scenario data and color enabled.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    # Enable color output
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")

    # Mock original_stderr with StringIO
    mock_stderr = StringIO()
    monkeypatch.setattr("molecule.reporting.original_stderr", mock_stderr)

    # Create comprehensive test data (same as no-color test)
    results = generate_scenarios_results()
    report(results)

    # Expected output with ANSI escape codes using ANSICodes constants
    expected_output = (
        f"\n{A.BOLD}{A.UNDERLINE}Summary{A.RESET}{A.RESET}\n"
        f"{A.GREEN}default{A.RESET} ➜ {A.YELLOW}create{A.RESET}: {A.GREEN}Completed: Successful{A.RESET}\n"
        f"{A.GREEN}default{A.RESET} ➜ {A.YELLOW}converge{A.RESET}: {A.RED}Completed: Failed{A.RESET} {A.DIM}(Task failed){A.RESET}\n"
        f"{A.GREEN}default{A.RESET} ➜ {A.YELLOW}verify{A.RESET}: {A.MAGENTA}Completed: Missing{A.RESET} {A.DIM}(Playbook not found){A.RESET}\n"
        "\n"
        f"{A.GREEN}docker{A.RESET} ➜ {A.YELLOW}destroy{A.RESET}: {A.CYAN}Completed: Skipped{A.RESET}\n"
        "\n"
    )

    output = mock_stderr.getvalue()
    assert output == expected_output


def test_completion_state_info_equality() -> None:
    """Test CompletionStateInfo objects can be compared."""
    state1 = CompletionState.successful
    state2 = CompletionState.successful
    state3 = CompletionState.failed

    # Same state instances should be equal
    assert state1 == state2
    assert state1 != state3


def test_action_result_summary_priority_order() -> None:
    """Test ActionResult summary follows correct priority order."""
    result = ActionResult(action="test")
    result.append(CompletionState.successful)
    result.append(CompletionState.disabled)
    result.append(CompletionState.skipped)
    result.append(CompletionState.missing)

    summary = result.summary
    assert summary.state == "missing"  # Highest priority

    # Add failed - should take precedence
    result.append(CompletionState.failed)
    summary = result.summary
    assert summary.state == "failed"

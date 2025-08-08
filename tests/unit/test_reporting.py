"""Unit tests for reporting module."""

from __future__ import annotations

import re

from io import StringIO
from typing import TYPE_CHECKING

from molecule.ansi_output import AnsiOutput
from molecule.constants import ANSICodes as A
from molecule.reporting import (
    ActionResult,
    CompletionState,
    CompletionStateInfo,
    ScenarioResults,
    ScenariosResults,
    report,
)


if TYPE_CHECKING:
    import pytest


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
    assert state_info.message == "Executed: Custom"

    # Test with default message (from state)
    state_info = CompletionStateInfo("failed", "error", A.RED)
    assert state_info.message == "Executed: Failed"


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
    assert custom.message == "Executed: 2 successful, 1 failed"


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
    assert custom.message == "Executed: Connection failed"


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
        "\nDETAILS                                                                        \n"
        "default > create: Executed: Successful\n"
        "default > converge: Executed: Failed (Task failed)\n"
        "default > verify: Executed: Missing (Playbook not found)\n"
        "\n"
        "docker > destroy: Executed: Skipped\n"
        "\n"
        "SCENARIO RECAP                                                                 \n"
        "default                   : actions=3  successful=1  disabled=0  skipped=0  missing=1  failed=1\n"
        "docker                    : actions=1  successful=0  disabled=0  skipped=1  missing=0  failed=0\n"
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
        f"\n{A.BOLD}{A.UNDERLINE}DETAILS                                                                        {A.RESET}\n"
        f"{A.GREEN}default{A.RESET} ➜ {A.YELLOW}create{A.RESET}: {A.GREEN}Executed: Successful{A.RESET}\n"
        f"{A.GREEN}default{A.RESET} ➜ {A.YELLOW}converge{A.RESET}: {A.RED}Executed: Failed{A.RESET} {A.DIM}(Task failed){A.RESET}\n"
        f"{A.GREEN}default{A.RESET} ➜ {A.YELLOW}verify{A.RESET}: {A.MAGENTA}Executed: Missing{A.RESET} {A.DIM}(Playbook not found){A.RESET}\n"
        "\n"
        f"{A.GREEN}docker{A.RESET} ➜ {A.YELLOW}destroy{A.RESET}: {A.CYAN}Executed: Skipped{A.RESET}\n"
        "\n"
        f"{A.BOLD}{A.UNDERLINE}SCENARIO RECAP                                                                 {A.RESET}\n"
        f"{A.GREEN}default                   {A.RESET}: {A.YELLOW}actions=3{A.RESET}  {A.GREEN}successful=1{A.RESET}  disabled=0  skipped=0  {A.MAGENTA}missing=1{A.RESET}  {A.RED}failed=1{A.RESET}\n"
        f"{A.GREEN}docker                    {A.RESET}: {A.YELLOW}actions=1{A.RESET}  successful=0  disabled=0  {A.CYAN}skipped=1{A.RESET}  missing=0  failed=0\n"
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


# New tests for scenario recap functionality


def test_format_scenario_recap_empty() -> None:
    """Test recap with no scenarios."""
    results = ScenariosResults([])
    ansi_output = AnsiOutput()

    recap = ansi_output.format_scenario_recap(results)
    assert recap == ""


def test_format_scenario_recap_single_scenario() -> None:
    """Test recap with single successful scenario."""
    action1 = ActionResult(action="create")
    action1.append(CompletionState.successful)
    action2 = ActionResult(action="converge")
    action2.append(CompletionState.successful)

    scenario = ScenarioResults(name="default", actions=[action1, action2])
    results = ScenariosResults([scenario])
    ansi_output = AnsiOutput()

    recap = ansi_output.format_scenario_recap(results)

    assert "SCENARIO RECAP" in recap
    assert "default" in recap
    assert "actions=2" in recap
    assert "successful=2" in recap
    assert "disabled=0" in recap
    assert "skipped=0" in recap
    assert "missing=0" in recap
    assert "failed=0" in recap


def test_format_scenario_recap_mixed_states() -> None:
    """Test recap with mixed completion states."""
    action1 = ActionResult(action="create")
    action1.append(CompletionState.successful)

    action2 = ActionResult(action="prepare")
    action2.append(CompletionState.missing)

    action3 = ActionResult(action="converge")
    action3.append(CompletionState.failed)

    action4 = ActionResult(action="cleanup")
    action4.append(CompletionState.skipped)

    scenario = ScenarioResults(name="test-scenario", actions=[action1, action2, action3, action4])
    results = ScenariosResults([scenario])
    ansi_output = AnsiOutput()

    recap = ansi_output.format_scenario_recap(results)

    assert "test-scenario" in recap
    assert "actions=4" in recap
    assert "successful=1" in recap
    assert "missing=1" in recap
    assert "failed=1" in recap
    assert "skipped=1" in recap
    assert "disabled=0" in recap


def test_format_scenario_recap_line_format() -> None:
    """Test recap line formatting matches expected pattern."""
    action = ActionResult(action="create")
    action.append(CompletionState.successful)

    scenario = ScenarioResults(name="default", actions=[action])
    results = ScenariosResults([scenario])
    ansi_output = AnsiOutput()

    recap = ansi_output.format_scenario_recap(results)
    lines = recap.split("\n")

    # Find the scenario line (skip header and separator)
    scenario_line = None
    for line in lines:
        if "default" in line and "actions=" in line:
            scenario_line = line
            break

    assert scenario_line is not None
    assert "default                   :" in scenario_line
    assert "actions=1" in scenario_line
    assert "successful=1" in scenario_line


def test_format_scenario_recap_colors_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that colors are applied when enabled and counts > 0.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    # Force enable colors for this test by removing NO_COLOR if present
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")

    # Create scenario with mixed results (some zero, some non-zero)
    action1 = ActionResult(action="create")
    action1.append(CompletionState.successful)
    action2 = ActionResult(action="verify")
    action2.append(CompletionState.successful)
    action2.append(CompletionState.failed)
    action2.append(CompletionState.missing)

    scenario = ScenarioResults(name="default", actions=[action1, action2])
    results = ScenariosResults([scenario])

    # Create a new AnsiOutput after setting environment variables
    ansi_output = AnsiOutput()

    # Verify that markup is enabled
    assert ansi_output.markup_enabled, "Colors should be enabled for this test"

    recap = ansi_output.format_scenario_recap(results)

    # Should contain ANSI color codes for non-zero values only
    assert "\x1b[32m" in recap  # GREEN for successful=2 should be colored
    assert "\x1b[31m" in recap  # RED for failed=1 should be colored
    assert "\x1b[35m" in recap  # MAGENTA for missing=1 should be colored
    assert "\x1b[33m" in recap  # YELLOW for actions=2 should be colored

    # Verify that zero values are not colored (check the pattern)
    # Look for disabled=0 - should not have ANSI codes before it
    disabled_pattern = r"(\x1b\[[0-9;]*m)?disabled=0"
    disabled_match = re.search(disabled_pattern, recap)
    assert disabled_match is not None
    assert disabled_match.group(1) is None, "disabled=0 should not be colored"

    # Look for skipped=0 - should not have ANSI codes before it
    skipped_pattern = r"(\x1b\[[0-9;]*m)?skipped=0"
    skipped_match = re.search(skipped_pattern, recap)
    assert skipped_match is not None
    assert skipped_match.group(1) is None, "skipped=0 should not be colored"


def test_format_scenario_recap_colors_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test recap without colors when disabled.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    # Force disable colors
    monkeypatch.setenv("NO_COLOR", "1")

    # Create scenario with non-zero counts (but colors should still be disabled)
    action1 = ActionResult(action="create")
    action1.append(CompletionState.successful)
    action2 = ActionResult(action="verify")
    action2.append(CompletionState.failed)
    action2.append(CompletionState.missing)

    scenario = ScenarioResults(name="default", actions=[action1, action2])
    results = ScenariosResults([scenario])
    ansi_output = AnsiOutput()

    recap = ansi_output.format_scenario_recap(results)

    # Should not contain ANSI color codes even for non-zero values
    assert "\x1b[32m" not in recap  # No GREEN
    assert "\x1b[31m" not in recap  # No RED
    assert "\x1b[35m" not in recap  # No MAGENTA
    assert "\x1b[33m" not in recap  # No YELLOW

    # Should still contain the content
    assert "default" in recap
    assert "actions=2" in recap
    assert "successful=1" in recap
    assert "failed=1" in recap
    assert "missing=1" in recap
    assert "disabled=0" in recap
    assert "skipped=0" in recap


def test_format_scenario_recap_multiple_scenarios() -> None:
    """Test recap with multiple scenarios shows all correctly."""
    expected_lines_with_header_and_scenarios = 4

    # Scenario 1: All successful
    action1 = ActionResult(action="create")
    action1.append(CompletionState.successful)
    scenario1 = ScenarioResults(name="default", actions=[action1])

    # Scenario 2: Mixed results
    action2a = ActionResult(action="create")
    action2a.append(CompletionState.successful)
    action2b = ActionResult(action="prepare")
    action2b.append(CompletionState.missing)
    scenario2 = ScenarioResults(name="test-scenario", actions=[action2a, action2b])

    # Scenario 3: Longer name
    action3 = ActionResult(action="converge")
    action3.append(CompletionState.failed)
    scenario3 = ScenarioResults(name="very-long-scenario-name", actions=[action3])

    results = ScenariosResults([scenario1, scenario2, scenario3])
    ansi_output = AnsiOutput()

    recap = ansi_output.format_scenario_recap(results)

    # Check all scenarios present
    assert "default" in recap
    assert "test-scenario" in recap
    assert "very-long-scenario-name" in recap

    # Check action counts
    assert "actions=1" in recap  # default scenario
    assert "actions=2" in recap  # test-scenario
    # very-long-scenario-name has actions=1 too, so appears twice total

    # Verify line count (header + 3 scenarios, no separator line)
    lines = [line for line in recap.split("\n") if line.strip()]
    assert len(lines) == expected_lines_with_header_and_scenarios


def test_format_scenario_recap_separator_length() -> None:
    """Test that recap header has proper width without separator line."""
    min_lines_for_header_and_scenario = 2

    action = ActionResult(action="create")
    action.append(CompletionState.successful)
    scenario = ScenarioResults(name="default", actions=[action])
    results = ScenariosResults([scenario])
    ansi_output = AnsiOutput()

    recap = ansi_output.format_scenario_recap(results)
    lines = recap.split("\n")

    # First line should be the header (with ANSI codes for bold/underline)
    header_line = lines[0]
    assert "SCENARIO RECAP" in header_line

    # Should not have a separate separator line
    assert len(lines) >= min_lines_for_header_and_scenario, (
        "Should have header and at least one scenario line"
    )
    second_line = lines[1]
    assert "default" in second_line, "Second line should be scenario data, not separator"


def test_format_scenario_recap_action_result_summary() -> None:
    """Test recap counts all individual states, not just summary."""
    # Create action with multiple states - should count all states
    action = ActionResult(action="verify")
    action.append(CompletionState.successful)
    action.append(CompletionState.failed)  # Both should be counted

    scenario = ScenarioResults(name="default", actions=[action])
    results = ScenariosResults([scenario])
    ansi_output = AnsiOutput()

    recap = ansi_output.format_scenario_recap(results)

    # Should count both states (not just the summary)
    assert "successful=1" in recap
    assert "failed=1" in recap
    assert "actions=1" in recap  # Still one action


def test_format_scenario_recap_multiple_states_per_action() -> None:
    """Test recap correctly counts multiple states within single actions."""
    # Create action with multiple verify results (like running multiple tests)
    verify_action = ActionResult(action="verify")
    verify_action.append(CompletionState.successful)  # Test 1 passed
    verify_action.append(CompletionState.successful)  # Test 2 passed
    verify_action.append(CompletionState.failed)  # Test 3 failed
    verify_action.append(CompletionState.missing)  # Test 4 missing

    # Create another action with single state
    create_action = ActionResult(action="create")
    create_action.append(CompletionState.successful)

    scenario = ScenarioResults(name="test-scenario", actions=[verify_action, create_action])
    results = ScenariosResults([scenario])
    ansi_output = AnsiOutput()

    recap = ansi_output.format_scenario_recap(results)

    # Should count all individual states across both actions
    assert "actions=2" in recap  # Two actions (verify + create)
    assert "successful=3" in recap  # 2 from verify + 1 from create
    assert "failed=1" in recap  # 1 from verify
    assert "missing=1" in recap  # 1 from verify
    assert "disabled=0" in recap  # None
    assert "skipped=0" in recap  # None


def test_format_scenario_recap_alignment_multi_digit() -> None:
    """Test that multi-digit counts maintain proper alignment."""
    # Constants for this test
    total_action_count = 42
    successful_action_count = 23
    scenario_field_width = 26

    # Create a scenario with many actions to generate multi-digit counts
    actions = []
    for i in range(total_action_count):  # 42 actions total
        action = ActionResult(action=f"action_{i}")
        if i < successful_action_count:
            action.append(CompletionState.successful)
        elif i < total_action_count:
            action.append(CompletionState.missing)
        actions.append(action)

    scenario = ScenarioResults(name="test-scenario-long-name", actions=actions)
    results = ScenariosResults([scenario])
    ansi_output = AnsiOutput()

    recap = ansi_output.format_scenario_recap(results)

    # Should handle multi-digit counts properly
    assert "actions=42" in recap
    assert "successful=23" in recap
    assert "missing=19" in recap

    # Find the scenario line (not the header)
    lines = recap.split("\n")
    scenario_line = None
    for line in lines:
        if "test-scenario-long-name" in line:
            scenario_line = line
            break

    assert scenario_line is not None, "Should find scenario line"

    # Check alignment positions
    colon_pos = scenario_line.find(":")
    actions_pos = scenario_line.find("actions=")
    successful_pos = scenario_line.find("successful=")

    # Consistent positioning regardless of digit count
    assert colon_pos == scenario_field_width  # Scenario field width
    assert actions_pos > colon_pos + 1
    assert successful_pos > actions_pos + 10  # Field + spacing


def test_report_includes_scenario_recap(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that report() function includes scenario recap.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    # Ensure predictable output without ANSI codes
    monkeypatch.setenv("NO_COLOR", "1")

    # Mock original_stderr with StringIO
    mock_stderr = StringIO()
    monkeypatch.setattr("molecule.reporting.original_stderr", mock_stderr)

    # Create test results
    action = ActionResult(action="create")
    action.append(CompletionState.successful)
    scenario = ScenarioResults(name="default", actions=[action])
    results = ScenariosResults([scenario])

    # Call report
    report(results)

    # Verify recap is included in output
    output = mock_stderr.getvalue()
    assert "DETAILS" in output  # Changed to all caps
    assert "SCENARIO RECAP" in output  # New recap in all caps
    assert "default" in output
    assert "actions=1" in output


def test_report_details_format_updated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that Details section has proper formatting.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    # Ensure predictable output without ANSI codes
    monkeypatch.setenv("NO_COLOR", "1")

    # Mock original_stderr with StringIO
    mock_stderr = StringIO()
    monkeypatch.setattr("molecule.reporting.original_stderr", mock_stderr)

    # Create test results
    action = ActionResult(action="create")
    action.append(CompletionState.successful)
    scenario = ScenarioResults(name="default", actions=[action])
    results = ScenariosResults([scenario])

    # Call report
    report(results)

    # Verify Details formatting
    output = mock_stderr.getvalue()

    # Should contain "DETAILS" (not "Summary")
    assert "DETAILS" in output
    assert "Summary" not in output

    # Should NOT contain separator line after Details
    lines = output.split("\n")
    details_line_idx = None
    for i, line in enumerate(lines):
        if "DETAILS" in line:
            details_line_idx = i
            break

    assert details_line_idx is not None
    # Next line should NOT be separator (should be empty or content)
    next_line = lines[details_line_idx + 1] if details_line_idx + 1 < len(lines) else ""
    assert next_line != "─" * 79, "Separator line should be removed"


def test_report_recap_after_details(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that scenario recap appears after details section.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    # Ensure predictable output without ANSI codes
    monkeypatch.setenv("NO_COLOR", "1")

    # Mock original_stderr with StringIO
    mock_stderr = StringIO()
    monkeypatch.setattr("molecule.reporting.original_stderr", mock_stderr)

    # Create test results with multiple scenarios for clear output
    action1 = ActionResult(action="create")
    action1.append(CompletionState.successful)
    scenario1 = ScenarioResults(name="default", actions=[action1])

    action2 = ActionResult(action="converge")
    action2.append(CompletionState.missing)
    scenario2 = ScenarioResults(name="test-scenario", actions=[action2])

    results = ScenariosResults([scenario1, scenario2])

    # Call report
    report(results)

    # Verify order: Details appears before Scenario recap
    output = mock_stderr.getvalue()
    details_pos = output.find("DETAILS")
    recap_pos = output.find("SCENARIO RECAP")

    assert details_pos != -1, "DETAILS section not found"
    assert recap_pos != -1, "SCENARIO RECAP section not found"
    assert details_pos < recap_pos, "SCENARIO RECAP should appear after DETAILS"


def test_report_no_recap_for_empty_results(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that no recap is shown for empty results.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    # Ensure predictable output without ANSI codes
    monkeypatch.setenv("NO_COLOR", "1")

    # Mock original_stderr with StringIO
    mock_stderr = StringIO()
    monkeypatch.setattr("molecule.reporting.original_stderr", mock_stderr)

    # Call report with empty results
    results = ScenariosResults([])
    report(results)

    # Should not contain recap
    output = mock_stderr.getvalue()
    assert "SCENARIO RECAP" not in output

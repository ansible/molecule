"""Tests for the click_command_ex decorator exception handling."""

from __future__ import annotations

from typing import TYPE_CHECKING

import click

from click.testing import CliRunner

from molecule.click_cfg import click_command_ex
from molecule.exceptions import ImmediateExit, MoleculeError, ScenarioFailureError


if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_click_command_ex_with_immediate_exit_success(mocker: MockerFixture) -> None:
    """Test click_command_ex decorator handles ImmediateExit with code 0 correctly.

    Args:
        mocker: pytest-mock fixture for mocking.
    """
    # Mock the logger and util.sysexit
    mock_logger = mocker.patch("molecule.click_cfg.logging.getLogger")
    mock_sysexit = mocker.patch("molecule.util.sysexit")

    # Create a command that raises ImmediateExit with success code
    @click_command_ex()
    def test_command() -> None:
        """Test command that raises ImmediateExit with code 0.

        Raises:
            ImmediateExit: Always raised for testing.
        """
        msg = "Operation completed successfully"
        raise ImmediateExit(msg, code=0)

    # Create a Click runner and invoke the command
    runner = CliRunner()
    runner.invoke(test_command, [])

    # Verify logging and sysexit were called correctly (info for success)
    mock_logger.return_value.info.assert_called_once_with("Operation completed successfully")
    mock_logger.return_value.error.assert_not_called()
    mock_sysexit.assert_called_once_with(code=0)


def test_click_command_ex_with_immediate_exit_failure(mocker: MockerFixture) -> None:
    """Test click_command_ex decorator handles ImmediateExit with failure code correctly.

    Args:
        mocker: pytest-mock fixture for mocking.
    """
    # Mock the logger and util.sysexit
    mock_logger = mocker.patch("molecule.click_cfg.logging.getLogger")
    mock_sysexit = mocker.patch("molecule.util.sysexit")
    mocker.patch("molecule.click_cfg.util.is_debug_mode", return_value=False)

    # Create a command that raises ImmediateExit with failure code
    @click_command_ex()
    def test_command() -> None:
        """Test command that raises ImmediateExit with failure code.

        Raises:
            ImmediateExit: Always raised for testing.
        """
        msg = "Operation failed"
        error_code = 42
        raise ImmediateExit(msg, code=error_code)

    # Create a Click runner and invoke the command
    runner = CliRunner()
    runner.invoke(test_command, [])

    # Verify logging and sysexit were called correctly (error with exc_info=False in non-debug)
    mock_logger.return_value.error.assert_called_once_with("Operation failed", exc_info=False)
    mock_logger.return_value.info.assert_not_called()
    mock_sysexit.assert_called_once_with(code=42)


def test_click_command_ex_with_immediate_exit_failure_debug_mode(mocker: MockerFixture) -> None:
    """Test click_command_ex decorator shows full traceback in debug mode for failures.

    Args:
        mocker: pytest-mock fixture for mocking.
    """
    # Mock the logger and util.sysexit
    mock_logger = mocker.patch("molecule.click_cfg.logging.getLogger")
    mock_sysexit = mocker.patch("molecule.util.sysexit")
    mocker.patch("molecule.click_cfg.util.is_debug_mode", return_value=True)

    # Create a command that raises ImmediateExit with failure code
    @click_command_ex()
    def test_command() -> None:
        """Test command that raises ImmediateExit with failure code.

        Raises:
            ImmediateExit: Always raised for testing.
        """
        msg = "Operation failed"
        error_code = 42
        raise ImmediateExit(msg, code=error_code)

    # Create a Click runner and invoke the command
    runner = CliRunner()
    runner.invoke(test_command, [])

    # Verify logging and sysexit were called correctly (error with full traceback in debug mode)
    mock_logger.return_value.error.assert_called_once_with("Operation failed", exc_info=True)
    mock_logger.return_value.info.assert_not_called()
    mock_sysexit.assert_called_once_with(code=42)


def test_click_command_ex_failure_no_context(mocker: MockerFixture) -> None:
    """Test click_command_ex decorator handles missing context gracefully.

    Args:
        mocker: pytest-mock fixture for mocking.
    """
    # Mock the logger and util.sysexit
    mock_logger = mocker.patch("molecule.click_cfg.logging.getLogger")
    mock_sysexit = mocker.patch("molecule.util.sysexit")
    mocker.patch("molecule.click_cfg.util.is_debug_mode", return_value=False)

    # Create a command that raises ImmediateExit with failure code
    @click_command_ex()
    def test_command() -> None:
        """Test command that raises ImmediateExit with failure code.

        Raises:
            ImmediateExit: Always raised for testing.
        """
        msg = "Operation failed"
        error_code = 42
        raise ImmediateExit(msg, code=error_code)

    # Create a Click runner and invoke the command
    runner = CliRunner()
    runner.invoke(test_command, [])

    # Verify it defaults to non-debug behavior (error with exc_info=False)
    mock_logger.return_value.error.assert_called_once_with("Operation failed", exc_info=False)
    mock_logger.return_value.info.assert_not_called()
    mock_sysexit.assert_called_once_with(code=42)


def test_click_command_ex_with_molecule_error(mocker: MockerFixture) -> None:
    """A MoleculeError exits with its code without an extra log line.

    MoleculeError logs its message at CRITICAL on construction, so the handler
    should not re-log it in non-debug mode.

    Args:
        mocker: pytest-mock fixture for mocking.
    """
    mock_logger = mocker.patch("molecule.click_cfg.logging.getLogger")
    mock_sysexit = mocker.patch("molecule.util.sysexit")
    mocker.patch("molecule.click_cfg.util.is_debug_mode", return_value=False)

    @click_command_ex()
    def test_command() -> None:
        """Test command that raises MoleculeError.

        Raises:
            MoleculeError: Always raised for testing.
        """
        msg = "Unable to load molecule.yml"
        raise MoleculeError(msg, code=3)

    runner = CliRunner()
    runner.invoke(test_command, [])

    mock_logger.return_value.error.assert_not_called()
    mock_sysexit.assert_called_once_with(code=3)


def test_click_command_ex_scenario_failure_exits_with_code(mocker: MockerFixture) -> None:
    """A ScenarioFailureError exits with the code it carries.

    A failed verifier raises ScenarioFailureError with the tool's return code
    (see verifier/testinfra.py), so the process must exit with that same code
    rather than a generic 1.

    Args:
        mocker: pytest-mock fixture for mocking.
    """
    mocker.patch("molecule.click_cfg.logging.getLogger")
    mock_sysexit = mocker.patch("molecule.util.sysexit")
    mocker.patch("molecule.click_cfg.util.is_debug_mode", return_value=False)

    @click_command_ex()
    def test_command() -> None:
        """Test command that raises ScenarioFailureError.

        Raises:
            ScenarioFailureError: Always raised for testing.
        """
        msg = "Verifier tests failed"
        raise ScenarioFailureError(message=msg, code=2)

    runner = CliRunner()
    runner.invoke(test_command, [])

    mock_sysexit.assert_called_once_with(code=2)


def test_click_command_ex_with_message_less_molecule_error(mocker: MockerFixture) -> None:
    """A message-less MoleculeError still reports the failure before exiting.

    Such an error (for example a lock timeout carrying only an exit code) logs
    nothing on construction, so the handler must surface it.

    Args:
        mocker: pytest-mock fixture for mocking.
    """
    mock_logger = mocker.patch("molecule.click_cfg.logging.getLogger")
    mock_sysexit = mocker.patch("molecule.util.sysexit")
    mocker.patch("molecule.click_cfg.util.is_debug_mode", return_value=False)

    @click_command_ex()
    def test_command() -> None:
        """Test command that raises a message-less MoleculeError.

        Raises:
            MoleculeError: Always raised for testing.
        """
        raise MoleculeError(code=7)

    runner = CliRunner()
    runner.invoke(test_command, [])

    mock_logger.return_value.error.assert_called_once_with(
        "Molecule failed with exit code %s.",
        7,
    )
    mock_sysexit.assert_called_once_with(code=7)


def test_click_command_ex_with_molecule_error_debug_mode(mocker: MockerFixture) -> None:
    """In debug mode a MoleculeError shows the full traceback before exiting.

    Args:
        mocker: pytest-mock fixture for mocking.
    """
    mock_logger = mocker.patch("molecule.click_cfg.logging.getLogger")
    mock_sysexit = mocker.patch("molecule.util.sysexit")
    mocker.patch("molecule.click_cfg.util.is_debug_mode", return_value=True)

    @click_command_ex()
    def test_command() -> None:
        """Test command that raises MoleculeError.

        Raises:
            MoleculeError: Always raised for testing.
        """
        msg = "Unable to load molecule.yml"
        raise MoleculeError(msg, code=3)

    runner = CliRunner()
    runner.invoke(test_command, [])

    mock_logger.return_value.error.assert_called_once()
    call_args = mock_logger.return_value.error.call_args
    assert call_args[0][0] == "Unable to load molecule.yml"
    assert isinstance(call_args[1]["exc_info"], MoleculeError)
    mock_sysexit.assert_called_once_with(code=3)


def test_click_command_ex_normal_execution() -> None:
    """Test click_command_ex decorator allows normal command execution."""

    # Create a normal command
    @click_command_ex()
    def test_command() -> None:
        """Test command that executes normally."""
        click.echo("Command executed successfully")

    # Create a Click runner and invoke the command
    runner = CliRunner()
    result = runner.invoke(test_command, [])

    # Verify normal execution
    assert result.exit_code == 0
    assert "Command executed successfully" in result.output


def test_click_command_ex_other_exceptions_not_caught() -> None:
    """Test click_command_ex decorator doesn't catch other exceptions."""

    # Create a command that raises a different exception
    @click_command_ex()
    def test_command() -> None:
        """Test command that raises ValueError.

        Raises:
            ValueError: Always raised for testing.
        """
        msg = "This should not be caught"
        raise ValueError(msg)

    # Create a Click runner and invoke the command
    runner = CliRunner()

    # Verify the exception is not caught by our decorator (should fail with exit code 1)
    result = runner.invoke(test_command, [])
    assert result.exit_code == 1
    assert isinstance(result.exception, ValueError)
    assert str(result.exception) == "This should not be caught"

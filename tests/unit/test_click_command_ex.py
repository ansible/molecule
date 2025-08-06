"""Tests for the click_command_ex decorator exception handling."""

from __future__ import annotations

from typing import TYPE_CHECKING

import click

from click.testing import CliRunner

from molecule.click_cfg import click_command_ex
from molecule.exceptions import ImmediateExit


if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_click_command_ex_with_immediate_exit_success(mocker: MockerFixture) -> None:
    """Test click_command_ex decorator handles ImmediateExit with code 0 correctly.

    Args:
        mocker: pytest-mock fixture for mocking.
    """
    # Mock the logger and util.sysexit
    mock_logger = mocker.patch("logging.getLogger")
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
    mock_logger.assert_called_once()
    mock_logger.return_value.info.assert_called_once_with("Operation completed successfully")
    mock_logger.return_value.error.assert_not_called()
    mock_logger.return_value.exception.assert_not_called()
    mock_sysexit.assert_called_once_with(code=0)


def test_click_command_ex_with_immediate_exit_failure(mocker: MockerFixture) -> None:
    """Test click_command_ex decorator handles ImmediateExit with failure code correctly.

    Args:
        mocker: pytest-mock fixture for mocking.
    """
    # Mock the logger and util.sysexit
    mock_logger = mocker.patch("logging.getLogger")
    mock_sysexit = mocker.patch("molecule.util.sysexit")
    mock_get_current_context = mocker.patch("click.get_current_context")

    # Mock context without debug mode
    mock_ctx = mocker.MagicMock()
    mock_ctx.obj = {"args": {"debug": False}}
    mock_get_current_context.return_value = mock_ctx

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

    # Verify logging and sysexit were called correctly (error, not exception in non-debug mode)
    mock_logger.assert_called_once()
    mock_logger.return_value.error.assert_called_once_with("Operation failed")
    mock_logger.return_value.exception.assert_not_called()
    mock_logger.return_value.info.assert_not_called()
    mock_sysexit.assert_called_once_with(code=42)


def test_click_command_ex_with_immediate_exit_failure_debug_mode(mocker: MockerFixture) -> None:
    """Test click_command_ex decorator shows full traceback in debug mode for failures.

    Args:
        mocker: pytest-mock fixture for mocking.
    """
    # Mock the logger and util.sysexit
    mock_logger = mocker.patch("logging.getLogger")
    mock_sysexit = mocker.patch("molecule.util.sysexit")
    mock_get_current_context = mocker.patch("click.get_current_context")

    # Mock context with debug mode enabled
    mock_ctx = mocker.MagicMock()
    mock_ctx.obj = {"args": {"debug": True}}
    mock_get_current_context.return_value = mock_ctx

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

    # Verify logging and sysexit were called correctly (exception with full traceback in debug mode)
    mock_logger.assert_called_once()
    mock_logger.return_value.exception.assert_called_once_with("Operation failed")
    mock_logger.return_value.error.assert_not_called()
    mock_logger.return_value.info.assert_not_called()
    mock_sysexit.assert_called_once_with(code=42)


def test_click_command_ex_failure_no_context(mocker: MockerFixture) -> None:
    """Test click_command_ex decorator handles missing context gracefully.

    Args:
        mocker: pytest-mock fixture for mocking.
    """
    # Mock the logger and util.sysexit
    mock_logger = mocker.patch("logging.getLogger")
    mock_sysexit = mocker.patch("molecule.util.sysexit")
    mock_get_current_context = mocker.patch("click.get_current_context")

    # Mock no context available
    mock_get_current_context.return_value = None

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

    # Verify it defaults to non-debug behavior (error, not exception)
    mock_logger.assert_called_once()
    mock_logger.return_value.error.assert_called_once_with("Operation failed")
    mock_logger.return_value.exception.assert_not_called()
    mock_logger.return_value.info.assert_not_called()
    mock_sysexit.assert_called_once_with(code=42)


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

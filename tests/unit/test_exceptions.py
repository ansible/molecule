"""Tests for molecule.exceptions module."""

from __future__ import annotations

import pytest

from molecule.exceptions import ImmediateExit


# Test constants
TEST_CODE = 42
SUCCESS_CODE = 0
FAILURE_CODE = 1


def test_immediate_exit_basic() -> None:
    """Test ImmediateExit basic functionality."""
    exc = ImmediateExit("Test message", code=TEST_CODE)

    assert str(exc) == "Test message"
    assert exc.message == "Test message"
    assert exc.code == TEST_CODE


def test_immediate_exit_success() -> None:
    """Test ImmediateExit with success code."""
    exc = ImmediateExit("Operation completed", code=SUCCESS_CODE)

    assert str(exc) == "Operation completed"
    assert exc.message == "Operation completed"
    assert exc.code == SUCCESS_CODE


def test_immediate_exit_failure() -> None:
    """Test ImmediateExit with failure code."""
    exc = ImmediateExit("Operation failed", code=FAILURE_CODE)

    assert str(exc) == "Operation failed"
    assert exc.message == "Operation failed"
    assert exc.code == FAILURE_CODE


def test_immediate_exit_custom_code() -> None:
    """Test ImmediateExit with custom exit code."""
    exc = ImmediateExit("Custom failure", code=TEST_CODE)

    assert str(exc) == "Custom failure"
    assert exc.message == "Custom failure"
    assert exc.code == TEST_CODE


def test_immediate_exit_inheritance() -> None:
    """Test ImmediateExit inheritance.

    Raises:
        exc: ImmediateExit instance for testing inheritance.
    """
    exc = ImmediateExit("Test exception", code=FAILURE_CODE)

    # Test inheritance
    assert isinstance(exc, Exception)

    # Test it can be caught as Exception
    with pytest.raises(ImmediateExit) as exc_info:
        raise exc
    assert exc_info.value.message == "Test exception"
    assert exc_info.value.code == FAILURE_CODE

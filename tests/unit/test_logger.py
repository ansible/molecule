#  Copyright (c) 2015-2018 Cisco Systems, Inc.  # noqa: D100
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
from __future__ import annotations

import logging

from typing import TYPE_CHECKING

import pytest

from molecule.command.base import Base
from molecule.console import should_do_markup
from molecule.logger import get_section_loggers


if TYPE_CHECKING:
    from molecule import config


# the dummy/instance fixtures are based on fixtures in tests.unit.command.test_base
class Dummy(Base):
    """ExtendedBase Class."""

    def execute(self, action_args=None):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG002, D102
        return True


@pytest.fixture
def _dummy_class(patched_config_validate, config_instance: config.Config):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN202, ARG001
    return Dummy


@pytest.fixture
def _instance(_dummy_class, config_instance, _patched_logger_env):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN202
    # _patched_logger_env included here to ensure pytest runs it first
    get_section_loggers.cache_clear()
    return _dummy_class(config_instance)


@pytest.fixture
def _patched_logger_env(request, monkeypatch):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN202
    """Parametrize tests with and without CI env vars."""
    envvars = {"CI": None, "GITHUB_ACTIONS": None, "GITLAB_CI": None, "TRAVIS": None}
    envvars.update(request.param[1])
    for envvar, value in envvars.items():
        if value is None:
            monkeypatch.delenv(envvar, raising=False)
        else:
            monkeypatch.setenv(envvar, value)
    return request.param[0]


get_section_logger_tests = [
    # (expected # of section_loggers, envvars)
    (1, {}),
    (2, {"CI": "true", "GITHUB_ACTIONS": "true"}),
    (2, {"CI": "true", "GITLAB_CI": "true"}),
    (2, {"CI": "true", "TRAVIS": "true"}),
    (1, {"CI": "true", "RANDOM_CI": "true"}),
]


@pytest.mark.parametrize(
    "_patched_logger_env",
    get_section_logger_tests,
    indirect=True,
)
def test_get_section_loggers(_patched_logger_env):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    expected_section_loggers = _patched_logger_env
    get_section_loggers.cache_clear()
    section_loggers = get_section_loggers()
    assert len(section_loggers) == expected_section_loggers  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "_patched_logger_env",
    get_section_logger_tests,
    indirect=True,
)
def test_section_loggers_do_not_change_behavior(_patched_logger_env, _instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    dummy_return = _instance.execute()
    assert dummy_return is True


def test_markup_detection_pycolors0(monkeypatch):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    monkeypatch.setenv("PY_COLORS", "0")
    assert not should_do_markup()


def test_markup_detection_pycolors1(monkeypatch):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("PY_COLORS", "1")
    assert should_do_markup()


def test_markup_detection_tty_yes(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    mocker.patch("sys.stdout.isatty", return_value=True)
    mocker.patch("os.environ", {"TERM": "xterm"})
    assert should_do_markup()
    mocker.resetall()
    mocker.stopall()


def test_markup_detection_tty_no(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    mocker.patch("os.environ", {})
    mocker.patch("sys.stdout.isatty", return_value=False)
    assert not should_do_markup()
    mocker.resetall()
    mocker.stopall()


def test_logger_class():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    class FooLogger(logging.getLoggerClass()):  # type: ignore[misc]
        """stub logger that subclasses logging.getLoggerClass()."""

    logging.setLoggerClass(FooLogger)

    # this test throws RecursionError prior to bugfix
    assert FooLogger("foo")

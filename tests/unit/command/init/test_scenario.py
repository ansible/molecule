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

import os

from typing import TYPE_CHECKING

import pytest

from molecule.command.init import scenario
from molecule.config import Config


if TYPE_CHECKING:
    from pathlib import Path
    from unittest.mock import Mock


@pytest.fixture(name="command_args")
def fixture_command_args() -> dict[str, str]:
    """Provide a dictionary of command arguments."""
    return {
        "driver_name": "default",
        "role_name": "test-role",
        "scenario_name": "test-scenario",
        "subcommand": __name__,
        "verifier_name": "ansible",
    }


@pytest.fixture(name="instance")
def fixture_instance(command_args: scenario.CommandArgs) -> scenario.Scenario:
    """Provide a scenario instance.

    Args:
        command_args: A dictionary of command arguments.
    """
    return scenario.Scenario(Config(""), command_args)


def test_scenario_execute(
    monkeypatch: pytest.MonkeyPatch,
    instance: scenario.Scenario,
    patched_logger_info: Mock,
    test_cache_path: Path,
) -> None:
    """Test that the scenario is initialized successfully.

    Args:
        monkeypatch: Pytest fixture.
        instance: A scenario instance.
        patched_logger_info: A patched logger.
        test_cache_path: Path to the cache directory for the test.
    """
    monkeypatch.chdir(test_cache_path)
    instance.execute()

    msg = "Initializing new scenario test-scenario..."
    patched_logger_info.assert_any_call(msg)

    assert os.path.isdir("./molecule/test-scenario")  # noqa: PTH112

    scenario_directory = test_cache_path / "molecule" / "test-scenario"
    msg = f"Initialized scenario in {scenario_directory} successfully."
    patched_logger_info.assert_any_call(msg)


def test_execute_scenario_exists(
    monkeypatch: pytest.MonkeyPatch,
    instance: scenario.Scenario,
    caplog: pytest.LogCaptureFixture,
    test_cache_path: Path,
) -> None:
    """Test that the scenario is initialized successfully.

    Args:
        monkeypatch: Pytest fixture.
        instance: A scenario instance.
        caplog: Pytest log capture fixture.
        test_cache_path: Path to the cache directory for the test.
    """
    monkeypatch.chdir(test_cache_path)
    instance.execute()

    with pytest.raises(SystemExit) as e:
        instance.execute()

    assert e.value.code == 1

    msg = "The directory molecule/test-scenario exists. Cannot create new scenario."
    assert msg in caplog.text

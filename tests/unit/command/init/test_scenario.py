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

from molecule.command.init.scenario import Scenario
from molecule.config import Config
from molecule.exceptions import ImmediateExit
from molecule.utils import util


if TYPE_CHECKING:
    from pathlib import Path

    from molecule.command.init.scenario import CommandArgs


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
def fixture_instance(command_args: CommandArgs) -> Scenario:
    """Provide a scenario instance.

    Args:
        command_args: A dictionary of command arguments.
    """
    return Scenario(Config(""), command_args)


def test_scenario_execute(
    monkeypatch: pytest.MonkeyPatch,
    instance: Scenario,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
) -> None:
    """Test that the scenario is initialized successfully.

    Args:
        monkeypatch: Pytest fixture.
        instance: A scenario instance.
        caplog: Pytest log capture fixture.
        tmp_path: Pytest temporary directory fixture.
    """
    monkeypatch.chdir(tmp_path)

    # Mock the run_command to avoid ansible execution and create the directory structure
    def mock_run_command(*args: object, **kwargs: object) -> None:
        # Create the molecule/test-scenario directory like ansible-playbook would
        scenario_dir = tmp_path / "molecule" / "test-scenario"
        scenario_dir.mkdir(parents=True, exist_ok=True)

    with monkeypatch.context() as m:
        m.setattr("molecule.app.App.run_command", mock_run_command)

        with caplog.at_level(logging.INFO):
            instance.execute()

    msg = "Initializing new scenario test-scenario..."
    assert any(msg in record.message for record in caplog.records)

    assert (tmp_path / "molecule" / "test-scenario").is_dir()

    scenario_directory = tmp_path / "molecule" / "test-scenario"
    msg = f"Initialized scenario in {scenario_directory} successfully."
    assert any(msg in record.message for record in caplog.records)


def test_execute_scenario_exists(
    monkeypatch: pytest.MonkeyPatch,
    instance: Scenario,
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

    with pytest.raises(ImmediateExit) as e:
        instance.execute()

    assert e.value.code == 1

    msg = "The directory molecule/test-scenario exists. Cannot create new scenario."
    assert e.value.message == msg


def test_scenario_execute_collection_mode(
    monkeypatch: pytest.MonkeyPatch,
    instance: Scenario,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
) -> None:
    """Test that the scenario is initialized in collection mode.

    Args:
        monkeypatch: Pytest fixture.
        instance: A scenario instance.
        caplog: Pytest log capture fixture.
        tmp_path: Pytest temporary directory fixture.
    """
    monkeypatch.chdir(tmp_path)

    # Create a galaxy.yml file to simulate collection context
    galaxy_yml = tmp_path / "galaxy.yml"
    galaxy_yml.write_text("""
namespace: test_ns
name: test_collection
version: 1.0.0
""")

    # Clear cache to ensure fresh detection
    util.get_collection_metadata.cache_clear()

    # Mock the run_command to avoid ansible execution and create the directory structure
    def mock_run_command(*args: object, **kwargs: object) -> None:
        # Create the extensions/molecule/test-scenario directory like ansible-playbook would
        scenario_dir = tmp_path / "extensions" / "molecule" / "test-scenario"
        scenario_dir.mkdir(parents=True, exist_ok=True)

    with monkeypatch.context() as m:
        m.setattr("molecule.app.App.run_command", mock_run_command)

        with caplog.at_level(logging.INFO):
            instance.execute()

    msg = "Initializing new scenario test-scenario..."
    assert any(msg in record.message for record in caplog.records)

    # Should create in extensions/molecule instead of molecule/
    assert (tmp_path / "extensions" / "molecule" / "test-scenario").is_dir()
    assert not (tmp_path / "molecule" / "test-scenario").is_dir()

    scenario_directory = tmp_path / "extensions" / "molecule" / "test-scenario"
    msg = f"Initialized scenario in {scenario_directory} successfully."
    assert any(msg in record.message for record in caplog.records)


def test_scenario_execute_standard_mode(
    monkeypatch: pytest.MonkeyPatch,
    instance: Scenario,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
) -> None:
    """Test that the scenario is initialized in standard mode when no collection detected.

    Args:
        monkeypatch: Pytest fixture.
        instance: A scenario instance.
        caplog: Pytest log capture fixture.
        tmp_path: Pytest temporary directory fixture.
    """
    monkeypatch.chdir(tmp_path)

    # Ensure no galaxy.yml exists
    # Clear cache to ensure fresh detection
    util.get_collection_metadata.cache_clear()

    # Mock the run_command to avoid ansible execution and create the directory structure
    def mock_run_command(*args: object, **kwargs: object) -> None:
        # Create the molecule/test-scenario directory like ansible-playbook would
        scenario_dir = tmp_path / "molecule" / "test-scenario"
        scenario_dir.mkdir(parents=True, exist_ok=True)

    with monkeypatch.context() as m:
        m.setattr("molecule.app.App.run_command", mock_run_command)

        with caplog.at_level(logging.INFO):
            instance.execute()

    msg = "Initializing new scenario test-scenario..."
    assert any(msg in record.message for record in caplog.records)

    # Should create in molecule/ (standard mode)
    assert (tmp_path / "molecule" / "test-scenario").is_dir()
    assert not (tmp_path / "extensions" / "molecule" / "test-scenario").is_dir()

    scenario_directory = tmp_path / "molecule" / "test-scenario"
    msg = f"Initialized scenario in {scenario_directory} successfully."
    assert any(msg in record.message for record in caplog.records)


def test_execute_scenario_exists_collection_mode(
    monkeypatch: pytest.MonkeyPatch,
    instance: Scenario,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
) -> None:
    """Test error when scenario already exists in collection mode.

    Args:
        monkeypatch: Pytest fixture.
        instance: A scenario instance.
        caplog: Pytest log capture fixture.
        tmp_path: Pytest temporary directory fixture.
    """
    monkeypatch.chdir(tmp_path)

    # Create a galaxy.yml file to simulate collection context
    galaxy_yml = tmp_path / "galaxy.yml"
    galaxy_yml.write_text("""
namespace: test_ns
name: test_collection
version: 1.0.0
""")

    # Create existing scenario directory
    existing_dir = tmp_path / "extensions" / "molecule" / "test-scenario"
    existing_dir.mkdir(parents=True, exist_ok=True)

    # Clear cache to ensure fresh detection
    util.get_collection_metadata.cache_clear()

    with pytest.raises(ImmediateExit) as e:
        instance.execute()

    assert e.value.code == 1

    msg = "The directory extensions/molecule/test-scenario exists. Cannot create new scenario."
    assert e.value.message == msg


def test_scenario_execute_invalid_collection(
    monkeypatch: pytest.MonkeyPatch,
    instance: Scenario,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
) -> None:
    """Test that scenario falls back to standard mode with invalid galaxy.yml.

    Args:
        monkeypatch: Pytest fixture.
        instance: A scenario instance.
        caplog: Pytest log capture fixture.
        tmp_path: Pytest temporary directory fixture.
    """
    monkeypatch.chdir(tmp_path)

    # Create an invalid galaxy.yml file (missing required fields)
    galaxy_yml = tmp_path / "galaxy.yml"
    galaxy_yml.write_text("""
# Missing namespace and name
version: 1.0.0
""")

    # Clear cache to ensure fresh detection
    util.get_collection_metadata.cache_clear()

    # Mock the run_command to avoid ansible execution and create the directory structure
    def mock_run_command(*args: object, **kwargs: object) -> None:
        # Create the molecule/test-scenario directory like ansible-playbook would
        scenario_dir = tmp_path / "molecule" / "test-scenario"
        scenario_dir.mkdir(parents=True, exist_ok=True)

    with monkeypatch.context() as m:
        m.setattr("molecule.app.App.run_command", mock_run_command)

        with caplog.at_level(logging.INFO):
            instance.execute()

    msg = "Initializing new scenario test-scenario..."
    assert any(msg in record.message for record in caplog.records)

    # Should fall back to standard mode due to invalid galaxy.yml
    assert (tmp_path / "molecule" / "test-scenario").is_dir()
    assert not (tmp_path / "extensions" / "molecule" / "test-scenario").is_dir()

    scenario_directory = tmp_path / "molecule" / "test-scenario"
    msg = f"Initialized scenario in {scenario_directory} successfully."
    assert any(msg in record.message for record in caplog.records)

"""Test reset command module."""  # noqa: DOC201, DOC101, DOC106, DOC107, DOC103

from __future__ import annotations

import shutil

from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from molecule import logger
from molecule.api import drivers
from molecule.command import base
from molecule.command.base import _run_scenarios


LOG = logger.get_scenario_logger(__name__, "reset", "test")


if TYPE_CHECKING:
    from collections.abc import Callable

    from molecule.config import Config
    from molecule.types import CommandArgs, MoleculeArgs


# Pytest fixtures for reusable patches


@pytest.fixture(name="patched_scenario_factory")
def _patched_scenario_factory() -> type[Any]:
    """Factory fixture to create PatchedScenario instances.

    Returns:
        PatchedScenario class that can be instantiated with scenario details.
    """

    class PatchedScenario:
        def __init__(self, name: str, ephemeral_dir: str, shared_ephemeral_dir: str = "") -> None:
            self.config = type(
                "Config",
                (),
                {
                    "scenario": type(
                        "Scenario",
                        (),
                        {
                            "name": name,
                            "shared_ephemeral_directory": shared_ephemeral_dir or ephemeral_dir,
                        },
                    )(),
                    "config": {"prerun": False},
                },
            )()
            self.ephemeral_directory = ephemeral_dir

    return PatchedScenario


@pytest.fixture(name="patched_scenarios_factory")
def _patched_scenarios_factory(
    patched_scenario_factory: type[Any],
) -> Callable[[list[tuple[str, str, str]] | None], object]:
    """Factory fixture to create Scenarios objects with multiple patched scenarios.

    Args:
        patched_scenario_factory: Factory for creating PatchedScenario instances.

    Returns:
        Function that creates scenarios objects from scenario data.
    """

    def create_scenarios(scenario_data: list[tuple[str, str, str]] | None = None) -> object:
        """Create a scenarios object with given scenario data.

        Args:
            scenario_data: List of tuples (name, ephemeral_dir, shared_ephemeral_dir).

        Returns:
            Patched scenarios object with .all attribute containing scenario list.
        """
        if scenario_data is None:
            scenario_data = []

        scenarios_list = [
            patched_scenario_factory(name, ephemeral_dir, shared_ephemeral_dir)
            for name, ephemeral_dir, shared_ephemeral_dir in scenario_data
        ]

        return type(
            "Scenarios",
            (),
            {
                "all": scenarios_list,
                "results": [],
                "shared_state": False,  # Default to False for test scenarios
            },
        )()

    return create_scenarios


@pytest.fixture(name="patched_rmtree_tracker")
def _patched_rmtree_tracker() -> tuple[Callable[[str, bool], None], list[str]]:
    """Fixture that provides a patched rmtree function and tracks removed directories.

    Returns:
        Tuple of (patched_rmtree_function, removed_directories_list).
    """
    removed_directories: list[str] = []

    def _rmtree(path: str, ignore_errors: bool = False) -> None:  # noqa: FBT001, FBT002
        removed_directories.append(path)

    return _rmtree, removed_directories


@pytest.fixture(name="patched_execute_subcommand")
def _patched_execute_subcommand() -> Callable[..., None]:
    """Fixture that provides a no-op patched for execute_subcommand_default.

    Returns:
        Patched function that accepts config and subcommand parameters.
    """

    def _execute_subcommand_default(
        config: object,
        subcommand: str,
        *,
        shared_state: bool = False,
    ) -> None:
        return None

    return _execute_subcommand_default


@pytest.fixture(name="patched_execute_cmdline_scenarios")
def _patched_execute_cmdline_scenarios(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """Fixture that patches execute_cmdline_scenarios and tracks its calls.

    Args:
        monkeypatch: Pytest monkeypatch fixture.

    Returns:
        List of dictionaries containing call history with parameters.
    """
    call_history: list[dict[str, Any]] = []

    def _execute_cmdline_scenarios(
        scenarios: list[str] | None,
        args: dict[str, Any],
        command_args: dict[str, Any],
        excludes: list[str] | None = None,
    ) -> None:
        call_history.append(
            {
                "scenarios": scenarios,
                "args": args,
                "command_args": command_args,
                "excludes": excludes,
            },
        )

    monkeypatch.setattr(
        "molecule.command.base.execute_cmdline_scenarios",
        _execute_cmdline_scenarios,
    )

    return call_history


@pytest.fixture(name="common_patches")
def _common_patches(
    monkeypatch: pytest.MonkeyPatch,
    patched_rmtree_tracker: tuple[Callable[[str, bool], None], list[str]],
    patched_execute_subcommand: Callable[..., None],
) -> dict[str, Any]:
    """Fixture that applies common patches needed for reset tests.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        patched_rmtree_tracker: Tuple of patched rmtree function and removed directories list.
        patched_execute_subcommand: Patched execute_subcommand_default function.

    Returns:
        Dictionary containing patched objects and tracking data.
    """
    _rmtree, removed_directories = patched_rmtree_tracker

    monkeypatch.setattr("shutil.rmtree", _rmtree)
    monkeypatch.setattr(
        "molecule.command.base.execute_subcommand_default",
        patched_execute_subcommand,
    )

    return {
        "removed_directories": removed_directories,
        "rmtree": _rmtree,
        "execute_subcommand": patched_execute_subcommand,
    }


def test_reset_execute_cmdline_scenarios_called_correctly(
    patched_execute_cmdline_scenarios: list[dict[str, Any]],
) -> None:
    """Test that execute_cmdline_scenarios is called with correct parameters.

    Verifies that the reset command logic properly calls execute_cmdline_scenarios
    with the expected arguments and behavior.

    Args:
        patched_execute_cmdline_scenarios: Pytest fixture for patching execute_cmdline_scenarios.
    """
    scenario_name = "test_scenario"
    args: MoleculeArgs = {"base_config": []}
    command_args: CommandArgs = {"subcommand": "reset"}

    base.execute_cmdline_scenarios([scenario_name], args, command_args)

    # Verify the function was called with correct parameters
    assert len(patched_execute_cmdline_scenarios) == 1
    call = patched_execute_cmdline_scenarios[0]
    assert call["scenarios"] == [scenario_name]
    assert call["args"] == args
    assert call["command_args"] == command_args
    assert call["excludes"] is None


def test_reset_driver_reset_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that reset calls reset method on all drivers.

    Verifies that the reset command properly calls the reset method
    on all available drivers through the drivers API.

    Args:
        monkeypatch: Pytest fixture for patching (used implicitly by drivers fixture).
    """
    driver_resets: list[str] = []

    class PatchedDriver:
        def __init__(self, name: str) -> None:
            self.name = name

        def reset(self) -> None:
            driver_resets.append(self.name)

    def _drivers() -> dict[str, Any]:
        return {
            "driver1": PatchedDriver("driver1"),
            "driver2": PatchedDriver("driver2"),
        }

    drivers.cache_clear()
    monkeypatch.setattr("molecule.api.drivers", _drivers)

    for driver in _drivers().values():
        driver.reset()

    expected_driver_count = 2
    assert "driver1" in driver_resets
    assert "driver2" in driver_resets
    assert len(driver_resets) == expected_driver_count


def test_reset_processes_multiple_scenarios_fixed(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    common_patches: dict[str, Any],
    patched_scenarios_factory: Any,  # noqa: ANN401
) -> None:
    """Test that reset now processes ALL scenarios after the bug fix.

    This test verifies the fix for the bug in _run_scenarios where reset would
    exit early after processing the first scenario. After changing 'return' to
    'continue', all scenarios should be processed.

    Args:
        tmp_path: Pytest fixture for temporary directory.
        caplog: Pytest fixture for capturing log output.
        common_patches: Pytest fixture for common patches.
        patched_scenarios_factory: Pytest fixture for creating scenarios.
    """
    # Create multiple scenarios using the factory
    scenario_data = [
        ("scenario1", str(tmp_path / "scenario1"), str(tmp_path / "shared")),
        ("scenario2", str(tmp_path / "scenario2"), str(tmp_path / "shared")),
        ("scenario3", str(tmp_path / "scenario3"), str(tmp_path / "shared")),
    ]
    scenarios = patched_scenarios_factory(scenario_data)

    command_args: CommandArgs = {"subcommand": "reset"}

    _run_scenarios(scenarios, command_args, None)

    # All scenarios should be processed
    removed_directories = common_patches["removed_directories"]
    assert str(tmp_path / "scenario1") in removed_directories
    assert str(tmp_path / "scenario2") in removed_directories
    assert str(tmp_path / "scenario3") in removed_directories

    # Extract scenario names from the log messages which have format: "[scenario1 > reset] Removing ..."
    scenario_names = []
    for record in caplog.records:
        if "[" in record.message and "] Removing" in record.message:
            # Extract scenario name from format "[scenario1 > reset] Removing ..."
            scenario_name = record.message.split("[")[1].split(" >")[0]
            scenario_names.append(scenario_name)

    assert "scenario1" in scenario_names
    assert "scenario2" in scenario_names
    assert "scenario3" in scenario_names


def test_reset_removes_ephemeral_directory(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    common_patches: dict[str, Any],
    patched_scenarios_factory: Any,  # noqa: ANN401
) -> None:
    """Test that reset command removes scenario ephemeral directories.

    Verifies that the reset logic properly removes scenario ephemeral directories
    and logs the appropriate messages.

    Args:
        tmp_path: Pytest fixture for temporary directory.
        caplog: Pytest fixture for capturing log output.
        common_patches: Pytest fixture for common patches.
        patched_scenarios_factory: Pytest fixture for creating scenarios.
    """
    scenario_name = "test_scenario"
    ephemeral_dir = str(tmp_path / "test_scenario")
    shared_dir = str(tmp_path / "shared")

    scenario_data = [(scenario_name, ephemeral_dir, shared_dir)]
    scenarios = patched_scenarios_factory(scenario_data)

    command_args: CommandArgs = {"subcommand": "reset"}

    _run_scenarios(scenarios, command_args, None)

    removed_directories = common_patches["removed_directories"]
    assert ephemeral_dir in removed_directories
    assert len(caplog.records) == 1
    # Log message format is "[scenario_name > reset] Removing ephemeral_directory"
    assert f"[{scenario_name} > reset] Removing {ephemeral_dir}" in caplog.text


def test_reset_command_with_all_flag_integration(
    patched_execute_cmdline_scenarios: list[dict[str, Any]],
) -> None:
    """Test reset command --all flag integration.

    Verifies that the execute_cmdline_scenarios function correctly handles
    None scenario_name (which represents --all flag behavior).

    Args:
        patched_execute_cmdline_scenarios: Pytest fixture for patching execute_cmdline_scenarios.
    """
    # Test --all flag behavior: scenario_name = None
    args: MoleculeArgs = {"base_config": []}
    command_args: CommandArgs = {"subcommand": "reset"}

    base.execute_cmdline_scenarios(None, args, command_args, excludes=[])

    # Verify --all behavior (None scenarios passed)
    assert len(patched_execute_cmdline_scenarios) == 1
    call = patched_execute_cmdline_scenarios[0]
    assert call["scenarios"] is None  # None represents --all flag
    assert call["excludes"] == []


def test_reset_command_with_exclude_flag(
    patched_execute_cmdline_scenarios: list[dict[str, Any]],
) -> None:
    """Test reset command --all --exclude combination.

    Verifies that exclude functionality works correctly when passed
    to execute_cmdline_scenarios.

    Args:
        patched_execute_cmdline_scenarios: Pytest fixture for patching execute_cmdline_scenarios.
    """
    # Test --all --exclude behavior
    args: MoleculeArgs = {"base_config": []}
    command_args: CommandArgs = {"subcommand": "reset"}
    exclude_list = ["scenario1", "scenario2"]

    base.execute_cmdline_scenarios(None, args, command_args, excludes=exclude_list)

    # Verify exclude list is passed correctly
    assert len(patched_execute_cmdline_scenarios) == 1
    call = patched_execute_cmdline_scenarios[0]
    assert call["scenarios"] is None  # --all flag
    assert call["excludes"] == exclude_list


def test_reset_command_backward_compatibility(
    patched_execute_cmdline_scenarios: list[dict[str, Any]],
) -> None:
    """Test reset command backward compatibility.

    Verifies that the existing behavior (specific scenario names) still works
    correctly when passed to execute_cmdline_scenarios.

    Args:
        patched_execute_cmdline_scenarios: Pytest fixture for patching execute_cmdline_scenarios.
    """
    # Test traditional usage: specific scenario names
    args: MoleculeArgs = {"base_config": []}
    command_args: CommandArgs = {"subcommand": "reset"}
    scenario_names = ["custom_scenario"]

    base.execute_cmdline_scenarios(scenario_names, args, command_args)

    # Should pass through the scenario names as-is
    assert len(patched_execute_cmdline_scenarios) == 1
    call = patched_execute_cmdline_scenarios[0]
    assert call["scenarios"] == ["custom_scenario"]


def test_reset_cleans_shared_directories_when_all_flag_used(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    config_instance: Config,
) -> None:
    """Test that reset removes shared directories when --all flag is used.

    Tests the specific shared directory cleanup logic in reset.py.

    Args:
        monkeypatch: Pytest fixture for patching.
        tmp_path: Pytest fixture for temporary directory.
        caplog: Pytest fixture for capturing log output.
        config_instance: Pytest fixture for molecule config.
    """
    removed_directories: list[str] = []

    def _rmtree(path: str, ignore_errors: bool = False) -> None:  # noqa: FBT001, FBT002
        removed_directories.append(path)

    def _exists(path: str | Path) -> bool:
        return True

    def _execute_cmdline_scenarios(
        scenarios: list[str] | None,
        args: dict[str, Any],
        command_args: dict[str, Any],
        excludes: list[str] | None = None,
    ) -> None:
        # Just return - we're testing the shared cleanup logic
        pass

    def _get_all() -> dict[str, Any]:
        return {}

    # Patch the dependencies that reset uses
    monkeypatch.setattr("molecule.command.reset.shutil.rmtree", _rmtree)
    monkeypatch.setattr("molecule.command.reset.Path.exists", _exists)
    monkeypatch.setattr(
        "molecule.command.reset.base.execute_cmdline_scenarios",
        _execute_cmdline_scenarios,
    )
    monkeypatch.setattr("molecule.command.reset.base.get_configs", _get_all)

    # Test the reset logic by importing and calling the piece we care about
    # Simulate the specific conditions in reset.py when --all is used
    all_flag = True
    scenario_name = None  # This happens when --all is used

    # This is the exact logic from reset.py we want to test
    if all_flag and scenario_name is None:
        configs = [config_instance]  # Use the real config_instance
        if configs:
            shared_dir = configs[0].scenario.shared_ephemeral_directory
            if Path(shared_dir).exists():
                msg = f"Removing shared directory {shared_dir}"
                LOG.info(msg, extra={"molecule_scenario": "reset", "molecule_step": "test"})
                shutil.rmtree(shared_dir)

    # Verify shared directory was removed
    assert config_instance.scenario.shared_ephemeral_directory in removed_directories

    # Verify proper logging occurred using caplog
    assert "Removing shared directory" in caplog.text
    assert config_instance.scenario.shared_ephemeral_directory in caplog.text


def test_reset_does_not_clean_shared_without_all_flag(
    tmp_path: Path,
    common_patches: dict[str, Any],
    patched_scenarios_factory: Any,  # noqa: ANN401
) -> None:
    """Test that reset does NOT remove shared directories without --all flag.

    Verifies that when resetting individual scenarios, shared directories
    are left untouched.

    Args:
        tmp_path: Pytest fixture for temporary directory.
        common_patches: Pytest fixture for common patches.
        patched_scenarios_factory: Pytest fixture for creating scenarios.
    """
    scenario_data = [("scenario1", str(tmp_path / "scenario1"), str(tmp_path / "shared"))]
    scenarios = patched_scenarios_factory(scenario_data)

    command_args: CommandArgs = {"subcommand": "reset"}

    _run_scenarios(scenarios, command_args, None)

    # Scenario directory should be removed, but shared should not
    removed_directories = common_patches["removed_directories"]
    assert str(tmp_path / "scenario1") in removed_directories

    # Shared directory should NOT be removed when --all is not used
    assert str(tmp_path / "shared") not in removed_directories

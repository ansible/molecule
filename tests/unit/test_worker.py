"""Tests for the parallel worker execution module."""

from __future__ import annotations

import os

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from molecule.exceptions import MoleculeError, ScenarioFailureError
from molecule.reporting.definitions import ScenarioResults
from molecule.worker import run_one_scenario, run_scenarios_parallel, validate_worker_args


if TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from molecule.types import CommandArgs, MoleculeArgs


# --- validate_worker_args ---


def test_validate_workers_1_passes() -> None:
    """No validation error when workers is 1."""
    command_args: CommandArgs = {"workers": 1, "subcommand": "test"}
    validate_worker_args(command_args)


def test_validate_workers_missing_passes() -> None:
    """No validation error when workers is not set."""
    command_args: CommandArgs = {"subcommand": "test"}
    validate_worker_args(command_args)


def test_validate_workers_gt1_not_collection_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Error when workers > 1 outside collection mode.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    monkeypatch.setattr(
        "molecule.worker.util.get_collection_metadata",
        lambda: (None, None),
    )
    command_args: CommandArgs = {"workers": 4, "subcommand": "test"}
    with pytest.raises(MoleculeError) as exc_info:
        validate_worker_args(command_args)
    assert "collection mode" in exc_info.value.message


def test_validate_workers_gt1_destroy_never_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Error when workers > 1 combined with destroy=never.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    monkeypatch.setattr(
        "molecule.worker.util.get_collection_metadata",
        lambda: ("/some/path", {"name": "test", "namespace": "ns"}),
    )
    command_args: CommandArgs = {"workers": 4, "destroy": "never", "subcommand": "test"}
    with pytest.raises(MoleculeError) as exc_info:
        validate_worker_args(command_args)
    assert "destroy=never" in exc_info.value.message


def test_validate_workers_gt1_in_collection_passes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No error when workers > 1 in collection mode without destroy=never.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    monkeypatch.setattr(
        "molecule.worker.util.get_collection_metadata",
        lambda: ("/some/path", {"name": "test", "namespace": "ns"}),
    )
    command_args: CommandArgs = {"workers": 4, "destroy": "always", "subcommand": "test"}
    validate_worker_args(command_args)


# --- run_one_scenario ---


def _patch_run_one(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
    *,
    scenario_name: str = "test_scenario",
    execute_side_effect: Exception | None = None,
    action: str = "",
) -> tuple[MagicMock, MagicMock, MagicMock]:
    """Patch dependencies for run_one_scenario tests.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        mocker: Pytest mocker fixture.
        scenario_name: Name for the mock scenario.
        execute_side_effect: Optional exception for execute_scenario to raise.
        action: Value for mock config's action attribute.

    Returns:
        Tuple of (mock_configure, mock_config_cls, mock_execute).
    """
    monkeypatch.setattr("molecule.worker.os.chdir", lambda _p: None)

    mock_scenario = MagicMock()
    mock_scenario.results = ScenarioResults(name=scenario_name, actions=[])

    mock_config = MagicMock()
    mock_config.scenario = mock_scenario
    if action:
        mock_config.action = action

    mock_config_cls = mocker.patch(
        "molecule.worker.config_module.Config",
        return_value=mock_config,
    )
    mock_configure = mocker.patch("molecule.worker.logger.configure")
    mock_execute = mocker.patch("molecule.worker.execute_scenario")
    if execute_side_effect:
        mock_execute.side_effect = execute_side_effect

    return mock_configure, mock_config_cls, mock_execute


def test_run_one_returns_results_on_success(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
) -> None:
    """Worker function returns (ScenarioResults, None, '', '') on success.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        mocker: Pytest mocker fixture.
    """
    mock_configure, mock_config_cls, mock_execute = _patch_run_one(
        monkeypatch,
        mocker,
    )

    args: MoleculeArgs = {}
    command_args: CommandArgs = {"subcommand": "test"}

    result, error, ansible_output, failed_step = run_one_scenario(
        "/path/to/molecule.yml",
        args,
        command_args,
        (),
        "/path/to",
    )

    mock_configure.assert_called_once()
    mock_config_cls.assert_called_once_with(
        molecule_file="/path/to/molecule.yml",
        args=args,
        command_args={**command_args, "force": True},
        ansible_args=(),
    )
    mock_execute.assert_called_once()
    assert result.name == "test_scenario"
    assert error is None
    assert ansible_output == ""
    assert failed_step == ""


def test_run_one_returns_error_on_failure(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
) -> None:
    """Worker function returns (results, error_msg, ansible_output, step) on failure.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        mocker: Pytest mocker fixture.
    """
    _patch_run_one(
        monkeypatch,
        mocker,
        scenario_name="failing_scenario",
        action="converge",
        execute_side_effect=ScenarioFailureError(
            message="converge failed",
            ansible_output="TASK [fail] ***\nfatal: FAILED!",
        ),
    )

    args: MoleculeArgs = {}
    command_args: CommandArgs = {"subcommand": "test"}

    result, error, ansible_output, failed_step = run_one_scenario(
        "/path/to/molecule.yml",
        args,
        command_args,
        (),
        "/path/to",
    )

    assert result.name == "failing_scenario"
    assert error is not None
    assert "converge failed" in error
    assert "TASK [fail]" in ansible_output
    assert failed_step == "converge"


def test_run_one_sets_quiet_ansible_when_not_verbose(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
) -> None:
    """MOLECULE_QUIET_ANSIBLE is set when verbose=0 and debug=False.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        mocker: Pytest mocker fixture.
    """
    monkeypatch.delenv("MOLECULE_QUIET_ANSIBLE", raising=False)
    _patch_run_one(monkeypatch, mocker, scenario_name="s")

    args: MoleculeArgs = {"verbose": 0, "debug": False}
    command_args: CommandArgs = {"subcommand": "test"}

    run_one_scenario("/path/to/molecule.yml", args, command_args, (), "/path/to")

    assert os.environ.get("MOLECULE_QUIET_ANSIBLE") == "1"


def test_run_one_does_not_set_quiet_ansible_when_verbose(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
) -> None:
    """MOLECULE_QUIET_ANSIBLE is NOT set when verbose > 0.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        mocker: Pytest mocker fixture.
    """
    monkeypatch.delenv("MOLECULE_QUIET_ANSIBLE", raising=False)
    _patch_run_one(monkeypatch, mocker, scenario_name="s")

    args: MoleculeArgs = {"verbose": 1, "debug": False}
    command_args: CommandArgs = {"subcommand": "test"}

    run_one_scenario("/path/to/molecule.yml", args, command_args, (), "/path/to")

    assert os.environ.get("MOLECULE_QUIET_ANSIBLE") is None


# --- run_scenarios_parallel ---


def _make_mock_scenarios(
    names: list[str],
    *,
    shared_state: bool = True,
    prerun: bool = False,
) -> MagicMock:
    """Create a mock Scenarios object with named scenarios.

    Args:
        names: Scenario names to create.
        shared_state: Whether shared_state is enabled.
        prerun: Whether prerun is enabled.

    Returns:
        A MagicMock Scenarios object.
    """
    mock_scenarios = MagicMock()
    mock_scenarios.shared_state = shared_state

    scenario_list = []
    for name in names:
        scenario = MagicMock()
        scenario.name = name
        scenario.config.molecule_file = f"/path/{name}/molecule.yml"
        scenario.config.args = {}
        scenario.config.command_args = {"subcommand": "test"}
        scenario.config.ansible_args = ()
        scenario.config.config = {"prerun": prerun, "role_name_check": 0}
        scenario.config.scenario.name = name
        scenario.ephemeral_directory = f"/tmp/{name}"  # noqa: S108
        scenario_list.append(scenario)

    mock_scenarios.all = scenario_list
    mock_scenarios.results = MagicMock()
    return mock_scenarios


def _make_mock_pool(
    mocker: MockerFixture,
    futures: list[MagicMock] | None = None,
) -> MagicMock:
    """Create a mock ProcessPoolExecutor and patch it into worker module.

    Args:
        mocker: Pytest mocker fixture.
        futures: Optional list of futures for submit to return.

    Returns:
        The mock pool instance.
    """
    mock_pool = MagicMock()
    mock_pool.__enter__ = MagicMock(return_value=mock_pool)
    mock_pool.__exit__ = MagicMock(return_value=False)
    if futures:
        mock_pool.submit.side_effect = futures
    mocker.patch("molecule.worker.ProcessPoolExecutor", return_value=mock_pool)
    return mock_pool


def test_parallel_runs_create_and_destroy(mocker: MockerFixture) -> None:
    """Default create runs before workers, destroy runs after.

    Args:
        mocker: Pytest mocker fixture.
    """
    mock_exec_default = mocker.patch(
        "molecule.worker.execute_subcommand_default",
        return_value=None,
    )
    _make_mock_pool(mocker)

    scenarios = _make_mock_scenarios([])
    default_config = MagicMock()
    command_args: CommandArgs = {"workers": 2, "subcommand": "test"}

    run_scenarios_parallel(scenarios, command_args, default_config, num_workers=2)

    assert mock_exec_default.call_count == 2  # noqa: PLR2004
    calls = mock_exec_default.call_args_list
    assert calls[0].args[1] == "create"
    assert calls[1].args[1] == "destroy"


def test_parallel_collects_results(mocker: MockerFixture) -> None:
    """Results from successful workers are appended to scenarios.results.

    Args:
        mocker: Pytest mocker fixture.
    """
    mocker.patch("molecule.worker.execute_subcommand_default", return_value=None)

    future = MagicMock()
    result = ScenarioResults(name="scenario_a", actions=[])
    future.result.return_value = (result, None, "", "")
    mocker.patch("molecule.worker.as_completed", return_value=[future])

    _make_mock_pool(mocker, futures=[future])

    scenarios = _make_mock_scenarios(["scenario_a"])
    command_args: CommandArgs = {"workers": 2, "subcommand": "test"}

    run_scenarios_parallel(scenarios, command_args, None, num_workers=2)

    scenarios.results.append.assert_called_with(result)  # pylint: disable=no-member


def test_parallel_fail_fast_on_failure(mocker: MockerFixture) -> None:
    """Fail-fast shuts down executor on first failure.

    Args:
        mocker: Pytest mocker fixture.
    """
    mocker.patch("molecule.worker.execute_subcommand_default", return_value=None)

    future = MagicMock()
    failed_result = ScenarioResults(name="failing_scenario", actions=[])
    future.result.return_value = (
        failed_result,
        "converge failed",
        "fatal: FAILED!",
        "converge",
    )
    mocker.patch("molecule.worker.as_completed", return_value=[future])

    mock_pool = _make_mock_pool(mocker, futures=[future])

    scenarios = _make_mock_scenarios(["failing_scenario"])
    command_args: CommandArgs = {
        "workers": 2,
        "continue_on_failure": False,
        "subcommand": "test",
    }

    with pytest.raises(ScenarioFailureError) as exc_info:
        run_scenarios_parallel(scenarios, command_args, None, num_workers=2)
    assert "Scenarios failed" in exc_info.value.message

    mock_pool.shutdown.assert_called_once_with(wait=True, cancel_futures=True)
    scenarios.results.append.assert_called_with(failed_result)  # pylint: disable=no-member


def test_parallel_continue_on_failure(mocker: MockerFixture) -> None:
    """With continue_on_failure, executor is not shut down on failure.

    Args:
        mocker: Pytest mocker fixture.
    """
    mocker.patch("molecule.worker.execute_subcommand_default", return_value=None)

    future_fail = MagicMock()
    failed_result = ScenarioResults(name="failing", actions=[])
    future_fail.result.return_value = (failed_result, "converge failed", "", "converge")
    future_ok = MagicMock()
    ok_result = ScenarioResults(name="ok", actions=[])
    future_ok.result.return_value = (ok_result, None, "", "")
    mocker.patch("molecule.worker.as_completed", return_value=[future_fail, future_ok])

    mock_pool = _make_mock_pool(mocker, futures=[future_fail, future_ok])

    scenarios = _make_mock_scenarios(["failing", "passing"])
    command_args: CommandArgs = {
        "workers": 2,
        "continue_on_failure": True,
        "subcommand": "test",
    }

    with pytest.raises(ScenarioFailureError) as exc_info:
        run_scenarios_parallel(scenarios, command_args, None, num_workers=2)
    assert "Scenarios failed" in exc_info.value.message

    mock_pool.shutdown.assert_not_called()
    assert scenarios.results.append.call_count >= 2  # noqa: PLR2004  # pylint: disable=no-member

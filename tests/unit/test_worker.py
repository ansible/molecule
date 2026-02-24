"""Tests for the parallel worker execution module."""

from __future__ import annotations

import copy

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from molecule.exceptions import MoleculeError, ScenarioFailureError
from molecule.reporting.definitions import ScenarioResults
from molecule.worker import run_one_scenario, run_scenarios_parallel, validate_worker_args


if TYPE_CHECKING:
    from molecule.types import CommandArgs, MoleculeArgs


class TestValidateWorkerArgs:
    """Tests for validate_worker_args."""

    def test_workers_1_passes(self) -> None:
        """No validation error when workers is 1."""
        command_args: CommandArgs = {"workers": 1, "subcommand": "test"}
        validate_worker_args(command_args)

    def test_workers_missing_passes(self) -> None:
        """No validation error when workers is not set."""
        command_args: CommandArgs = {"subcommand": "test"}
        validate_worker_args(command_args)

    @patch("molecule.worker.util.get_collection_metadata")
    def test_workers_gt1_not_collection_raises(
        self,
        mock_metadata: MagicMock,
    ) -> None:
        """Error when workers > 1 outside collection mode."""
        mock_metadata.return_value = (None, None)
        command_args: CommandArgs = {"workers": 4, "subcommand": "test"}
        with pytest.raises(MoleculeError) as exc_info:
            validate_worker_args(command_args)
        assert "collection mode" in exc_info.value.message

    @patch("molecule.worker.util.get_collection_metadata")
    def test_workers_gt1_destroy_never_raises(
        self,
        mock_metadata: MagicMock,
    ) -> None:
        """Error when workers > 1 combined with destroy=never."""
        mock_metadata.return_value = ("/some/path", {"name": "test", "namespace": "ns"})
        command_args: CommandArgs = {"workers": 4, "destroy": "never", "subcommand": "test"}
        with pytest.raises(MoleculeError) as exc_info:
            validate_worker_args(command_args)
        assert "destroy=never" in exc_info.value.message

    @patch("molecule.worker.util.get_collection_metadata")
    def test_workers_gt1_in_collection_passes(
        self,
        mock_metadata: MagicMock,
    ) -> None:
        """No error when workers > 1 in collection mode without destroy=never."""
        mock_metadata.return_value = ("/some/path", {"name": "test", "namespace": "ns"})
        command_args: CommandArgs = {"workers": 4, "destroy": "always", "subcommand": "test"}
        validate_worker_args(command_args)


class TestRunOneScenario:
    """Tests for run_one_scenario."""

    @patch("molecule.worker.os.chdir")
    @patch("molecule.worker.execute_scenario")
    @patch("molecule.worker.config_module.Config")
    @patch("molecule.worker.logger.configure")
    def test_returns_results_and_no_error_on_success(
        self,
        mock_configure: MagicMock,
        mock_config_cls: MagicMock,
        mock_execute: MagicMock,
        mock_chdir: MagicMock,
    ) -> None:
        """Worker function returns (ScenarioResults, None) on success."""
        mock_scenario = MagicMock()
        mock_scenario.results = ScenarioResults(name="test_scenario", actions=[])
        mock_config = MagicMock()
        mock_config.scenario = mock_scenario
        mock_config_cls.return_value = mock_config

        args: MoleculeArgs = {}
        command_args: CommandArgs = {"subcommand": "test"}

        result, error = run_one_scenario(
            "/path/to/molecule.yml", args, command_args, (), "/path/to",
        )

        mock_configure.assert_called_once()
        mock_config_cls.assert_called_once_with(
            molecule_file="/path/to/molecule.yml",
            args=args,
            command_args=command_args,
            ansible_args=(),
        )
        mock_execute.assert_called_once_with(mock_scenario, shared_state=True)
        assert result.name == "test_scenario"
        assert error is None

    @patch("molecule.worker.os.chdir")
    @patch("molecule.worker.execute_scenario")
    @patch("molecule.worker.config_module.Config")
    @patch("molecule.worker.logger.configure")
    def test_returns_results_and_error_on_failure(
        self,
        mock_configure: MagicMock,
        mock_config_cls: MagicMock,
        mock_execute: MagicMock,
        mock_chdir: MagicMock,
    ) -> None:
        """Worker function returns (partial_results, error_msg) on failure."""
        mock_scenario = MagicMock()
        mock_scenario.results = ScenarioResults(name="failing_scenario", actions=[])
        mock_config = MagicMock()
        mock_config.scenario = mock_scenario
        mock_config_cls.return_value = mock_config
        mock_execute.side_effect = ScenarioFailureError(message="converge failed")

        args: MoleculeArgs = {}
        command_args: CommandArgs = {"subcommand": "test"}

        result, error = run_one_scenario(
            "/path/to/molecule.yml", args, command_args, (), "/path/to",
        )

        assert result.name == "failing_scenario"
        assert error is not None
        assert "converge failed" in error


class TestRunScenariosParallel:
    """Tests for run_scenarios_parallel."""

    def _make_mock_scenarios(
        self,
        names: list[str],
        *,
        shared_state: bool = True,
        prerun: bool = False,
    ) -> MagicMock:
        """Create a mock Scenarios object with named scenarios."""
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
            scenario.ephemeral_directory = f"/tmp/{name}"
            scenario_list.append(scenario)

        mock_scenarios.all = scenario_list
        mock_scenarios.results = MagicMock()
        return mock_scenarios

    @patch("molecule.worker.ProcessPoolExecutor")
    @patch("molecule.worker.execute_subcommand_default")
    def test_runs_create_and_destroy(
        self,
        mock_exec_default: MagicMock,
        mock_pool_cls: MagicMock,
    ) -> None:
        """Default create runs before workers, destroy runs after."""
        mock_exec_default.return_value = None
        mock_pool = MagicMock()
        mock_pool.__enter__ = MagicMock(return_value=mock_pool)
        mock_pool.__exit__ = MagicMock(return_value=False)
        mock_pool.submit.return_value = MagicMock()
        mock_pool_cls.return_value = mock_pool

        scenarios = self._make_mock_scenarios([])
        default_config = MagicMock()
        command_args: CommandArgs = {"workers": 2, "subcommand": "test"}

        run_scenarios_parallel(scenarios, command_args, default_config, num_workers=2)

        assert mock_exec_default.call_count == 2
        calls = mock_exec_default.call_args_list
        assert calls[0].args[1] == "create"
        assert calls[1].args[1] == "destroy"

    @patch("molecule.worker.as_completed")
    @patch("molecule.worker.ProcessPoolExecutor")
    @patch("molecule.worker.execute_subcommand_default")
    def test_collects_results(
        self,
        mock_exec_default: MagicMock,
        mock_pool_cls: MagicMock,
        mock_as_completed: MagicMock,
    ) -> None:
        """Results from successful workers are appended to scenarios.results."""
        mock_exec_default.return_value = None

        future = MagicMock()
        result = ScenarioResults(name="scenario_a", actions=[])
        future.result.return_value = (result, None)
        mock_as_completed.return_value = [future]

        mock_pool = MagicMock()
        mock_pool.__enter__ = MagicMock(return_value=mock_pool)
        mock_pool.__exit__ = MagicMock(return_value=False)
        mock_pool.submit.return_value = future
        mock_pool_cls.return_value = mock_pool

        scenarios = self._make_mock_scenarios(["scenario_a"])
        command_args: CommandArgs = {"workers": 2, "subcommand": "test"}

        run_scenarios_parallel(scenarios, command_args, None, num_workers=2)

        scenarios.results.append.assert_called_with(result)

    @patch("molecule.worker.as_completed")
    @patch("molecule.worker.ProcessPoolExecutor")
    @patch("molecule.worker.execute_subcommand_default")
    def test_fail_fast_on_failure(
        self,
        mock_exec_default: MagicMock,
        mock_pool_cls: MagicMock,
        mock_as_completed: MagicMock,
    ) -> None:
        """Fail-fast shuts down executor on first failure."""
        mock_exec_default.return_value = None

        future = MagicMock()
        failed_result = ScenarioResults(name="failing_scenario", actions=[])
        future.result.return_value = (failed_result, "converge failed")
        mock_as_completed.return_value = [future]

        mock_pool = MagicMock()
        mock_pool.__enter__ = MagicMock(return_value=mock_pool)
        mock_pool.__exit__ = MagicMock(return_value=False)
        mock_pool.submit.return_value = future
        mock_pool_cls.return_value = mock_pool

        scenarios = self._make_mock_scenarios(["failing_scenario"])
        command_args: CommandArgs = {
            "workers": 2,
            "continue_on_failure": False,
            "subcommand": "test",
        }

        with pytest.raises(ScenarioFailureError) as exc_info:
            run_scenarios_parallel(scenarios, command_args, None, num_workers=2)
        assert "Scenarios failed" in exc_info.value.message

        mock_pool.shutdown.assert_called_once_with(wait=True, cancel_futures=True)
        scenarios.results.append.assert_called_with(failed_result)

    @patch("molecule.worker.as_completed")
    @patch("molecule.worker.ProcessPoolExecutor")
    @patch("molecule.worker.execute_subcommand_default")
    def test_continue_on_failure(
        self,
        mock_exec_default: MagicMock,
        mock_pool_cls: MagicMock,
        mock_as_completed: MagicMock,
    ) -> None:
        """With continue_on_failure, executor is not shut down on failure."""
        mock_exec_default.return_value = None

        future_fail = MagicMock()
        failed_result = ScenarioResults(name="fail_scen", actions=[])
        future_fail.result.return_value = (failed_result, "converge failed")
        future_ok = MagicMock()
        ok_result = ScenarioResults(name="ok", actions=[])
        future_ok.result.return_value = (ok_result, None)
        mock_as_completed.return_value = [future_fail, future_ok]

        mock_pool = MagicMock()
        mock_pool.__enter__ = MagicMock(return_value=mock_pool)
        mock_pool.__exit__ = MagicMock(return_value=False)
        mock_pool.submit.side_effect = [future_fail, future_ok]
        mock_pool_cls.return_value = mock_pool

        scenarios = self._make_mock_scenarios(["fail_scen", "ok_scen"])
        command_args: CommandArgs = {
            "workers": 2,
            "continue_on_failure": True,
            "subcommand": "test",
        }

        with pytest.raises(ScenarioFailureError) as exc_info:
            run_scenarios_parallel(scenarios, command_args, None, num_workers=2)
        assert "Scenarios failed" in exc_info.value.message

        mock_pool.shutdown.assert_not_called()
        assert scenarios.results.append.call_count >= 2

"""Parallel worker execution for collection scenarios.

Uses concurrent.futures.ProcessPoolExecutor to run multiple scenarios
concurrently while the default scenario's create/destroy lifecycle
is managed serially in the main process.
"""

from __future__ import annotations

import copy
import logging
import os
import shutil

from concurrent.futures import Future, ProcessPoolExecutor, as_completed
from typing import TYPE_CHECKING

from molecule import config as config_module
from molecule import logger, util
from molecule.command.base import (
    execute_scenario,
    execute_subcommand_default,
)
from molecule.exceptions import ScenarioFailureError
from molecule.reporting.definitions import ScenarioResults


if TYPE_CHECKING:
    from molecule.scenarios import Scenarios
    from molecule.types import CommandArgs, MoleculeArgs

LOG = logging.getLogger(__name__)


def run_one_scenario(
    molecule_file: str,
    args: MoleculeArgs,
    command_args: CommandArgs,
    ansible_args: tuple[str, ...],
    project_directory: str,
) -> tuple[ScenarioResults, str | None]:
    """Execute a single scenario in a worker process.

    Reconstructs a Config from picklable arguments and runs the scenario's
    sequence, skipping create/destroy (handled by the default scenario in
    the main process).

    Always returns results (including partial results on failure) so that
    the report captures every scenario regardless of outcome.

    Args:
        molecule_file: Absolute path to the scenario's molecule.yml.
        args: Base molecule arguments dict.
        command_args: Command arguments dict.
        ansible_args: Tuple of extra ansible-playbook arguments.
        project_directory: Absolute path to the project directory.

    Returns:
        A tuple of (ScenarioResults, error_message). error_message is None
        on success, or a string describing the failure.
    """
    os.environ["MOLECULE_PROJECT_DIRECTORY"] = project_directory
    os.chdir(project_directory)

    logger.configure()
    cfg = config_module.Config(
        molecule_file=molecule_file,
        args=args,
        command_args=command_args,
        ansible_args=ansible_args,
    )
    scenario = cfg.scenario

    try:
        execute_scenario(scenario, shared_state=True)
    except Exception as exc:
        error_msg = getattr(exc, "message", None) or str(exc)
        return copy.deepcopy(scenario.results), error_msg
    return copy.deepcopy(scenario.results), None


def run_scenarios_parallel(
    scenarios: Scenarios,
    command_args: CommandArgs,
    default_config: config_module.Config | None,
    num_workers: int,
) -> None:
    """Run scenarios concurrently using a process pool.

    Handles the full lifecycle: default create, parallel scenario execution,
    and default destroy. Results are collected and failures are tracked.

    Args:
        scenarios: The Scenarios object holding all scenario objects.
        command_args: Dict of command arguments.
        default_config: Config for the default scenario (handles create/destroy).
        num_workers: Number of concurrent worker processes.

    Raises:
        ScenarioFailureError: If any scenario fails during execution.
    """
    continue_on_failure = command_args.get("continue_on_failure", False)

    create_results = execute_subcommand_default(
        default_config,
        "create",
        shared_state=scenarios.shared_state,
    )
    if create_results is not None:
        scenarios.results.append(create_results)

    for scenario in scenarios.all:
        if scenario.config.config["prerun"]:
            role_name_check = scenario.config.config["role_name_check"]
            scenario_log = logger.get_scenario_logger(
                __name__,
                scenario.config.scenario.name,
                "prerun",
            )
            scenario_log.info(
                f"Performing prerun with role_name_check={role_name_check}...",
            )
            scenario.config.runtime.prepare_environment(
                install_local=True,
                role_name_check=role_name_check,
            )

    if command_args.get("subcommand") == "reset":
        for scenario in scenarios.all:
            reset_log = logger.get_scenario_logger(
                __name__,
                scenario.config.scenario.name,
                "reset",
            )
            reset_log.info(f"Removing {scenario.ephemeral_directory}")
            shutil.rmtree(scenario.ephemeral_directory)
        return

    failed_scenarios: list[str] = []

    project_dir = scenarios.all[0].config.project_directory if scenarios.all else os.getcwd()

    LOG.info("Starting parallel execution with %d workers for %d scenarios", num_workers, len(scenarios.all))

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_name: dict[Future[tuple[ScenarioResults, str | None]], str] = {}
        for scenario in scenarios.all:
            mol_file = scenario.config.molecule_file
            mol_args = scenario.config.args
            ans_args = scenario.config.ansible_args
            future = executor.submit(
                run_one_scenario, mol_file, mol_args, command_args, ans_args, project_dir,
            )
            future_to_name[future] = scenario.config.scenario.name

        for future in as_completed(future_to_name):
            scenario_name = future_to_name[future]
            try:
                result, error = future.result()
            except Exception as exc:
                failed_scenarios.append(scenario_name)
                LOG.error("Scenario '%s' worker crashed: %s", scenario_name, exc)  # noqa: TRY400
                if not continue_on_failure:
                    LOG.warning(
                        "Fail-fast: cancelling remaining scenarios. "
                        "Use --continue-on-failure to run all scenarios.",
                    )
                    executor.shutdown(wait=True, cancel_futures=True)
                    break
                continue

            scenarios.results.append(result)

            if error:
                failed_scenarios.append(scenario_name)
                LOG.error("Scenario '%s' failed: %s", scenario_name, error)  # noqa: TRY400

                if not continue_on_failure:
                    LOG.warning(
                        "Fail-fast: cancelling remaining scenarios. "
                        "Use --continue-on-failure to run all scenarios.",
                    )
                    executor.shutdown(wait=True, cancel_futures=True)
                    break
            else:
                LOG.info("Scenario '%s' completed successfully", scenario_name)

    destroy_results = execute_subcommand_default(
        default_config,
        "destroy",
        shared_state=scenarios.shared_state,
    )
    if destroy_results is not None:
        scenarios.results.append(destroy_results)

    if failed_scenarios:
        names = ", ".join(failed_scenarios)
        msg = f"Scenarios failed: {names}"
        raise ScenarioFailureError(message=msg)


def validate_worker_args(command_args: CommandArgs) -> None:
    """Validate that --workers > 1 is used correctly.

    Args:
        command_args: Dict of command arguments.

    Raises:
        MoleculeError: If workers is used in an unsupported configuration.
    """
    from molecule.exceptions import MoleculeError

    workers = command_args.get("workers", 1)
    if workers <= 1:
        return

    collection_dir, _ = util.get_collection_metadata()
    if not collection_dir:
        msg = "--workers > 1 is only supported in collection mode (galaxy.yml required)."
        raise MoleculeError(msg)

    if command_args.get("destroy") == "never":
        msg = 'Combining "--workers" > 1 and "--destroy=never" is not supported.'
        raise MoleculeError(msg)

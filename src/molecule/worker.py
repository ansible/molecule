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
from pathlib import Path
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
    from molecule.scenario import Scenario
    from molecule.scenarios import Scenarios
    from molecule.types import CommandArgs, MoleculeArgs

LOG = logging.getLogger(__name__)


ScenarioEntry = tuple[str, str]
SliceResult = tuple[str, ScenarioResults, str | None, str, str]


def _slice_key(scenario_name: str, depth: int) -> str:
    """Derive the grouping key for a scenario at a given directory depth.

    Args:
        scenario_name: The scenario name (e.g. "appliance_vlans/gathered").
        depth: Number of path segments to include in the key.

    Returns:
        The prefix of the scenario name truncated to depth segments.
    """
    parts = scenario_name.split("/")
    return "/".join(parts[:depth])


def _group_scenarios_by_slice(
    scenarios: list[Scenario],
    depth: int,
) -> dict[str, list[Scenario]]:
    """Group scenarios by their name prefix at the given depth.

    Preserves the original sort order within each group.

    Args:
        scenarios: List of Scenario objects.
        depth: Directory depth for grouping (1 = top-level resource).

    Returns:
        Ordered dict of group_key -> list of scenarios.
    """
    groups: dict[str, list[Scenario]] = {}
    for scenario in scenarios:
        name = scenario.config.scenario.name
        key = _slice_key(name, depth)
        groups.setdefault(key, []).append(scenario)
    return groups


def run_scenario_slice(
    scenario_entries: list[ScenarioEntry],
    args: MoleculeArgs,
    command_args: CommandArgs,
    ansible_args: tuple[str, ...],
    project_directory: str,
) -> list[SliceResult]:
    """Execute a slice of scenarios sequentially in one worker process.

    Runs each scenario in order. Stops on first failure within the slice;
    remaining scenarios are skipped but still included in results as
    incomplete entries.

    Args:
        scenario_entries: List of (molecule_file, scenario_name) pairs.
        args: Base molecule arguments dict.
        command_args: Command arguments dict.
        ansible_args: Tuple of extra ansible-playbook arguments.
        project_directory: Absolute path to the project directory.

    Returns:
        List of (name, ScenarioResults, error, ansible_output, failed_step)
        tuples, one per scenario in the slice.
    """
    os.environ["MOLECULE_PROJECT_DIRECTORY"] = project_directory
    os.chdir(project_directory)

    verbose = args.get("verbose", 0)
    debug = args.get("debug", False)
    if not verbose and not debug:
        os.environ["MOLECULE_QUIET_ANSIBLE"] = "1"

    worker_command_args: CommandArgs = {**command_args, "force": True}
    logger.configure()

    results: list[SliceResult] = []
    for mol_file, name in scenario_entries:
        cfg = config_module.Config(
            molecule_file=mol_file,
            args=args,
            command_args=worker_command_args,
            ansible_args=ansible_args,
        )
        scenario = cfg.scenario

        try:
            execute_scenario(scenario, shared_state=True)
        except Exception as exc:  # noqa: BLE001
            error_msg = getattr(exc, "message", None) or str(exc)
            ansible_output = getattr(exc, "ansible_output", "") or ""
            failed_step = getattr(cfg, "action", "") or ""
            results.append(
                (name, copy.deepcopy(scenario.results), error_msg, ansible_output, failed_step)
            )
            break

        results.append((name, copy.deepcopy(scenario.results), None, "", ""))

    return results


def run_one_scenario(
    molecule_file: str,
    args: MoleculeArgs,
    command_args: CommandArgs,
    ansible_args: tuple[str, ...],
    project_directory: str,
) -> tuple[ScenarioResults, str | None, str, str]:
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
        A 4-tuple of (ScenarioResults, error_message, ansible_output, failed_step).
        error_message is None on success. ansible_output contains captured
        ansible stdout+stderr for the failing step. failed_step is the name
        of the action that failed (e.g. "verify", "converge").
    """
    os.environ["MOLECULE_PROJECT_DIRECTORY"] = project_directory
    os.chdir(project_directory)

    verbose = args.get("verbose", 0)
    debug = args.get("debug", False)
    if not verbose and not debug:
        os.environ["MOLECULE_QUIET_ANSIBLE"] = "1"

    # Force prepare to always run. With shared_state, all scenarios share
    # one state file and a single "prepared" flag. In sequential mode this
    # isn't a problem because all Config/State objects are created before
    # any scenario executes, so they all snapshot prepared=False in memory.
    # In worker mode each Config is created on-demand; later workers read
    # the file after earlier workers already wrote prepared=True, causing
    # their per-scenario prepare playbooks to be skipped.
    worker_command_args: CommandArgs = {**command_args, "force": True}

    logger.configure()
    cfg = config_module.Config(
        molecule_file=molecule_file,
        args=args,
        command_args=worker_command_args,
        ansible_args=ansible_args,
    )
    scenario = cfg.scenario

    try:
        execute_scenario(scenario, shared_state=True)
    except Exception as exc:  # noqa: BLE001
        error_msg = getattr(exc, "message", None) or str(exc)
        ansible_output = getattr(exc, "ansible_output", "") or ""
        failed_step = getattr(cfg, "action", "") or ""
        return copy.deepcopy(scenario.results), error_msg, ansible_output, failed_step
    return copy.deepcopy(scenario.results), None, "", ""


def _print_failed_output(failed_outputs: list[tuple[str, str, str]]) -> None:
    """Print captured ansible output for failed scenarios using bordered blocks.

    Args:
        failed_outputs: List of (scenario_name, ansible_output, failed_step) tuples.
    """
    from molecule.ansi_output import write_bordered_block  # noqa: PLC0415
    from molecule.console import original_stderr  # noqa: PLC0415
    from molecule.constants import ANSICodes as A  # noqa: PLC0415

    for name, output, step in failed_outputs:
        title = f"Failed: {name} > {step}" if step else f"Failed: {name}"
        write_bordered_block(
            stream=original_stderr,
            content=output,
            title=title,
            color=A.RED,
        )


def run_scenarios_parallel(  # noqa: C901, PLR0912, PLR0915
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
    failed_outputs: list[tuple[str, str, str]] = []

    project_dir = scenarios.all[0].config.project_directory if scenarios.all else str(Path.cwd())

    slice_depth = scenarios.slice
    groups = _group_scenarios_by_slice(scenarios.all, slice_depth)

    LOG.info(
        "Starting parallel execution with %d workers for %d scenarios (%d slices, depth=%d)",
        num_workers,
        len(scenarios.all),
        len(groups),
        slice_depth,
    )

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_group: dict[Future[list[SliceResult]], str] = {}
        for group_name, group_scenarios in groups.items():
            entries: list[ScenarioEntry] = [
                (s.config.molecule_file, s.config.scenario.name) for s in group_scenarios
            ]
            mol_args = group_scenarios[0].config.args
            ans_args = group_scenarios[0].config.ansible_args
            future = executor.submit(
                run_scenario_slice,
                entries,
                mol_args,
                command_args,
                ans_args,
                project_dir,
            )
            future_to_group[future] = group_name

        for future in as_completed(future_to_group):
            group_name = future_to_group[future]
            try:
                slice_results = future.result()
            except Exception as exc:  # noqa: BLE001
                failed_scenarios.append(group_name)
                LOG.error("Slice '%s' worker crashed: %s", group_name, exc)  # noqa: TRY400
                if not continue_on_failure:
                    LOG.warning(
                        "Fail-fast: cancelling remaining scenarios. "
                        "Use --continue-on-failure to run all scenarios.",
                    )
                    executor.shutdown(wait=True, cancel_futures=True)
                    break
                continue

            for name, result, error, ansible_output, failed_step in slice_results:
                scenarios.results.append(result)

                if error:
                    failed_scenarios.append(name)
                    LOG.error("Scenario '%s' failed: %s", name, error)
                    if ansible_output and ansible_output.strip():
                        failed_outputs.append((name, ansible_output.strip(), failed_step))
                else:
                    LOG.info("Scenario '%s' completed successfully", name)

            slice_had_failure = any(err for _, _, err, _, _ in slice_results)
            if slice_had_failure and not continue_on_failure:
                LOG.warning(
                    "Fail-fast: cancelling remaining scenarios. "
                    "Use --continue-on-failure to run all scenarios.",
                )
                executor.shutdown(wait=True, cancel_futures=True)
                break

    destroy_results = execute_subcommand_default(
        default_config,
        "destroy",
        shared_state=scenarios.shared_state,
    )
    if destroy_results is not None:
        scenarios.results.append(destroy_results)

    if failed_outputs:
        _print_failed_output(failed_outputs)

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
    from molecule.exceptions import MoleculeError  # noqa: PLC0415

    workers = command_args.get("workers", 1)
    if workers <= 1:
        slice_depth = command_args.get("slice", 1)
        if slice_depth != 1:
            msg = "--slice requires --workers > 1."
            raise MoleculeError(msg)
        return

    collection_dir, _ = util.get_collection_metadata()
    if not collection_dir:
        msg = "--workers > 1 is only supported in collection mode (galaxy.yml required)."
        raise MoleculeError(msg)

    if command_args.get("destroy") == "never":
        msg = 'Combining "--workers" > 1 and "--destroy=never" is not supported.'
        raise MoleculeError(msg)

#  Copyright (c) 2015-2018 Cisco Systems, Inc.
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
"""Base Command Module."""

from __future__ import annotations

import abc
import collections
import contextlib
import copy
import fnmatch
import importlib
import logging
import shutil
import subprocess

from pathlib import Path
from typing import TYPE_CHECKING, Any

import wcmatch.pathlib
import wcmatch.wcmatch

from wcmatch import glob

from molecule import config, logger, text, util
from molecule.constants import MOLECULE_COLLECTION_ROOT, MOLECULE_DEFAULT_SCENARIO_NAME
from molecule.exceptions import MoleculeError, ScenarioFailureError
from molecule.reporting.definitions import ScenarioResults
from molecule.reporting.rendering import report
from molecule.scenarios import Scenarios


if TYPE_CHECKING:
    from molecule.scenario import Scenario
    from molecule.types import CommandArgs, MoleculeArgs


def _log(scenario_name: str, step: str, message: str, level: str = "info") -> None:
    """Create scenario logger on-demand and log message.

    Args:
        scenario_name: Name of the scenario for context.
        step: Step name for context (e.g., 'discovery', 'prerun', 'reset').
        message: Log message (pre-formatted, no placeholders).
        level: Log level ('info', 'warning', 'error', 'debug').
    """
    scenario_log = logger.get_scenario_logger(__name__, scenario_name, step)
    getattr(scenario_log, level)(message)


class Base(abc.ABC):
    """An abstract base class used to define the command interface."""

    def __init__(self, c: config.Config) -> None:
        """Initialize code for all command classes.

        Args:
            c: An instance of a Molecule config.
        """
        self._config = c
        self._config.scenario.results.add_action_result(self._config.action or "unknown")
        self._setup()

    def __init_subclass__(cls) -> None:
        """Decorate execute from all subclasses."""
        super().__init_subclass__()
        for wrapper in logger.get_section_loggers():
            cls.execute = wrapper(cls.execute)  # type: ignore[method-assign,assignment]

    @property
    def _log(self) -> logger.ScenarioLoggerAdapter:
        """Get a scenario logger with command-specific step context.

        Returns:
            A scenario logger adapter with current scenario and step context.
        """
        step_name = self.__class__.__name__.lower()
        return logger.get_scenario_logger(__name__, self._config.scenario.name, step_name)

    @abc.abstractmethod
    def execute(
        self,
        action_args: list[str] | None = None,
    ) -> None:  # pragma: no cover
        """Abstract method to execute the command.

        Args:
            action_args: An optional list of arguments to pass to the action.
        """

    def _setup(self) -> None:
        """Prepare Molecule's provisioner and returns None."""
        self._config.write()
        if self._config.provisioner is not None:
            self._config.provisioner.write_config()
            self._config.provisioner.manage_inventory()


def _is_excluded(name: str, excludes: list[str]) -> bool:
    """Check if a scenario name matches any exclude pattern.

    Supports both exact names and glob-style wildcards (e.g., 'appliance_*/*').

    Args:
        name: The scenario name to check.
        excludes: List of exclude patterns (exact names or glob patterns).

    Returns:
        True if the name matches any exclude pattern.
    """
    for pattern in excludes:
        if pattern == name:
            return True
        if fnmatch.fnmatchcase(name, pattern):
            return True
    return False


def _resolve_scenario_glob(effective_base_glob: str, scenario_name: str) -> str:
    """Resolve a scenario name to a glob pattern for molecule.yml discovery.

    In collection mode (glob contains MOLECULE_COLLECTION_ROOT), uses path-based
    resolution to correctly handle both nested names ('appliance_vlans/merged')
    and flat names ('default') without corrupting multi-star globs like '**'.
    Outside collection mode, uses the existing str.replace behavior.

    Args:
        effective_base_glob: The base glob pattern (e.g., 'extensions/molecule/**/molecule.yml').
        scenario_name: The scenario name from -s (e.g., 'default' or 'appliance_vlans/merged').

    Returns:
        A glob string targeting the specific scenario's molecule.yml.

    Raises:
        ScenarioFailureError: If the scenario name contains path traversal sequences.
    """
    if ".." in scenario_name or scenario_name.startswith("/"):
        msg = f"Invalid scenario name '{scenario_name}': path traversal is not allowed."
        raise ScenarioFailureError(message=msg)

    is_collection = MOLECULE_COLLECTION_ROOT in effective_base_glob
    if is_collection:
        # Split on the first wildcard to get the scenarios root directory.
        # Assumes the glob follows the pattern <root>*<suffix> where the
        # first '*' marks the scenario placeholder.
        base_dir = effective_base_glob.split("*", maxsplit=1)[0]
        has_wildcard = glob.is_magic(scenario_name, flags=glob.BRACE)
        is_recursive = "**" in effective_base_glob
        if has_wildcard and is_recursive:
            # Preserve recursive matching so -s "camera_*" or -s "{camera,router}_*"
            # finds scenarios at any depth under matching directories.
            return str(Path(base_dir) / scenario_name / "**" / "molecule.yml")
        return str(Path(base_dir) / scenario_name / "molecule.yml")
    return effective_base_glob.replace("*", scenario_name)


def execute_cmdline_scenarios(
    scenario_names: list[str] | None,
    args: MoleculeArgs,
    command_args: CommandArgs,
    ansible_args: tuple[str, ...] = (),
    excludes: list[str] | None = None,
) -> None:
    """Execute scenario sequences based on parsed command-line arguments.

    This is useful for subcommands that run scenario sequences, which
    excludes subcommands such as ``list``, ``login``, and ``matrix``.

    ``args`` and ``command_args`` are combined using :func:`get_configs`
    to generate the scenario(s) configuration.

    Args:
        scenario_names: Name of scenarios to run, or ``None`` to run all.
        args: ``args`` dict from ``click`` command context
        command_args: dict of command arguments, including the target
        ansible_args: Optional tuple of arguments to pass to the `ansible-playbook` command
        excludes: Name of scenarios to not run.
    """
    if excludes is None:
        excludes = []

    effective_base_glob = util.get_effective_molecule_glob()

    configs: list[config.Config] = []
    if scenario_names is None:
        configs = [
            config
            for config in get_configs(args, command_args, ansible_args)
            if not _is_excluded(config.scenario.name, excludes)
        ]
    else:
        try:
            # filter out excludes
            scenario_names = [name for name in scenario_names if not _is_excluded(name, excludes)]
            for scenario_name in scenario_names:
                glob_str = _resolve_scenario_glob(effective_base_glob, scenario_name)
                configs.extend(get_configs(args, command_args, ansible_args, glob_str))
        except ScenarioFailureError as exc:
            util.sysexit_from_exception(exc)

        # When -s used glob wildcards (e.g. "appliance_vlans/*"), the resolved
        # configs may have expanded to multiple scenarios. Replace the original
        # names with the actual discovered names so Scenarios._verify matches.
        scenario_names = [c.scenario.name for c in configs]

    default_glob = _resolve_scenario_glob(effective_base_glob, MOLECULE_DEFAULT_SCENARIO_NAME)
    default_config = None
    try:
        default_config = get_configs(args, command_args, ansible_args, default_glob)[0]
    except MoleculeError:
        # Use a generic logger for this since it's not tied to a specific scenario
        logging.getLogger(__name__).info("default scenario not found, disabling shared state.")

    scenarios = _generate_scenarios(scenario_names, configs)

    try:
        _run_scenarios(scenarios, command_args, default_config)

    except ScenarioFailureError as exc:
        util.sysexit_from_exception(exc)
    finally:
        report(scenarios.results, report_flag=command_args.get("report", False))


def _generate_scenarios(
    scenario_names: list[str] | None,
    configs: list[config.Config],
) -> Scenarios:
    """Generate Scenarios object from names and configs.

    Args:
        scenario_names: Names of scenarios to include.
        configs: List of Config objects to consider.

    Returns:
        Combined Scenarios object.
    """
    scenarios = Scenarios(
        configs,
        scenario_names,
    )

    if scenario_names is not None:
        for scenario_name in scenario_names:
            if scenario_name != "*" and scenarios:
                # Use generic "discovery" step since this is scenario discovery phase
                _log(
                    scenario_name,
                    "discovery",
                    f"scenario test matrix: {', '.join(scenarios.sequence(scenario_name))}",
                )

    return scenarios


def _run_scenarios(  # noqa: C901
    scenarios: Scenarios,
    command_args: CommandArgs,
    default_config: config.Config | None,
) -> None:
    """Loop through Scenarios object and execute each.

    Args:
        scenarios: The Scenarios object holding all of the Scenario objects.
        command_args: dict of command arguments.
        default_config: Molecule Config object for the default scenario.

    Raises:
        ScenarioFailureError: when a scenario fails prematurely.
    """
    num_workers = command_args.get("workers", 1)
    if num_workers > 1:
        from molecule.worker import run_scenarios_parallel, validate_worker_args  # noqa: PLC0415

        validate_worker_args(command_args)
        run_scenarios_parallel(scenarios, command_args, default_config, num_workers)
        return

    # Run initial create
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
            _log(
                scenario.config.scenario.name,
                "prerun",
                f"Performing prerun with role_name_check={role_name_check}...",
            )
            scenario.config.runtime.prepare_environment(
                install_local=True,
                role_name_check=role_name_check,
            )

        if command_args.get("subcommand") == "reset":
            _log(
                scenario.config.scenario.name,
                "reset",
                f"Removing {scenario.ephemeral_directory}",
            )
            shutil.rmtree(scenario.ephemeral_directory)
            continue
        try:
            execute_scenario(scenario, shared_state=scenarios.shared_state)
            scenarios.results.append(scenario.results)
        except ScenarioFailureError:
            # if the command has a 'destroy' arg, like test does,
            # handle that behavior here.
            if command_args.get("destroy") == "always":
                msg = (
                    f"An error occurred during the {scenario.config.subcommand} sequence action: "
                    f"'{scenario.config.action}'. Cleaning up."
                )
                step_name = getattr(scenario.config, "action", "cleanup")
                _log(
                    scenario.config.scenario.name,
                    step_name,
                    msg,
                    level="warning",
                )
                execute_subcommand(scenario.config, "cleanup")
                destroy_results = execute_subcommand_default(
                    default_config,
                    "destroy",
                    shared_state=scenarios.shared_state,
                )
                if destroy_results is not None:
                    scenarios.results.append(scenario.results)
                    scenarios.results.append(destroy_results)
                else:
                    execute_subcommand(scenario.config, "destroy")
                    scenarios.results.append(scenario.results)

                # always prune ephemeral dir if destroying on failure
                scenario.prune()
                if scenario.config.is_parallel:
                    scenario._remove_scenario_state_directory()  # noqa: SLF001
            raise

    # Run final destroy if any scenario needed shared state
    destroy_results = execute_subcommand_default(
        default_config,
        "destroy",
        shared_state=scenarios.shared_state,
    )
    if destroy_results is not None:
        scenarios.results.append(destroy_results)


def execute_subcommand_default(
    default_config: config.Config | None,
    subcommand: str,
    *,
    shared_state: bool,
) -> ScenarioResults | None:
    """Execute subcommand as in execute_subcommand, but do it from the default scenario if one exists.

    Args:
        default_config: The Config object for the default scenario, if it exists.
        subcommand: The desired subcommand to run.
        shared_state: Whether any scenario requires shared state infrastructure.

    Returns:
        The result of the subcommand.
    """
    if default_config is None or not shared_state:
        # We have not been asked to do anything.
        return None

    default = default_config.scenario
    if subcommand in default.sequence:
        execute_subcommand(default_config, subcommand)
        results = copy.deepcopy(default.results)
        # clear results for later reuse
        default.results = ScenarioResults(name=default.name, actions=[])
        return results
    _log(
        default.name,
        subcommand,
        f"{subcommand} not found in default scenario, falling back to current scenario",
        level="warning",
    )
    return None


def execute_subcommand(
    current_config: config.Config,
    subcommand_and_args: str,
) -> Any:  # noqa: ANN401
    """Execute subcommand.

    Args:
        current_config: An instance of a Molecule config.
        subcommand_and_args: A string representing the subcommand and arguments.

    Returns:
        The result of the subcommand.
    """
    (subcommand, *args) = subcommand_and_args.split(" ")
    command_module = importlib.import_module(f"molecule.command.{subcommand}")
    command = getattr(command_module, text.camelize(subcommand))

    # knowledge of the current action is used by some provisioners
    # to ensure they behave correctly during certain sequence steps,
    # particularly the setting of ansible options in create/destroy,
    # and is also used for reporting in execute_cmdline_scenarios
    current_config.action = subcommand
    return command(current_config).execute(args)


def execute_scenario(scenario: Scenario, *, shared_state: bool = False) -> None:
    """Execute each command in the given scenario's configured sequence.

    Args:
        scenario: The scenario to execute.
        shared_state: Whether global shared state execution is active for this run.
    """
    for action in scenario.sequence:
        if shared_state and action in ("create", "destroy"):
            # Ignore
            continue

        execute_subcommand(scenario.config, action)

    if (
        not shared_state
        and "destroy" in scenario.sequence
        and scenario.config.command_args.get("destroy") != "never"
    ):
        scenario.prune()

        if scenario.config.is_parallel:
            scenario._remove_scenario_state_directory()  # noqa: SLF001


def filter_ignored_scenarios(scenario_paths: list[str]) -> list[str]:
    """Filter out candidate scenario paths that are ignored by git.

    Args:
        scenario_paths: List of candidate scenario paths.

    Returns:
        Filtered list of scenario paths.
    """
    command = ["git", "check-ignore", *scenario_paths]

    with contextlib.suppress(subprocess.CalledProcessError, FileNotFoundError):
        proc = subprocess.run(
            args=command,
            capture_output=True,
            check=True,
            text=True,
            shell=False,
        )

    try:
        ignored = proc.stdout.splitlines()
        paths = [candidate for candidate in scenario_paths if str(candidate) not in ignored]
    except NameError:
        paths = scenario_paths

    return paths


def get_configs(
    args: MoleculeArgs,
    command_args: CommandArgs,
    ansible_args: tuple[str, ...] = (),
    glob_str: str | None = None,
) -> list[config.Config]:
    """Glob the current directory for Molecule config files.

    Instantiate config objects, and returns a list.

    Args:
        args: A dict of options, arguments and commands from the CLI.
        command_args: A dict of options passed to the subcommand from the CLI.
        ansible_args: An optional tuple of arguments provided to the `ansible-playbook` command.
        glob_str: A string representing the glob used to find Molecule config files.
                 If None, uses util.get_effective_molecule_glob().

    Returns:
        A list of Config objects.
    """
    if glob_str is None:
        glob_str = util.get_effective_molecule_glob()

    scenario_paths = glob.glob(
        glob_str,
        flags=wcmatch.pathlib.GLOBSTAR | wcmatch.pathlib.BRACE | wcmatch.pathlib.DOTGLOB,
    )

    scenario_paths = filter_ignored_scenarios(scenario_paths)
    configs = [
        config.Config(
            molecule_file=util.abs_path(c),
            args=args,
            command_args=command_args,
            ansible_args=ansible_args,
        )
        for c in scenario_paths
    ]
    _verify_configs(configs, glob_str)

    return configs


def _verify_configs(configs: list[config.Config], glob_str: str | None = None) -> None:
    """Verify a Molecule config was found and returns None.

    Args:
        configs: A list containing absolute paths to Molecule config files.
        glob_str: A string representing the glob used to find Molecule config files.
                 If None, uses util.get_effective_molecule_glob().

    Raises:
        ScenarioFailureError: When scenario configs cannot be verified.
    """
    if glob_str is None:
        glob_str = util.get_effective_molecule_glob()

    if configs:
        scenario_names = [c.scenario.name for c in configs]
        for scenario_name, n in collections.Counter(scenario_names).items():
            if n > 1:
                msg = f"Duplicate scenario name '{scenario_name}' found.  Exiting."
                raise ScenarioFailureError(message=msg)

    else:
        msg = f"'{glob_str}' glob failed.  Exiting."
        raise ScenarioFailureError(message=msg)


def _get_subcommand(string: str) -> str:
    """Return the subcommand from a string.

    Args:
        string: A string containing a subcommand.

    Returns:
        A string representing the subcommand.
    """
    return string.rsplit(".", maxsplit=1)[-1]

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
import importlib
import logging
import shutil
import subprocess

from typing import TYPE_CHECKING, Any

import wcmatch.pathlib
import wcmatch.wcmatch

from wcmatch import glob

from molecule import config, logger, text, util
from molecule.console import console
from molecule.constants import MOLECULE_DEFAULT_SCENARIO_NAME, MOLECULE_GLOB
from molecule.exceptions import MoleculeError, ScenarioFailureError
from molecule.scenarios import Scenarios
from molecule.util import safe_dump


if TYPE_CHECKING:
    from molecule.scenario import Scenario
    from molecule.types import CommandArgs, MoleculeArgs, ScenariosResults


class Base(abc.ABC):
    """An abstract base class used to define the command interface."""

    def __init__(self, c: config.Config) -> None:
        """Initialize code for all command classes.

        Args:
            c: An instance of a Molecule config.
        """
        self._config = c
        self._setup()

    def __init_subclass__(cls) -> None:
        """Decorate execute from all subclasses."""
        super().__init_subclass__()
        for wrapper in logger.get_section_loggers():
            cls.execute = wrapper(cls.execute)  # type: ignore[method-assign,assignment]

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

    configs: list[config.Config] = []
    if scenario_names is None:
        configs = [
            config
            for config in get_configs(args, command_args, ansible_args, MOLECULE_GLOB)
            if config.scenario.name not in excludes
        ]
    else:
        try:
            # filter out excludes
            scenario_names = [name for name in scenario_names if name not in excludes]
            for scenario_name in scenario_names:
                glob_str = MOLECULE_GLOB.replace("*", scenario_name)
                configs.extend(get_configs(args, command_args, ansible_args, glob_str))
        except ScenarioFailureError as exc:
            util.sysexit(code=exc.code)

    default_glob = MOLECULE_GLOB.replace("*", MOLECULE_DEFAULT_SCENARIO_NAME)
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
        util.sysexit(code=exc.code)
    finally:
        if command_args.get("report"):
            console.print(generate_report(scenarios.results))


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
                scenario_log = logger.get_scenario_logger(__name__, scenario_name)
                scenario_log.info(
                    "scenario test matrix: %s",
                    ", ".join(scenarios.sequence(scenario_name)),
                )

    return scenarios


def _run_scenarios(
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
    # Run initial create
    create_results = execute_subcommand_default(default_config, "create")
    if create_results is not None:
        scenarios.results.append(create_results)

    for scenario in scenarios.all:
        if scenario.config.config["prerun"]:
            role_name_check = scenario.config.config["role_name_check"]
            scenario_log = logger.get_scenario_logger(__name__, scenario.config.scenario.name)
            scenario_log.info("Performing prerun with role_name_check=%s...", role_name_check)
            scenario.config.runtime.prepare_environment(
                install_local=True,
                role_name_check=role_name_check,
            )

        if command_args.get("subcommand") == "reset":
            scenario_log = logger.get_scenario_logger(__name__, scenario.config.scenario.name)
            scenario_log.info("Removing %s", scenario.ephemeral_directory)
            shutil.rmtree(scenario.ephemeral_directory)
            return
        try:
            execute_scenario(scenario)
            scenarios.results.append({"name": scenario.name, "results": scenario.results})
        except ScenarioFailureError:
            # if the command has a 'destroy' arg, like test does,
            # handle that behavior here.
            if command_args.get("destroy") == "always":
                msg = (
                    f"An error occurred during the {scenario.config.subcommand} sequence action: "
                    f"'{scenario.config.action}'. Cleaning up."
                )
                scenario_log = logger.get_scenario_logger(__name__, scenario.config.scenario.name)
                scenario_log.warning(msg)
                execute_subcommand(scenario.config, "cleanup")
                destroy_results = execute_subcommand_default(default_config, "destroy")
                if destroy_results is not None:
                    scenarios.results.append({"name": scenario.name, "results": scenario.results})
                    scenarios.results.append(destroy_results)
                else:
                    execute_subcommand(scenario.config, "destroy")
                    scenarios.results.append({"name": scenario.name, "results": scenario.results})

                # always prune ephemeral dir if destroying on failure
                scenario.prune()
                if scenario.config.is_parallel:
                    scenario._remove_scenario_state_directory()  # noqa: SLF001
            raise

    # Run final destroy
    destroy_results = execute_subcommand_default(default_config, "destroy")
    if destroy_results is not None:
        scenarios.results.append(destroy_results)


def execute_subcommand_default(
    default_config: config.Config | None,
    subcommand: str,
) -> ScenariosResults | None:
    """Execute subcommand as in execute_subcommand, but do it from the default scenario if one exists.

    Args:
        default_config: The Config object for the default scenario, if it exists.
        subcommand: The desired subcommand to run.

    Returns:
        The result of the subcommand.
    """
    if default_config is None or default_config.shared_data is not True:
        # We have not been asked to do anything.
        return None

    default = default_config.scenario
    if subcommand in default.sequence:
        execute_subcommand(default_config, subcommand)
        results: ScenariosResults = {"name": default.name, "results": copy.copy(default.results)}
        # clear results for later reuse
        default.results = []
        return results
    # Use the default scenario name for this warning since it's about the default scenario
    scenario_log = logger.get_scenario_logger(__name__, default.name)
    scenario_log.warning(
        "%s not found in default scenario, falling back to current scenario",
        subcommand,
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


def execute_scenario(scenario: Scenario) -> None:
    """Execute each command in the given scenario's configured sequence.

    Args:
        scenario: The scenario to execute.
    """
    shared_data = scenario.config.shared_data is True
    for action in scenario.sequence:
        if shared_data and action in ("create", "destroy"):
            # Ignore
            continue

        execute_subcommand(scenario.config, action)

    if (
        not shared_data
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
    glob_str: str = MOLECULE_GLOB,
) -> list[config.Config]:
    """Glob the current directory for Molecule config files.

    Instantiate config objects, and returns a list.

    Args:
        args: A dict of options, arguments and commands from the CLI.
        command_args: A dict of options passed to the subcommand from the CLI.
        ansible_args: An optional tuple of arguments provided to the `ansible-playbook` command.
        glob_str: A string representing the glob used to find Molecule config files.

    Returns:
        A list of Config objects.
    """
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


def _verify_configs(configs: list[config.Config], glob_str: str = MOLECULE_GLOB) -> None:
    """Verify a Molecule config was found and returns None.

    Args:
        configs: A list containing absolute paths to Molecule config files.
        glob_str: A string representing the glob used to find Molecule config files.

    Raises:
        ScenarioFailureError: When scenario configs cannot be verified.
    """
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
    return string.split(".")[-1]


def generate_report(results: list[ScenariosResults]) -> str:
    """Print end-of-run report.

    Args:
        results: Dictionary containing results from each scenario.

    Returns:
        The formatted end-of-run report.
    """
    return safe_dump(results)

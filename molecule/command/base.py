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

import abc
import collections
import glob
import os
import shutil
from typing import Any, Callable

import click
from click_help_colors import HelpColorsCommand, HelpColorsGroup

import molecule.command
import molecule.scenarios
from molecule import config, logger, util

LOG = logger.get_logger(__name__)
MOLECULE_GLOB = os.environ.get("MOLECULE_GLOB", "molecule/*/molecule.yml")
MOLECULE_DEFAULT_SCENARIO_NAME = "default"


class Base(object, metaclass=abc.ABCMeta):
    """An abstract base class used to define the command interface."""

    def __init__(self, c):
        """
        Initialize code for all command classes.

        :param c: An instance of a Molecule config.
        :returns: None
        """
        self._config = c
        self._setup()

    @abc.abstractmethod
    def execute(self):  # pragma: no cover
        pass

    def print_info(self):
        msg = "Scenario: '{}'".format(self._config.scenario.name)
        LOG.info(msg)
        msg = "Action: '{}'".format(util.underscore(self.__class__.__name__))
        LOG.info(msg)

    def _setup(self):
        """
        Prepare Molecule's provisioner and returns None.

        :return: None
        """
        self._config.write()
        self._config.provisioner.write_config()
        self._config.provisioner.manage_inventory()


def execute_cmdline_scenarios(scenario_name, args, command_args, ansible_args=()):
    """
    Execute scenario sequences based on parsed command-line arguments.

    This is useful for subcommands that run scenario sequences, which
    excludes subcommands such as ``list``, ``login``, and ``matrix``.

    ``args`` and ``command_args`` are combined using :func:`get_configs`
    to generate the scenario(s) configuration.

    :param scenario_name: Name of scenario to run, or ``None`` to run all.
    :param args: ``args`` dict from ``click`` command context
    :param command_args: dict of command arguments, including the target
                         subcommand to execute
    :returns: None

    """
    glob_str = MOLECULE_GLOB
    if scenario_name:
        glob_str = glob_str.replace("*", scenario_name)
    scenarios = molecule.scenarios.Scenarios(
        get_configs(args, command_args, ansible_args, glob_str), scenario_name
    )
    scenarios.print_matrix()
    for scenario in scenarios:
        if command_args.get("subcommand") == "reset":
            LOG.info("Removing %s" % scenario.ephemeral_directory)
            shutil.rmtree(scenario.ephemeral_directory)
            return
        try:
            execute_scenario(scenario)
        except SystemExit:
            # if the command has a 'destroy' arg, like test does,
            # handle that behavior here.
            if command_args.get("destroy") == "always":
                msg = (
                    "An error occurred during the {} sequence action: "
                    "'{}'. Cleaning up."
                ).format(scenario.config.subcommand, scenario.config.action)
                LOG.warning(msg)
                execute_subcommand(scenario.config, "cleanup")
                execute_subcommand(scenario.config, "destroy")
                # always prune ephemeral dir if destroying on failure
                scenario.prune()
                if scenario.config.is_parallel:
                    scenario._remove_scenario_state_directory()
                util.sysexit()
            else:
                raise


def execute_subcommand(config, subcommand):
    """Execute subcommand."""
    command_module = getattr(molecule.command, subcommand)
    command = getattr(command_module, util.camelize(subcommand))
    # knowledge of the current action is used by some provisioners
    # to ensure they behave correctly during certain sequence steps,
    # particulary the setting of ansible options in create/destroy,
    # and is also used for reporting in execute_cmdline_scenarios
    config.action = subcommand

    return command(config).execute()


def execute_scenario(scenario):
    """
    Execute each command in the given scenario's configured sequence.

    :param scenario: The scenario to execute.
    :returns: None
    """
    for action in scenario.sequence:
        execute_subcommand(scenario.config, action)

    if (
        "destroy" in scenario.sequence
        and scenario.config.command_args.get("destroy") != "never"
    ):
        scenario.prune()

        if scenario.config.is_parallel:
            scenario._remove_scenario_state_directory()


def get_configs(args, command_args, ansible_args=(), glob_str=MOLECULE_GLOB):
    """
    Glob the current directory for Molecule config files, instantiate config \
    objects, and returns a list.

    :param args: A dict of options, arguments and commands from the CLI.
    :param command_args: A dict of options passed to the subcommand from
     the CLI.
    :param ansible_args: An optional tuple of arguments provided to the
     `ansible-playbook` command.
    :return: list
    """
    configs = [
        config.Config(
            molecule_file=util.abs_path(c),
            args=args,
            command_args=command_args,
            ansible_args=ansible_args,
        )
        for c in glob.glob(glob_str)
    ]
    _verify_configs(configs, glob_str)

    return configs


def _verify_configs(configs, glob_str=MOLECULE_GLOB):
    """
    Verify a Molecule config was found and returns None.

    :param configs: A list containing absolute paths to Molecule config files.
    :return: None
    """
    if configs:
        scenario_names = [c.scenario.name for c in configs]
        for scenario_name, n in collections.Counter(scenario_names).items():
            if n > 1:
                msg = ("Duplicate scenario name '{}' found.  " "Exiting.").format(
                    scenario_name
                )
                util.sysexit_with_message(msg)

    else:
        msg = "'{}' glob failed.  Exiting.".format(glob_str)
        util.sysexit_with_message(msg)


def _get_subcommand(string):
    return string.split(".")[-1]


def click_group_ex():
    """Return extended version of click.group()."""
    # Color coding used to group command types, documented only here as we may
    # decide to change them later.
    # green : (default) as sequence step
    # blue : molecule own command, not dependent on scenario
    # yellow : special commands, like full test sequence, or login
    return click.group(
        cls=HelpColorsGroup,
        # Workaround to disable click help line truncation to ~80 chars
        # https://github.com/pallets/click/issues/486
        context_settings=dict(max_content_width=9999),
        help_headers_color="yellow",
        help_options_color="green",
        help_options_custom_colors={
            "drivers": "blue",
            "init": "blue",
            "list": "blue",
            "matrix": "blue",
            "login": "bright_yellow",
            "reset": "blue",
            "test": "bright_yellow",
        },
    )


def click_command_ex() -> Callable[[Callable[..., Any]], click.Command]:
    """Return extended version of click.command()."""
    return click.command(  # type: ignore
        cls=HelpColorsCommand, help_headers_color="yellow", help_options_color="green"
    )

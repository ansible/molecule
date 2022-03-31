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
"""Check Command Module."""

import logging
import os

import click

from molecule import util
from molecule.command import base

LOG = logging.getLogger(__name__)
MOLECULE_PARALLEL = os.environ.get("MOLECULE_PARALLEL", False)


class Check(base.Base):
    """
    Check Command Class.

    .. program:: molecule check

    .. option:: molecule check

        Target the default scenario.

    .. program:: molecule check --scenario-name foo

    .. option:: molecule check --scenario-name foo

        Targeting a specific scenario.

    .. program:: molecule --debug check

    .. option:: molecule --debug check

        Executing with `debug`.

    .. program:: molecule --base-config base.yml check

    .. option:: molecule --base-config base.yml check

        Executing with a `base-config`.

    .. program:: molecule --env-file foo.yml check

    .. option:: molecule --env-file foo.yml check

        Load an env file to read variables from when rendering
        molecule.yml.

    .. program:: molecule check --parallel

    .. option:: molecule check --parallel

       Run in parallelizable mode.
    """

    def execute(self, action_args=None):
        """
        Execute the actions necessary to perform a `molecule check` and \
        returns None.

        :return: None
        """
        self._config.provisioner.check()


@base.click_command_ex()
@click.pass_context
@click.option(
    "--scenario-name",
    "-s",
    default=base.MOLECULE_DEFAULT_SCENARIO_NAME,
    help=f"Name of the scenario to target. ({base.MOLECULE_DEFAULT_SCENARIO_NAME})",
)
@click.option(
    "--parallel/--no-parallel",
    default=MOLECULE_PARALLEL,
    help="Enable or disable parallel mode. Default is disabled.",
)
def check(ctx, scenario_name, parallel):  # pragma: no cover
    """Use the provisioner to perform a Dry-Run (destroy, dependency, create, \
    prepare, converge)."""
    args = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)
    command_args = {"parallel": parallel, "subcommand": subcommand}

    if parallel:
        util.validate_parallel_cmd_args(command_args)

    base.execute_cmdline_scenarios(scenario_name, args, command_args)

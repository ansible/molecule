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
"""Syntax Command Module."""

import click

from molecule import logger
from molecule.command import base

LOG = logger.get_logger(__name__)


class Syntax(base.Base):
    """
    Syntax Command Class.

    .. program:: molecule syntax

    .. option:: molecule syntax

        Target the default scenario.

    .. program:: molecule syntax --scenario-name foo

    .. option:: molecule syntax --scenario-name foo

        Targeting a specific scenario.

    .. program:: molecule --debug syntax

    .. option:: molecule --debug syntax

        Executing with `debug`.

    .. program:: molecule --base-config base.yml syntax

    .. option:: molecule --base-config base.yml syntax

        Executing with a `base-config`.

    .. program:: molecule --env-file foo.yml syntax

    .. option:: molecule --env-file foo.yml syntax

        Load an env file to read variables from when rendering
        molecule.yml.
    """

    def execute(self):
        """Execute the actions necessary to perform a `molecule syntax` and \
        returns None.

        :return: None
        """
        self.print_info()
        self._config.provisioner.syntax()


@base.click_command_ex()
@click.pass_context
@click.option(
    "--scenario-name",
    "-s",
    default=base.MOLECULE_DEFAULT_SCENARIO_NAME,
    help="Name of the scenario to target. ({})".format(
        base.MOLECULE_DEFAULT_SCENARIO_NAME
    ),
)
def syntax(ctx, scenario_name):  # pragma: no cover
    """Use the provisioner to syntax check the role."""
    args = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)
    command_args = {"subcommand": subcommand}

    base.execute_cmdline_scenarios(scenario_name, args, command_args)

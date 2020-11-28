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
"""Dependency Command Module."""

import logging

import click

from molecule.command import base

LOG = logging.getLogger(__name__)


class Dependency(base.Base):
    """
    Dependency Command Class.

    .. program:: molecule dependency

    .. option:: molecule dependency

        Target the default scenario.

    .. program:: molecule dependency --scenario-name foo

    .. option:: molecule dependency --scenario-name foo

        Targeting a specific scenario.

    .. program:: molecule --debug dependency

    .. option:: molecule --debug dependency

        Executing with `debug`.

    .. program:: molecule --base-config base.yml dependency

    .. option:: molecule --base-config base.yml dependency

        Executing with a `base-config`.

    .. program:: molecule --env-file foo.yml dependency

    .. option:: molecule --env-file foo.yml dependency

        Load an env file to read variables from when rendering
        molecule.yml.
    """

    def execute(self):
        """
        Execute the actions necessary to perform a `molecule dependency` and \
        returns None.

        :return: None
        """
        self._config.dependency.execute()


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
def dependency(ctx, scenario_name):  # pragma: no cover
    """Manage the role's dependencies."""
    args = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)
    command_args = {"subcommand": subcommand}

    base.execute_cmdline_scenarios(scenario_name, args, command_args)

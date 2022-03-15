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
"""Converge Command Module."""

import logging

import click

from molecule.command import base

LOG = logging.getLogger(__name__)


class Converge(base.Base):
    """
    Converge Command Class.

    .. program:: molecule converge

    .. option:: molecule converge

        Target the default scenario.

    .. program:: molecule converge --scenario-name foo

    .. option:: molecule converge --scenario-name foo

        Targeting a specific scenario.

    .. program:: molecule converge -- -vvv --tags foo,bar

    .. option:: molecule converge -- -vvv --tags foo,bar

        Providing additional command line arguments to the `ansible-playbook`
        command.  Use this option with care, as there is no sanitation or
        validation of input.  Options passed on the CLI override options
        provided in provisioner's `options` section of `molecule.yml`.

    .. program:: molecule --debug converge

    .. option:: molecule --debug converge

        Executing with `debug`.

    .. program:: molecule --base-config base.yml converge

    .. option:: molecule --base-config base.yml converge

        Executing with a `base-config`.

    .. program:: molecule --env-file foo.yml converge

    .. option:: molecule --env-file foo.yml converge

        Load an env file to read variables from when rendering
        molecule.yml.
    """

    def execute(self, action_args=None):
        """
        Execute the actions necessary to perform a `molecule converge` and \
        returns None.

        :return: None
        """
        self._config.provisioner.converge()
        self._config.state.change_state("converged", True)


@base.click_command_ex()
@click.pass_context
@click.option(
    "--scenario-name",
    "-s",
    default=base.MOLECULE_DEFAULT_SCENARIO_NAME,
    help=f"Name of the scenario to target. ({base.MOLECULE_DEFAULT_SCENARIO_NAME})",
)
@click.argument("ansible_args", nargs=-1, type=click.UNPROCESSED)
def converge(ctx, scenario_name, ansible_args):  # pragma: no cover
    """Use the provisioner to configure instances (dependency, create, prepare converge)."""
    args = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)
    command_args = {"subcommand": subcommand}

    base.execute_cmdline_scenarios(scenario_name, args, command_args, ansible_args)

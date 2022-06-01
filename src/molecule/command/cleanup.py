#  Copyright (c) 2019 Red Hat, Inc.
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
"""Cleanup Command Module."""

import logging

import click

from molecule.command import base

LOG = logging.getLogger(__name__)


class Cleanup(base.Base):
    """
    Cleanup Command Class.

    This action has cleanup and is not enabled by default.
    See the provisioner's documentation for further details.

    .. program:: molecule cleanup

    .. option:: molecule cleanup

        Target the default scenario.

    .. program:: molecule cleanup --scenario-name foo

    .. option:: molecule cleanup --scenario-name foo

        Targeting a specific scenario.

    .. program:: molecule --debug cleanup

    .. option:: molecule --debug cleanup

        Executing with `debug`.

    .. program:: molecule --base-config base.yml cleanup

    .. option:: molecule --base-config base.yml cleanup

        Executing with a `base-config`.

    .. program:: molecule --env-file foo.yml cleanup

    .. option:: molecule --env-file foo.yml cleanup

        Load an env file to read variables when rendering
        molecule.yml.
    """

    def execute(self, action_args=None):
        """
        Execute the actions necessary to cleanup the instances and returns \
        None.

        :return: None
        """
        if not self._config.provisioner.playbooks.cleanup:
            msg = "Skipping, cleanup playbook not configured."
            LOG.warning(msg)
            return

        self._config.provisioner.cleanup()


@base.click_command_ex()
@click.pass_context
@click.option(
    "--scenario-name",
    "-s",
    default=base.MOLECULE_DEFAULT_SCENARIO_NAME,
    help=f"Name of the scenario to target. ({base.MOLECULE_DEFAULT_SCENARIO_NAME})",
)
def cleanup(ctx, scenario_name):  # pragma: no cover
    """Use the provisioner to cleanup any changes made to external systems during \
    the stages of testing."""
    args = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)
    command_args = {"subcommand": subcommand}

    base.execute_cmdline_scenarios(scenario_name, args, command_args)

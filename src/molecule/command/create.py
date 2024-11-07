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
"""Create Command Module."""
from __future__ import annotations

import logging

from typing import TYPE_CHECKING

import click

from molecule.api import drivers
from molecule.command import base
from molecule.config import DEFAULT_DRIVER


if TYPE_CHECKING:
    from molecule.types import CommandArgs, MoleculeArgs


LOG = logging.getLogger(__name__)


class Create(base.Base):
    """Create Command Class."""

    def execute(self, action_args: list[str] | None = None) -> None:  # noqa: ARG002
        """Execute the actions necessary to perform a `molecule create`.

        Args:
            action_args: Arguments for this command. Unused.
        """
        self._config.state.change_state("driver", self._config.driver.name)

        if self._config.state.created:
            msg = "Skipping, instances already created."
            LOG.warning(msg)
            return

        if self._config.provisioner:
            self._config.provisioner.create()

        self._config.state.change_state("created", value=True)


@base.click_command_ex()
@click.pass_context
@click.option(
    "--scenario-name",
    "-s",
    default=base.MOLECULE_DEFAULT_SCENARIO_NAME,
    help=f"Name of the scenario to target. ({base.MOLECULE_DEFAULT_SCENARIO_NAME})",
)
@click.option(
    "--driver-name",
    "-d",
    type=click.Choice([str(s) for s in drivers()]),
    help=f"Name of driver to use. ({DEFAULT_DRIVER})",
)
def create(
    ctx: click.Context,
    scenario_name: str,
    driver_name: str,
) -> None:  # pragma: no cover
    """Use the provisioner to start the instances.

    Args:
        ctx: Click context object holding commandline arguments.
        scenario_name: Name of the scenario to target.
        driver_name: Name of the Molecule driver to use.
    """
    args: MoleculeArgs = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)  # noqa: SLF001
    command_args: CommandArgs = {"subcommand": subcommand, "driver_name": driver_name}

    base.execute_cmdline_scenarios(scenario_name, args, command_args)

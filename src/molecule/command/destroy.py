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
"""Destroy Command Module."""

from __future__ import annotations

import logging

from typing import TYPE_CHECKING

import click

from molecule import util
from molecule.api import drivers
from molecule.command import base
from molecule.config import DEFAULT_DRIVER, MOLECULE_PARALLEL


if TYPE_CHECKING:
    from molecule.types import CommandArgs, MoleculeArgs


LOG = logging.getLogger(__name__)


class Destroy(base.Base):
    """Destroy Command Class."""

    def execute(self, action_args: list[str] | None = None) -> None:  # noqa: ARG002
        """Execute the actions necessary to perform a `molecule destroy`.

        Args:
            action_args: Arguments for this command. Unused.
        """
        if self._config.command_args.get("destroy") == "never":
            msg = "Skipping, '--destroy=never' requested."
            LOG.warning(msg)
            return

        if self._config.provisioner:
            self._config.provisioner.destroy()
        self._config.state.reset()


@base.click_command_ex()
@click.pass_context
@base.click_command_options
@click.option(
    "--driver-name",
    "-d",
    type=click.Choice([str(s) for s in drivers()]),
    help=f"Name of driver to use. ({DEFAULT_DRIVER})",
)
@click.option(
    "--parallel/--no-parallel",
    default=MOLECULE_PARALLEL,
    help="Enable or disable parallel mode. Default is disabled.",
)
def destroy(  # noqa: PLR0913
    ctx: click.Context,
    /,
    scenario_name: list[str] | None,
    exclude: list[str],
    driver_name: str,
    __all: bool,  # noqa: FBT001
    *,
    parallel: bool,
    report: bool,
    shared_inventory: bool,
) -> None:  # pragma: no cover
    """Use the provisioner to destroy the instances.

    \f
    Args:
        ctx: Click context object holding commandline arguments.
        scenario_name: Name of the scenario to target.
        exclude: Name of the scenarios to avoid targeting.
        driver_name: Molecule driver to use.
        __all: Whether molecule should target scenario_name or all scenarios.
        parallel: Whether the scenario(s) should be run in parallel mode.
        report: Whether to show an after-run summary report.
        shared_inventory: Whether the inventory should be shared between scenarios.
    """  # noqa: D301
    args: MoleculeArgs = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)  # noqa: SLF001
    command_args: CommandArgs = {
        "parallel": parallel,
        "subcommand": subcommand,
        "driver_name": driver_name,
        "report": report,
        "shared_inventory": shared_inventory,
    }

    if __all:
        scenario_name = None

    if parallel:
        util.validate_parallel_cmd_args(command_args)

    base.execute_cmdline_scenarios(scenario_name, args, command_args, excludes=exclude)

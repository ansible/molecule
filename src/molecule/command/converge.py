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

from __future__ import annotations

import logging

from typing import TYPE_CHECKING

import click

from molecule.command import base


if TYPE_CHECKING:
    from molecule.types import CommandArgs, MoleculeArgs


LOG = logging.getLogger(__name__)


class Converge(base.Base):
    """Converge Command Class."""

    def execute(self, action_args: list[str] | None = None) -> None:  # noqa: ARG002
        """Execute the actions necessary to perform a `molecule converge`.

        Args:
            action_args: Arguments for this command. Unused.
        """
        if self._config.provisioner:
            self._config.provisioner.converge()
        self._config.state.change_state("converged", value=True)


@base.click_command_ex()
@click.pass_context
@base.click_command_options
@click.argument("ansible_args", nargs=-1, type=click.UNPROCESSED)
def converge(  # noqa: PLR0913
    ctx: click.Context,
    /,
    scenario_name: list[str] | None,
    exclude: list[str],
    __all: bool,  # noqa: FBT001
    *,
    ansible_args: tuple[str],
    report: bool,
    shared_inventory: bool,
) -> None:  # pragma: no cover
    """Use the provisioner to configure instances (dependency, create, prepare converge).

    \f
    Args:
        ctx: Click context object holding commandline arguments.
        scenario_name: Name of the scenario to target.
        exclude: Name of the scenarios to avoid targeting.
        __all: Whether molecule should target scenario_name or all scenarios.
        ansible_args: Arguments to forward to Ansible.
        report: Whether to show an after-run summary report.
        shared_inventory: Whether the inventory should be shared between scenarios.
    """  # noqa: D301
    args: MoleculeArgs = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)  # noqa: SLF001
    command_args: CommandArgs = {
        "subcommand": subcommand,
        "report": report,
        "shared_inventory": shared_inventory,
    }

    if __all:
        scenario_name = None

    base.execute_cmdline_scenarios(scenario_name, args, command_args, ansible_args, exclude)

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
"""Verify Command Module."""
from __future__ import annotations

import logging

from typing import TYPE_CHECKING

import click

from molecule.command import base


if TYPE_CHECKING:
    from molecule.types import CommandArgs, MoleculeArgs


LOG = logging.getLogger(__name__)


class Verify(base.Base):
    """Verify Command Class."""

    def execute(self, action_args: list[str] | None = None) -> None:
        """Execute the actions necessary to perform a `molecule verify`.

        Args:
            action_args: Arguments for this command.
        """
        self._config.verifier.execute(action_args)


@base.click_command_ex()
@click.pass_context
@click.option(
    "--scenario-name",
    "-s",
    multiple=True,
    default=[base.MOLECULE_DEFAULT_SCENARIO_NAME],
    help=f"Name of the scenario to target. May be specified multiple times. ({base.MOLECULE_DEFAULT_SCENARIO_NAME})",
)
@click.option(
    "--all/--no-all",
    "__all",
    default=False,
    help="Verify all scenarios. Default is False.",
)
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    help="Name of the scenario to exclude from running. May be specified multiple times.",
)
def verify(
    ctx: click.Context,
    scenario_name: list[str] | None,
    exclude: list[str],
    __all: bool,  # noqa: FBT001
) -> None:  # pragma: no cover
    """Run automated tests against instances.

    Args:
        ctx: Click context object holding commandline arguments.
        scenario_name: Name of the scenario to target.
        exclude: Name of the scenarios to avoid targeting.
        __all: Whether molecule should target scenario_name or all scenarios.
    """
    args: MoleculeArgs = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)  # noqa: SLF001
    command_args: CommandArgs = {"subcommand": subcommand}

    if __all:
        scenario_name = None

    base.execute_cmdline_scenarios(scenario_name, args, command_args, excludes=exclude)

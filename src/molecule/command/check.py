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
from __future__ import annotations

import logging
import os

from typing import TYPE_CHECKING

import click

from molecule import util
from molecule.command import base


if TYPE_CHECKING:
    from molecule.types import CommandArgs, MoleculeArgs


LOG = logging.getLogger(__name__)
MOLECULE_PARALLEL = os.environ.get("MOLECULE_PARALLEL", False)


class Check(base.Base):
    """Check Command Class."""

    def execute(self, action_args: list[str] | None = None) -> None:  # noqa: ARG002
        """Execute the actions necessary to perform a `molecule check`.

        Args:
            action_args: Arguments for this command. Unused.
        """
        if self._config.provisioner is not None:
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
def check(  # pragma: no cover
    ctx: click.Context,
    scenario_name: str,
    *,
    parallel: bool,
) -> None:
    """Use the provisioner to perform a Dry-Run (destroy, dependency, create, prepare, converge).

    Args:
        ctx: Click context object holding commandline arguments.
        scenario_name: Name of the scenario to target.
        parallel: Whether the scenario(s) should be run in parallel.
    """
    args: MoleculeArgs = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)  # noqa: SLF001
    command_args: CommandArgs = {"parallel": parallel, "subcommand": subcommand}

    if parallel:
        util.validate_parallel_cmd_args(command_args)

    base.execute_cmdline_scenarios(scenario_name, args, command_args)

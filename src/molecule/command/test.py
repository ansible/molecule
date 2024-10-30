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
"""Test Command Module."""
from __future__ import annotations

import logging
import os

from typing import TYPE_CHECKING

import click

from molecule import util
from molecule.api import drivers
from molecule.command import base
from molecule.config import DEFAULT_DRIVER


if TYPE_CHECKING:
    from typing import Literal

    from molecule.types import CommandArgs, MoleculeArgs


LOG = logging.getLogger(__name__)
MOLECULE_PARALLEL = os.environ.get("MOLECULE_PARALLEL", False)
MOLECULE_PLATFORM_NAME = os.environ.get("MOLECULE_PLATFORM_NAME", None)


class Test(base.Base):
    """Test Command Class."""

    def execute(self, action_args: list[str] | None = None) -> None:
        """Execute the actions necessary to perform a `molecule test`.

        Args:
            action_args: Arguments for this command. Unused.
        """


@base.click_command_ex()
@click.pass_context
@click.option(
    "--scenario-name",
    "-s",
    default=base.MOLECULE_DEFAULT_SCENARIO_NAME,
    help=f"Name of the scenario to target. ({base.MOLECULE_DEFAULT_SCENARIO_NAME})",
)
@click.option(
    "--platform-name",
    "-p",
    default=MOLECULE_PLATFORM_NAME,
    help="Name of the platform to target only. Default is None",
)
@click.option(
    "--driver-name",
    "-d",
    type=click.Choice([str(s) for s in drivers()]),
    help=f"Name of driver to use. ({DEFAULT_DRIVER})",
)
@click.option(
    "--all/--no-all",
    "__all",
    default=False,
    help="Test all scenarios. Default is False.",
)
@click.option(
    "--destroy",
    type=click.Choice(["always", "never"]),
    default="always",
    help=("The destroy strategy used at the conclusion of a Molecule run (always)."),
)
@click.option(
    "--parallel/--no-parallel",
    default=MOLECULE_PARALLEL,
    help="Enable or disable parallel mode. Default is disabled.",
)
@click.argument("ansible_args", nargs=-1, type=click.UNPROCESSED)
def test(  # noqa: PLR0913
    ctx: click.Context,
    scenario_name: str | None,
    driver_name: str,
    __all: bool,  # noqa: FBT001
    destroy: Literal["always", "never"],
    parallel: bool,  # noqa: FBT001
    ansible_args: tuple[str, ...],
    platform_name: str,
) -> None:  # pragma: no cover
    """Test (dependency, cleanup, destroy, syntax, create, prepare, converge, idempotence, side_effect, verify, cleanup, destroy).

    Args:
        ctx: Click context object holding commandline arguments.
        scenario_name: Name of the scenario to target.
        driver_name: Name of the driver to use.
        __all: Whether molecule should target scenario_name or all scenarios.
        destroy: The destroy strategy to use.
        parallel: Whether the scenario(s) should be run in parallel mode.
        ansible_args: Arguments to forward to Ansible.
        platform_name: Name of the platform to use.
    """  # noqa: E501
    args: MoleculeArgs = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)  # noqa: SLF001
    command_args: CommandArgs = {
        "parallel": parallel,
        "destroy": destroy,
        "subcommand": subcommand,
        "driver_name": driver_name,
        "platform_name": platform_name,
    }

    if __all:
        scenario_name = None

    if parallel:
        util.validate_parallel_cmd_args(command_args)

    base.execute_cmdline_scenarios(scenario_name, args, command_args, ansible_args)

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
"""Matrix Command Module."""
from __future__ import annotations

import logging

from typing import TYPE_CHECKING

import click

from molecule import scenarios
from molecule.command import base


if TYPE_CHECKING:
    from molecule.types import CommandArgs, MoleculeArgs


LOG = logging.getLogger(__name__)


class Matrix(base.Base):
    """Matrix Command Class.

    .. program:: molecule matrix subcommand

    .. option:: molecule matrix subcommand

        Target the default scenario.

    .. program:: molecule matrix --scenario-name foo subcommand

    .. option:: molecule matrix --scenario-name foo subcommand

        Targeting a specific scenario.

    .. program:: molecule --debug matrix subcommand

    .. option:: molecule --debug matrix subcommand

        Executing with `debug`.

    .. program:: molecule --base-config base.yml matrix subcommand

    .. option:: molecule --base-config base.yml matrix subcommand

        Executing with a `base-config`.

    .. program:: molecule --env-file foo.yml matrix subcommand

    .. option:: molecule --env-file foo.yml matrix subcommand

        Load an env file to read variables from when rendering
        molecule.yml.
    """


@base.click_command_ex()
@click.pass_context
@click.option("--scenario-name", "-s", help="Name of the scenario to target.")
# NOTE(retr0h): Cannot introspect base.Base for `click.Choice`, since
# subclasses have not all loaded at this point.
@click.argument("subcommand", nargs=1, type=click.UNPROCESSED)
def matrix(
    ctx: click.Context,
    scenario_name: str,
    subcommand: str,
) -> None:  # pragma: no cover
    """List matrix of steps used to test instances.

    Args:
        ctx: Click context object holding commandline arguments.
        scenario_name: Name of the scenario to target.
        subcommand: Subcommand to target.
    """
    args: MoleculeArgs = ctx.obj.get("args")
    command_args: CommandArgs = {"subcommand": subcommand}

    s = scenarios.Scenarios(base.get_configs(args, command_args), scenario_name)
    s.print_matrix()

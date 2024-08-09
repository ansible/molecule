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
"""List Command Module."""
from __future__ import annotations

import logging

import click

from rich import box
from rich.syntax import Syntax
from rich.table import Table

from molecule import scenarios, text, util
from molecule.command import base
from molecule.command.base import MOLECULE_GLOB
from molecule.console import console
from molecule.status import Status


LOG = logging.getLogger(__name__)


class List(base.Base):
    """List command shows information about current scenarios."""

    def execute(self, action_args=None):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG002
        """Execute the actions necessary to perform a `molecule list` and returns None."""
        return self._config.driver.status()


@base.click_command_ex()
@click.pass_context
@click.option("--scenario-name", "-s", help="Name of the scenario to target.")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["simple", "plain", "yaml"]),
    default="simple",
    help="Change output format. (simple)",
)
def list(ctx, scenario_name, format):  # type: ignore[no-untyped-def] # pragma: no cover  # noqa: ANN001, ANN201, A001, A002
    """List status of instances."""
    args = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)  # noqa: SLF001
    command_args = {"subcommand": subcommand, "format": format}

    statuses = []
    s = scenarios.Scenarios(
        base.get_configs(args, command_args, glob_str=MOLECULE_GLOB),
        scenario_name,
    )
    for scenario in s:
        statuses.extend(base.execute_subcommand(scenario.config, subcommand))

    headers = [text.title(name) for name in Status._fields]
    if format in ["simple", "plain"]:
        table_format = format  # "simple"

        if format == "plain":
            headers = []
            table_format = format
        _print_tabulate_data(headers, statuses, table_format)  # type: ignore[no-untyped-call]
    else:
        _print_yaml_data(headers, statuses)  # type: ignore[no-untyped-call]


def _print_tabulate_data(headers, data, table_format):  # type: ignore[no-untyped-def] # pragma: no cover  # noqa: ANN001, ANN202
    """Show the tabulate data on the screen and returns None.

    Args:
        headers: A list of column headers.
        data: A list of tabular data to display.
        table_format: A string containing the table format.
    """
    if table_format == "plain":
        for line in data:
            console.print("\t".join(line))
    else:
        t = Table(box=box.MINIMAL)
        for header in headers:
            t.add_column(header)
        for line in data:
            t.add_row(*line)
        console.print(t)


def _print_yaml_data(headers, data):  # type: ignore[no-untyped-def] # pragma: no cover  # noqa: ANN001, ANN202
    l = [  # noqa: E741
        dict(zip(headers, [getattr(datum, field) for field in datum._fields], strict=False))
        for datum in data
    ]

    syntax = Syntax(util.safe_dump(l), "yaml")
    console.print(syntax)

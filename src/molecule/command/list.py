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

from __future__ import print_function

import logging

import click
from rich import box
from rich.syntax import Syntax
from rich.table import Table

from molecule import scenarios, text, util
from molecule.command import base
from molecule.console import console
from molecule.status import Status

LOG = logging.getLogger(__name__)


class List(base.Base):
    """
    List command shows information about current scenarios.

    .. program:: molecule list

    .. option:: molecule list

        Target the default scenario.

    .. program:: molecule list --scenario-name foo

    .. option:: molecule list --scenario-name foo

        Targeting a specific scenario.

    .. program:: molecule list --format plain

    .. option:: molecule list  --format plain

        Machine readable plain text output.

    .. program:: molecule list --format yaml

    .. option:: molecule list  --format yaml

        Machine readable yaml output.

    .. program:: molecule --debug list

    .. option:: molecule --debug list

        Executing with `debug`.

    .. program:: molecule --base-config base.yml list

    .. option:: molecule --base-config base.yml list

        Executing with a `base-config`.

    .. program:: molecule --env-file foo.yml list

    .. option:: molecule --env-file foo.yml list

        Load an env file to read variables from when rendering
        molecule.yml.
    """

    def execute(self):
        """
        Execute the actions necessary to perform a `molecule list` and \
        returns None.

        :return: None
        """
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
def list(ctx, scenario_name, format):  # pragma: no cover
    """List status of instances."""
    args = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)
    command_args = {"subcommand": subcommand, "format": format}

    statuses = []
    s = scenarios.Scenarios(base.get_configs(args, command_args), scenario_name)
    for scenario in s:
        statuses.extend(base.execute_subcommand(scenario.config, subcommand))

    headers = [text.title(name) for name in Status._fields]
    if format == "simple" or format == "plain":
        table_format = format  # "simple"

        if format == "plain":
            headers = []
            table_format = format
        _print_tabulate_data(headers, statuses, table_format)
    else:
        _print_yaml_data(headers, statuses)


def _print_tabulate_data(headers, data, table_format):  # pragma: no cover
    """
    Show the tabulate data on the screen and returns None.

    :param headers: A list of column headers.
    :param data:  A list of tabular data to display.
    :returns: None
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


def _print_yaml_data(headers, data):  # pragma: no cover
    l = [
        dict(zip(headers, [getattr(datum, field) for field in datum._fields]))
        for datum in data
    ]

    syntax = Syntax(util.safe_dump(l), "yaml")
    console.print(syntax)

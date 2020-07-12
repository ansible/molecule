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

from __future__ import print_function

import click
import tabulate

from molecule import api, logger
from molecule.command import base

LOG = logger.get_logger(__name__)


@base.click_command_ex()
@click.pass_context
@click.option(
    "--format",
    "-f",
    type=click.Choice(["simple", "plain"]),
    default="simple",
    help="Change output format. (simple)",
)
def drivers(ctx, format):  # pragma: no cover
    """List drivers."""
    drivers = [[x] for x in api.drivers()]

    headers = ["name"]
    table_format = "simple"
    if format == "plain":
        headers = []
        table_format = format
    _print_tabulate_data(headers, drivers, table_format)


def _print_tabulate_data(headers, data, table_format):  # pragma: no cover
    """
    Show the tabulate data on the screen and returns None.

    :param headers: A list of column headers.
    :param data:  A list of tabular data to display.
    :returns: None
    """
    print(tabulate.tabulate(data, headers, tablefmt=table_format))

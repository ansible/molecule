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

from typing import TYPE_CHECKING

from molecule import api
from molecule.click_cfg import click_command_ex, options
from molecule.console import console


if TYPE_CHECKING:
    import click


@click_command_ex()
@options(["format_simple"])
def drivers(ctx: click.Context) -> None:  # pragma: no cover
    """List drivers.

    Args:
        ctx: Click context object holding commandline arguments.
    """
    output_format = ctx.params["format"]
    drivers = []  # pylint: disable=redefined-outer-name

    for driver in api.drivers().values():
        description = str(driver)
        if output_format == "plain":
            description = f"{driver!s:16s}[logging.level.notset] {driver.title} Version {driver.version} from {driver.module} python module.)[/logging.level.notset]"
        drivers.append([driver, description])
        console.print(description)

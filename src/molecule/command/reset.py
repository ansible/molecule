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
"""Reset Command Module."""

from __future__ import annotations

import shutil

from pathlib import Path
from typing import TYPE_CHECKING

from molecule.api import drivers
from molecule.click_cfg import click_command_ex, options
from molecule.command import base
from molecule.command.base import _log


if TYPE_CHECKING:
    import click

    from molecule.types import CommandArgs


@click_command_ex()
@options(
    [
        "all_scenarios",
        "exclude",
        "report",
        "scenario_name_with_default",
        "command_borders",
    ],
)
def reset(ctx: click.Context) -> None:  # pragma: no cover
    """Reset molecule temporary folders.

    Args:
        ctx: Click context object holding commandline arguments.
    """
    args = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)  # noqa: SLF001
    command_args: CommandArgs = {
        "command_borders": ctx.params["command_borders"],
        "subcommand": subcommand,
    }

    all_flag = ctx.params["all"]
    exclude = ctx.params["exclude"]
    scenario_name = ctx.params["scenario_name"]

    if all_flag:
        scenario_name = None

    base.execute_cmdline_scenarios(scenario_name, args, command_args, excludes=exclude)

    # If --all was used, also clean shared directory after individual scenarios
    if all_flag:
        # Get configs to access shared directory
        configs = base.get_configs(args, command_args)
        if configs:
            shared_dir = configs[0].scenario.shared_ephemeral_directory
            if Path(shared_dir).exists():
                _log(
                    "shared",
                    "reset",
                    f"Removing shared directory {shared_dir}",
                )

                shutil.rmtree(shared_dir)
    for driver in drivers().values():
        driver.reset()

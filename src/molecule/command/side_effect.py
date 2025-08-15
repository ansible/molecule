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
"""Side-effect Command Module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from molecule.click_cfg import click_command_ex, common_options
from molecule.command import base
from molecule.reporting.definitions import CompletionState


if TYPE_CHECKING:
    import click

    from molecule.types import CommandArgs


class SideEffect(base.Base):
    """This action has side effects and not enabled by default.

    See the provisioners documentation for further details.
    """

    def execute(self, action_args: list[str] | None = None) -> None:
        """Execute the actions necessary to perform a `molecule side-effect`.

        Args:
            action_args: Arguments for this command.
        """
        if self._config.provisioner:
            if not self._config.provisioner.playbooks.side_effect:
                message = "Missing playbook"
                note = f"Remove from {self._config.subcommand}_sequence to suppress"
                self._config.scenario.results.add_completion(
                    CompletionState.missing(message=message, note=note),
                )
                return

            self._config.provisioner.side_effect(action_args)


@click_command_ex()
@common_options()
def side_effect(ctx: click.Context) -> None:  # pragma: no cover
    """Use the provisioner to perform side effects to the role.

    Args:
        ctx: Click context object holding commandline arguments.
    """
    args = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)  # noqa: SLF001
    command_args: CommandArgs = {
        "command_borders": ctx.params["command_borders"],
        "report": ctx.params["report"],
        "shared_state": ctx.params["shared_state"],
        "subcommand": subcommand,
    }

    __all = ctx.params["all"]
    exclude = ctx.params["exclude"]
    scenario_name = ctx.params["scenario_name"]

    if __all:
        scenario_name = None

    base.execute_cmdline_scenarios(scenario_name, args, command_args, excludes=exclude)

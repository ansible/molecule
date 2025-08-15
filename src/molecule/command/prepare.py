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
"""Prepare Command Module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from molecule.click_cfg import click_command_ex, common_options
from molecule.command import base
from molecule.reporting.definitions import CompletionState


if TYPE_CHECKING:
    import click

    from molecule.types import CommandArgs


class Prepare(base.Base):
    """This action is for the purpose of preparing a molecule managed instance.

    Done before the :py:class:`molecule.command.converge.Converge` action is run.

    Tasks contained within the ``prepare.yml`` playbook in the scenario
    directory will be run remotely on the managed instance. This action is run
    only once per test sequence.

    .. program:: molecule prepare

    .. option:: molecule prepare

        Target the default scenario.

    .. program:: molecule prepare --scenario-name foo

    .. option:: molecule prepare --scenario-name foo

        Targeting a specific scenario.

    .. program:: molecule prepare --driver-name foo

    .. option:: molecule prepare --driver-name foo

        Targeting a specific driver.

    .. program:: molecule prepare --force

    .. option:: molecule prepare --force

        Force the execution for the prepare playbook.

    .. program:: molecule --debug prepare

    .. option:: molecule --debug prepare

        Executing with `debug`.

    .. program:: molecule --base-config base.yml prepare

    .. option:: molecule --base-config base.yml prepare

        Executing with a `base-config`.

    .. program:: molecule --env-file foo.yml prepare

    .. option:: molecule --env-file foo.yml prepare

        Load an env file to read variables from when rendering
        molecule.yml.
    """

    def execute(self, action_args: list[str] | None = None) -> None:  # noqa: ARG002
        """Execute the actions necessary to prepare the instances.

        Args:
            action_args: Arguments for this command. Unused.
        """
        if self._config.state.prepared and not self._config.command_args.get("force"):
            msg = "Skipping, instances already prepared."
            self._log.warning(msg)
            return

        if self._config.provisioner:
            if not self._config.provisioner.playbooks.prepare:
                message = "Missing playbook"
                note = f"Remove from {self._config.subcommand}_sequence to suppress"
                self._config.scenario.results.add_completion(
                    CompletionState.missing(message=message, note=note),
                )
                return

            self._config.provisioner.prepare()
            self._config.state.change_state("prepared", value=True)


@click_command_ex()
@common_options("force", "driver_name_with_choices", "format_simple")
def prepare(ctx: click.Context) -> None:  # pragma: no cover
    """Use the provisioner to prepare the instances into a particular starting state.

    Args:
        ctx: Click context object holding commandline arguments.
    """
    args = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)  # noqa: SLF001
    command_args: CommandArgs = {
        "command_borders": ctx.params["command_borders"],
        "force": ctx.params["force"],
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

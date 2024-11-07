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
"""Idempotence Command Module."""
from __future__ import annotations

import logging
import re

from typing import TYPE_CHECKING

import click

from molecule import util
from molecule.command import base
from molecule.text import strip_ansi_escape


if TYPE_CHECKING:
    from molecule.types import CommandArgs, MoleculeArgs


LOG = logging.getLogger(__name__)


class Idempotence(base.Base):
    """Runs the converge step a second time.

    If no tasks will be marked as changed \
    the scenario will be considered idempotent.
    """

    def execute(self, action_args: list[str] | None = None) -> None:  # noqa: ARG002
        """Execute the actions necessary to perform a `molecule idempotence`.

        Args:
            action_args: Arguments for this command. Unused.
        """
        if not self._config.state.converged:
            msg = "Instances not converged.  Please converge instances first."
            util.sysexit_with_message(msg)

        if self._config.provisioner:
            output = self._config.provisioner.converge()

            idempotent = self._is_idempotent(output)
            if idempotent:
                msg = "Idempotence completed successfully."
                LOG.info(msg)
            else:
                details = "\n".join(self._non_idempotent_tasks(output))
                msg = f"Idempotence test failed because of the following tasks:\n{details}"
                util.sysexit_with_message(msg)

    def _is_idempotent(self, output: str) -> bool:
        """Parse the output of the provisioning for changed and returns a bool.

        Args:
            output: A string containing the output of the ansible run.

        Returns:
            bool: True if the output is idempotent, False otherwise.
        """
        # Remove blank lines to make regex matches easier
        output = re.sub(r"\n\s*\n*", "\n", output)

        # Look for any non-zero changed lines
        changed = re.search(r"(changed=[1-9][0-9]*)", output)

        return not bool(changed)

    def _non_idempotent_tasks(self, output: str) -> list[str]:
        """Parse the output to identify the non idempotent tasks.

        Args:
            output: A string containing the output of the ansible run.

        Returns:
            list: A list containing the names of the non idempotent tasks.

        """
        # Remove blank lines to make regex matches easier.
        output = re.sub(r"\n\s*\n*", "\n", output)

        # Remove ansi escape sequences.
        output = strip_ansi_escape(output)

        # Split the output into a list and go through it.
        output_lines = output.split("\n")
        res = []
        task_line = ""
        for _, line in enumerate(output_lines):
            if line.startswith("TASK"):
                task_line = line
            elif line.startswith("changed"):
                host_name = re.search(r"\[(.*)\]", line).groups()[0]  # type: ignore[union-attr]
                task_name = re.search(r"\[(.*)\]", task_line).groups()[0]  # type: ignore[union-attr]
                res.append(f"* [{host_name}] => {task_name}")

        return res


@base.click_command_ex()
@click.pass_context
@click.option(
    "--scenario-name",
    "-s",
    default=base.MOLECULE_DEFAULT_SCENARIO_NAME,
    help=f"Name of the scenario to target. ({base.MOLECULE_DEFAULT_SCENARIO_NAME})",
)
@click.argument("ansible_args", nargs=-1, type=click.UNPROCESSED)
def idempotence(
    ctx: click.Context,
    scenario_name: str,
    ansible_args: tuple[str, ...],
) -> None:  # pragma: no cover
    """Use the provisioner to configure the instances.

    After parse the output to determine idempotence.

    Args:
        ctx: Click context object holding commandline arguments.
        scenario_name: Name of the scenario to target.
        ansible_args: Arguments to forward to Ansible.
    """
    args: MoleculeArgs = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)  # noqa: SLF001
    command_args: CommandArgs = {"subcommand": subcommand}

    base.execute_cmdline_scenarios(scenario_name, args, command_args, ansible_args)

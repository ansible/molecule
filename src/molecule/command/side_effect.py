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

import argparse
import logging

from typing import TYPE_CHECKING

from molecule.command import base


if TYPE_CHECKING:
    from molecule.types import CommandArgs


LOG = logging.getLogger(__name__)


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
                msg = "Skipping, side effect playbook not configured."
                LOG.warning(msg)
                return

            self._config.provisioner.side_effect(action_args)


def side_effect() -> None:  # pragma: no cover
    """Use the provisioner to perform side-effects to the instances.

    Args:
        scenario_name: Name of the scenario to target.
    """
    parser = argparse.ArgumentParser(
        description="Use the provisioner to perform side-effects to the instances.",
    )
    parser.add_argument(
        "--scenario-name",
        "-s",
        default=base.MOLECULE_DEFAULT_SCENARIO_NAME,
        help=f"Name of the scenario to target. ({base.MOLECULE_DEFAULT_SCENARIO_NAME})",
    )

    args = parser.parse_args()
    scenario_name = args.scenario_name

    args_dict = {"args": vars(args)}
    subcommand = base._get_subcommand(__name__)  # noqa: SLF001
    command_args: CommandArgs = {"subcommand": subcommand}

    base.execute_cmdline_scenarios(scenario_name, args_dict, command_args)


if __name__ == "__main__":
    side_effect()

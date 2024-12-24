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
"""Verify Command Module."""
from __future__ import annotations

import argparse
import logging

from typing import TYPE_CHECKING

from molecule.command import base


if TYPE_CHECKING:
    from molecule.types import CommandArgs, MoleculeArgs


LOG = logging.getLogger(__name__)


class Verify(base.Base):
    """Verify Command Class."""

    def execute(self, action_args: list[str] | None = None) -> None:
        """Execute the actions necessary to perform a `molecule verify`.

        Args:
            action_args: Arguments for this command.
        """
        self._config.verifier.execute(action_args)


def verify() -> None:  # pragma: no cover
    """Run automated tests against instances.

    Args:
        scenario_name: Name of the scenario to target.
    """
    parser = argparse.ArgumentParser(description="Run automated tests against instances.")
    parser.add_argument(
        "--scenario-name",
        "-s",
        default=base.MOLECULE_DEFAULT_SCENARIO_NAME,
        help=f"Name of the scenario to target. ({base.MOLECULE_DEFAULT_SCENARIO_NAME})",
    )

    args = parser.parse_args()
    scenario_name = args.scenario_name

    args_dict: MoleculeArgs = {"args": vars(args)}
    subcommand = base._get_subcommand(__name__)  # noqa: SLF001
    command_args: CommandArgs = {"subcommand": subcommand}

    base.execute_cmdline_scenarios(scenario_name, args_dict, command_args)


if __name__ == "__main__":
    verify()

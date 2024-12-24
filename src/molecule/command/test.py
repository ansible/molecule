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
"""Test Command Module."""
from __future__ import annotations

import argparse
import logging
import os

from typing import TYPE_CHECKING

from molecule import util
from molecule.api import drivers
from molecule.command import base
from molecule.config import DEFAULT_DRIVER


if TYPE_CHECKING:
    from molecule.types import CommandArgs, MoleculeArgs


LOG = logging.getLogger(__name__)
MOLECULE_PARALLEL = os.environ.get("MOLECULE_PARALLEL", False)
MOLECULE_PLATFORM_NAME = os.environ.get("MOLECULE_PLATFORM_NAME", None)


class Test(base.Base):
    """Test Command Class."""

    def execute(self, action_args: list[str] | None = None) -> None:
        """Execute the actions necessary to perform a `molecule test`.

        Args:
            action_args: Arguments for this command. Unused.
        """


def test() -> None:  # pragma: no cover
    """Test (dependency, cleanup, destroy, syntax, create, prepare, converge, idempotence, side_effect, verify, cleanup, destroy).

    Args:
        scenario_name: Name of the scenario to target.
        driver_name: Name of the driver to use.
        __all: Whether molecule should target scenario_name or all scenarios.
        destroy: The destroy strategy to use.
        parallel: Whether the scenario(s) should be run in parallel mode.
        ansible_args: Arguments to forward to Ansible.
        platform_name: Name of the platform to use.
    """  # noqa: E501
    parser = argparse.ArgumentParser(
        description="Test (dependency, cleanup, destroy, syntax, create, prepare, converge, idempotence, side_effect, verify, cleanup, destroy).",
    )
    parser.add_argument(
        "--scenario-name",
        "-s",
        default=base.MOLECULE_DEFAULT_SCENARIO_NAME,
        help=f"Name of the scenario to target. ({base.MOLECULE_DEFAULT_SCENARIO_NAME})",
    )
    parser.add_argument(
        "--platform-name",
        "-p",
        default=MOLECULE_PLATFORM_NAME,
        help="Name of the platform to target only. Default is None",
    )
    parser.add_argument(
        "--driver-name",
        "-d",
        choices=[str(s) for s in drivers()],
        help=f"Name of driver to use. ({DEFAULT_DRIVER})",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="Test all scenarios. Default is False.",
    )
    parser.add_argument(
        "--destroy",
        choices=["always", "never"],
        default="always",
        help=("The destroy strategy used at the conclusion of a Molecule run (always)."),
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        default=MOLECULE_PARALLEL,
        help="Enable or disable parallel mode. Default is disabled.",
    )
    parser.add_argument(
        "ansible_args",
        nargs=argparse.REMAINDER,
        help="Arguments to forward to Ansible.",
    )

    args = parser.parse_args()
    scenario_name = args.scenario_name
    driver_name = args.driver_name
    __all = args.all
    destroy = args.destroy
    parallel = args.parallel
    ansible_args = args.ansible_args
    platform_name = args.platform_name

    args_dict: MoleculeArgs = {"args": vars(args)}
    subcommand = base._get_subcommand(__name__)  # noqa: SLF001
    command_args: CommandArgs = {
        "parallel": parallel,
        "destroy": destroy,
        "subcommand": subcommand,
        "driver_name": driver_name,
        "platform_name": platform_name,
    }

    if __all:
        scenario_name = None

    if parallel:
        util.validate_parallel_cmd_args(command_args)

    base.execute_cmdline_scenarios(scenario_name, args_dict, command_args, ansible_args)


if __name__ == "__main__":
    test()

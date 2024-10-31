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
"""Base class used by init scenario command."""
from __future__ import annotations

import json
import logging
import os
import sys

from pathlib import Path
from typing import TYPE_CHECKING

import click

from molecule import api, config, util
from molecule.command import base as command_base
from molecule.command.init import base
from molecule.config import DEFAULT_DRIVER, MOLECULE_EMBEDDED_DATA_DIR


if TYPE_CHECKING:
    from typing import TypedDict

    class CommandArgs(TypedDict):
        """Argument dictionary to pass to init-scenario playbook.

        Attributes:
            dependency_name: Name of the dependency to initialize.
            driver_name: Name of the driver to initialize.
            provisioner_name: Name of the provisioner to initialize.
            scenario_name: Name of the scenario to initialize.
            subcommand: Name of subcommand to initialize.
        """

        dependency_name: str
        driver_name: str
        provisioner_name: str
        scenario_name: str
        subcommand: str


LOG = logging.getLogger(__name__)


class Scenario(base.Base):
    """Scenario Class.

    .. program:: molecule init scenario bar --role-name foo

    .. option:: molecule init scenario bar --role-name foo

        Initialize a new scenario. In order to customize the role, please refer
        to the `init role` command.

    .. program:: cd foo; molecule init scenario bar --role-name foo

    .. option:: cd foo; molecule init scenario bar --role-name foo

        Initialize an existing role with Molecule:

    .. program:: cd foo; molecule init scenario bar --role-name foo

    .. option:: cd foo; molecule init scenario bar --role-name foo

        Initialize a new scenario using a embedded template.
    """

    def __init__(self, command_args: CommandArgs) -> None:
        """Construct Scenario.

        Args:
            command_args: Arguments to pass to init-scenario playbook.
        """
        self._command_args = command_args

    def execute(self, action_args: list[str] | None = None) -> None:  # noqa: ARG002
        """Execute the actions necessary to perform a `molecule init scenario`.

        Args:
            action_args: Arguments for this command. Unused.
        """
        scenario_name = self._command_args["scenario_name"]

        msg = f"Initializing new scenario {scenario_name}..."
        LOG.info(msg)
        molecule_directory = Path(config.molecule_directory(Path.cwd()))
        scenario_directory = molecule_directory / scenario_name

        if scenario_directory.is_dir():
            msg = f"The directory molecule/{scenario_name} exists. Cannot create new scenario."
            util.sysexit_with_message(msg)

        extra_vars = json.dumps(self._command_args)
        cmd = [
            "ansible-playbook",
            "-i",
            "localhost,",
            "--connection=local",
            "--extra-vars",
            extra_vars,
            f"{MOLECULE_EMBEDDED_DATA_DIR}/init-scenario.yml",
        ]
        env = os.environ.copy()
        # As ansible fails to find a terminal when run by molecule, we force
        # it to use colors.
        env["ANSIBLE_FORCE_COLOR"] = "1"
        env["ANSIBLE_PYTHON_INTERPRETER"] = sys.executable
        util.run_command(cmd, env=env, check=True)

        msg = f"Initialized scenario in {scenario_directory} successfully."
        LOG.info(msg)


def _role_exists(
    ctx: click.Context,  # noqa: ARG001
    param: str | None,  # noqa: ARG001
    value: str,
) -> str:  # pragma: no cover
    # if role name was not mentioned we assume that current directory is the
    # one hosting the role and determining the role name.
    if not value:
        value = Path.cwd().name

    role_directory = Path.cwd().parent / value
    if not role_directory.exists():
        msg = f"The role '{value}' not found. Please choose the proper role name."
        util.sysexit_with_message(msg)
    return value


@command_base.click_command_ex()
@click.pass_context
@click.option(
    "--dependency-name",
    type=click.Choice(["galaxy"]),
    default="galaxy",
    help="Name of dependency to initialize. (galaxy)",
)
@click.option(
    "--driver-name",
    "-d",
    type=click.Choice([str(s) for s in api.drivers()]),
    default=DEFAULT_DRIVER,
    help=f"Name of driver to initialize. ({DEFAULT_DRIVER})",
)
@click.option(
    "--provisioner-name",
    type=click.Choice(["ansible"]),
    default="ansible",
    help="Name of provisioner to initialize. (ansible)",
)
@click.argument(
    "scenario-name",
    default=command_base.MOLECULE_DEFAULT_SCENARIO_NAME,
    required=False,
)
def scenario(
    ctx: click.Context,  # noqa: ARG001
    dependency_name: str,
    driver_name: str,
    provisioner_name: str,
    scenario_name: str,
) -> None:  # pragma: no cover
    """Initialize a new scenario for use with Molecule.

    If name is not specified the 'default' value will be used.

    Args:
        ctx: Click context object holding commandline arguments.
        dependency_name: Name of dependency to initialize.
        driver_name: Name of driver to use.
        provisioner_name: Name of provisioner to use.
        scenario_name: Name of scenario to initialize.
    """
    command_args: CommandArgs = {
        "dependency_name": dependency_name,
        "driver_name": driver_name,
        "provisioner_name": provisioner_name,
        "scenario_name": scenario_name,
        "subcommand": __name__,
    }

    s = Scenario(command_args)
    s.execute()

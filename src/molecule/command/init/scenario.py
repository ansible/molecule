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
import os
import sys

from pathlib import Path
from typing import TYPE_CHECKING

import click

from molecule import api, logger
from molecule.click_cfg import click_command_ex
from molecule.command.init import base
from molecule.config import (
    DEFAULT_DRIVER,
    MOLECULE_EMBEDDED_DATA_DIR,
    Config,
    molecule_directory,
)
from molecule.constants import MOLECULE_DEFAULT_SCENARIO_NAME
from molecule.exceptions import MoleculeError


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

    def __init__(self, config: Config, command_args: CommandArgs) -> None:
        """Construct Scenario.

        Args:
            config: An instance of a Molecule config.
            command_args: Arguments to pass to init-scenario playbook.
        """
        self._config = config
        self._command_args = command_args
        # For init scenario, use the scenario name from command args
        scenario_name = command_args.get("scenario_name", "unknown")
        self._log = logger.get_scenario_logger(__name__, scenario_name)

    def execute(self, action_args: list[str] | None = None) -> None:  # noqa: ARG002
        """Execute the actions necessary to perform a `molecule init scenario`.

        Args:
            action_args: Arguments for this command. Unused.

        Raises:
            MoleculeError: when the scenario cannot be created.
        """
        scenario_name = self._command_args["scenario_name"]

        msg = f"Initializing new scenario {scenario_name}..."
        self._log.info(msg)
        molecule_path = Path(molecule_directory(Path.cwd()))
        scenario_directory = molecule_path / scenario_name

        if scenario_directory.is_dir():
            msg = f"The directory molecule/{scenario_name} exists. Cannot create new scenario."
            raise MoleculeError(msg)

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
        self._config.app.run_command(cmd, env=env, check=True)

        msg = f"Initialized scenario in {scenario_directory} successfully."
        self._log.info(msg)


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
        raise MoleculeError(msg)
    return value


@click_command_ex()
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
    type=str,
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
    default=MOLECULE_DEFAULT_SCENARIO_NAME,
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

    Raises:
        click.Abort: If the specified driver is not available.
    """
    config = Config("", args={})
    available_drivers = list(api.drivers(config).keys())
    if driver_name not in available_drivers:
        if len(available_drivers) == 1 and available_drivers[0] == "default":
            click.echo(
                click.style(
                    f"Driver '{driver_name}' not available.\n\n"
                    f"Install cloud drivers with:\n"
                    f"  pip install molecule-plugins\n\n"
                    f"Currently available drivers: {available_drivers}\n",
                    fg="red",
                ),
                err=True,
            )
        else:
            click.echo(
                click.style(
                    f"Driver '{driver_name}' not available.\n"
                    f"Available drivers: {available_drivers}",
                    fg="red",
                ),
                err=True,
            )
        raise click.Abort

    command_args: CommandArgs = {
        "dependency_name": dependency_name,
        "driver_name": driver_name,
        "provisioner_name": provisioner_name,
        "scenario_name": scenario_name,
        "subcommand": __name__,
    }

    config = Config(
        "",
        args={},
    )
    s = Scenario(config, command_args)
    s.execute()

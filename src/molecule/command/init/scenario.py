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

from molecule import logger, util
from molecule.click_cfg import click_command_ex
from molecule.command.init import base
from molecule.config import (
    MOLECULE_EMBEDDED_DATA_DIR,
    Config,
    molecule_directory,
)
from molecule.constants import (
    MOLECULE_COLLECTION_ROOT,
    MOLECULE_DEFAULT_SCENARIO_NAME,
    MOLECULE_ROOT,
)


if TYPE_CHECKING:
    from typing import TypedDict

    class CommandArgs(TypedDict):
        """Argument dictionary to pass to init-scenario playbook.

        Attributes:
            scenario_name: Name of the scenario to initialize.
            subcommand: Name of subcommand to initialize.
        """

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
        self._log = logger.get_scenario_logger(__name__, scenario_name, "init")

    def execute(self, action_args: list[str] | None = None) -> None:  # noqa: ARG002
        """Execute the actions necessary to perform a `molecule init scenario`.

        Args:
            action_args: Arguments for this command. Unused.
        """
        scenario_name = self._command_args["scenario_name"]

        msg = f"Initializing new scenario {scenario_name}..."
        self._log.info(msg)

        # Use collection-aware molecule directory
        collection_dir, _ = util.get_collection_metadata()

        if collection_dir:
            # We're in collection mode, use extensions/molecule
            molecule_path = collection_dir / MOLECULE_COLLECTION_ROOT
            relative_path = f"{MOLECULE_COLLECTION_ROOT}/{scenario_name}"
        else:
            # Standard mode, use molecule/
            molecule_path = Path(molecule_directory(Path.cwd()))
            relative_path = f"{MOLECULE_ROOT}/{scenario_name}"

        scenario_directory = molecule_path / scenario_name

        if scenario_directory.is_dir():
            msg = f"The directory {relative_path} exists. Cannot create new scenario."
            util.sysexit_with_message(msg, code=1)

        # Ensure parent directory exists
        molecule_path.mkdir(parents=True, exist_ok=True)

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
        self._config.app.run_command(
            cmd,
            env=env,
            check=True,
            command_borders=self._config.command_borders,
        )

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
        util.sysexit_with_message(msg, code=1)
    return value


@click_command_ex()
@click.pass_context
@click.argument(
    "scenario-name",
    default=MOLECULE_DEFAULT_SCENARIO_NAME,
    required=False,
)
def scenario(
    ctx: click.Context,  # noqa: ARG001
    scenario_name: str,
) -> None:  # pragma: no cover
    """Initialize a new scenario for use with Molecule.

    If name is not specified the 'default' value will be used.

    Args:
        ctx: Click context object holding commandline arguments.
        scenario_name: Name of scenario to initialize.
    """
    command_args: CommandArgs = {
        "scenario_name": scenario_name,
        "subcommand": __name__,
    }

    config = Config(
        "",
        args={},
    )
    s = Scenario(config, command_args)
    s.execute()

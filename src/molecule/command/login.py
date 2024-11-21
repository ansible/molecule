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
"""Login Command Module."""
from __future__ import annotations

import logging
import os
import shlex
import subprocess

from typing import TYPE_CHECKING

import click

from molecule import scenarios, util
from molecule.command import base


if TYPE_CHECKING:
    from molecule import config
    from molecule.types import CommandArgs


LOG = logging.getLogger(__name__)


class Login(base.Base):
    """Login Command Class."""

    def __init__(self, c: config.Config) -> None:
        """Construct Login.

        Args:
            c: An instance of a Molecule config.
        """
        super().__init__(c)
        self._pt = None

    def execute(self, action_args: list[str] | None = None) -> None:  # noqa: ARG002
        """Execute the actions necessary to perform a `molecule login`.

        Args:
            action_args: Arguments for this command. Unused.
        """
        c = self._config
        if (not c.state.created) and c.driver.managed:
            base.execute_subcommand(c, "create")

        hosts = [d["name"] for d in self._config.platforms.instances]
        hostname = self._get_hostname(hosts)
        self._get_login(hostname)

    def _get_hostname(self, hosts: list[str]) -> str:
        hostname = self._config.command_args.get("host")
        host_list = "\n".join(sorted(hosts))
        if hostname is None:
            if len(hosts) == 1:
                hostname = hosts[0]
            else:
                msg = (
                    f"There are {len(hosts)} running hosts. Please specify "
                    "which with --host.\n\n"
                    f"Available hosts:\n{host_list}"
                )
                util.sysexit_with_message(msg)
        match = [x for x in hosts if x.startswith(hostname)]
        if len(match) == 0:
            msg = (
                f"There are no hosts that match '{hostname}'.  You "
                "can only login to valid hosts."
            )
            util.sysexit_with_message(msg)
        elif len(match) != 1:
            # If there are multiple matches, but one of them is an exact string
            # match, assume this is the one they're looking for and use it.
            if hostname in match:
                match = [hostname]
            else:
                msg = (
                    f"There are {len(match)} hosts that match '{hostname}'. You "
                    "can only login to one at a time.\n\n"
                    f"Available hosts:\n{host_list}"
                )
                util.sysexit_with_message(msg)

        return match[0]

    def _get_login(self, hostname: str) -> None:  # pragma: no cover
        # ruff: noqa: S605,S607
        lines, columns = os.popen("stty size", "r").read().split()
        login_options = self._config.driver.login_options(hostname)
        login_options["columns"] = columns
        login_options["lines"] = lines
        if not self._config.driver.login_cmd_template:
            LOG.warning(
                "Login command is not supported for [dim]%s[/] host because 'login_cmd_template' was not defined in driver options.",  # noqa: E501
                login_options["instance"],
            )
            return
        login_cmd = self._config.driver.login_cmd_template.format(**login_options)

        cmd = shlex.split(f"/usr/bin/env {login_cmd}")
        # ruff: noqa: S603
        subprocess.run(cmd, check=False)


@base.click_command_ex()
@click.pass_context
@click.option("--host", "-h", help="Host to access.")
@click.option(
    "--scenario-name",
    "-s",
    default=base.MOLECULE_DEFAULT_SCENARIO_NAME,
    help=f"Name of the scenario to target. ({base.MOLECULE_DEFAULT_SCENARIO_NAME})",
)
def login(
    ctx: click.Context,
    host: str,
    scenario_name: str,
) -> None:  # pragma: no cover
    """Log in to one instance.

    Args:
        ctx: Click context object holding commandline arguments.
        host: Host to access.
        scenario_name: Name of the scenario to target.
    """
    args = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)  # noqa: SLF001
    command_args: CommandArgs = {"subcommand": subcommand, "host": host}

    s = scenarios.Scenarios(base.get_configs(args, command_args), scenario_name)
    for scenario in s.all:
        base.execute_subcommand(scenario.config, subcommand)

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

import logging
import os
import shlex
import subprocess

import click

from molecule import scenarios, util
from molecule.command import base

LOG = logging.getLogger(__name__)


class Login(base.Base):
    """
    Login Command Class.

    .. program:: molecule login

    .. option:: molecule login

        Target the default scenario.

    .. program:: molecule login --scenario-name foo

    .. option:: molecule login --scenario-name foo

        Targeting a specific scenario.

    .. program:: molecule login --host hostname

    .. option:: molecule login --host hostname

        Targeting a specific running host.

    .. program:: molecule login --host hostname --scenario-name foo

    .. option:: molecule login --host hostname --scenario-name foo

        Targeting a specific running host and scenario.

    .. program:: molecule --debug login

    .. option:: molecule --debug login

        Executing with `debug`.

    .. program:: molecule --base-config base.yml login

    .. option:: molecule --base-config base.yml login

        Executing with a `base-config`.

    .. program:: molecule --env-file foo.yml login

    .. option:: molecule --env-file foo.yml login

        Load an env file to read variables from when rendering
        molecule.yml.
    """

    def __init__(self, c):
        """Construct Login."""
        super(Login, self).__init__(c)
        self._pt = None

    def execute(self, action_args=None):
        """
        Execute the actions necessary to perform a `molecule login` and \
        returns None.

        :return: None
        """
        c = self._config
        if (not c.state.created) and c.driver.managed:
            msg = "Instances not created.  Please create instances first."
            util.sysexit_with_message(msg)

        hosts = [d["name"] for d in self._config.platforms.instances]
        hostname = self._get_hostname(hosts)
        self._get_login(hostname)

    def _get_hostname(self, hosts):
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

    def _get_login(self, hostname):  # pragma: no cover
        lines, columns = os.popen("stty size", "r").read().split()
        login_options = self._config.driver.login_options(hostname)
        login_options["columns"] = columns
        login_options["lines"] = lines
        login_cmd = self._config.driver.login_cmd_template.format(**login_options)

        cmd = shlex.split(f"/usr/bin/env {login_cmd}")
        subprocess.run(cmd)


@base.click_command_ex()
@click.pass_context
@click.option("--host", "-h", help="Host to access.")
@click.option(
    "--scenario-name",
    "-s",
    default=base.MOLECULE_DEFAULT_SCENARIO_NAME,
    help=f"Name of the scenario to target. ({base.MOLECULE_DEFAULT_SCENARIO_NAME})",
)
def login(ctx, host, scenario_name):  # pragma: no cover
    """Log in to one instance."""
    args = ctx.obj.get("args")
    subcommand = base._get_subcommand(__name__)
    command_args = {"subcommand": subcommand, "host": host}

    s = scenarios.Scenarios(base.get_configs(args, command_args), scenario_name)
    for scenario in s.all:
        base.execute_subcommand(scenario.config, subcommand)

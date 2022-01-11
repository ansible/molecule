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
"""Base class used by init role command."""

import logging
import os
import re

import click

from molecule import api, util
from molecule.command import base as command_base
from molecule.command.init import base
from molecule.config import DEFAULT_DRIVER

LOG = logging.getLogger(__name__)


class Role(base.Base):
    """
    Init Role Command Class.

    .. program:: molecule init role acme.foo

    .. option:: molecule init role acme.foo

        Initialize a new role.

        Initialize a new role using ansible-galaxy and include default
        molecule directory. Please refer to the ``init scenario``
        command in order to generate a custom ``molecule`` scenario.
    """

    def __init__(self, command_args):
        """Construct Role."""
        self._command_args = command_args

    def execute(self):
        """
        Execute the actions necessary to perform a `molecule init role` and \
        returns None.

        :return: None
        """
        namespace = None
        role_name = self._command_args["role_name"]
        role_directory = os.getcwd()

        # outside collections our tooling needs a namespace.
        if not os.path.isfile("../galaxy.yml"):
            name_re = re.compile(r"^[a-z][a-z0-9_]+\.[a-z][a-z0-9_]+$")

            if not name_re.match(role_name):
                util.sysexit_with_message(
                    "Outside collections you must mention role "
                    "namespace like: molecule init role 'acme.myrole'. Be sure "
                    "you use only lowercase characters and underlines. See https://galaxy.ansible.com/docs/contributing/creating_role.html"
                )
            namespace, role_name = role_name.split(".")

        msg = f"Initializing new role {role_name}..."
        LOG.info(msg)

        if os.path.isdir(role_name):
            msg = f"The directory {role_name} exists. Cannot create new role."
            util.sysexit_with_message(msg)

        cmd = ["ansible-galaxy", "init", "-v", "--offline", role_name]
        result = util.run_command(cmd)

        if result.returncode != 0:
            util.sysexit_with_message(
                f"Galaxy failed to create role, returned {result.returncode!s}"
            )

        if namespace:
            # we need to inject namespace info into meta/main.yml
            cmd = [
                "ansible",
                "localhost",
                "-o",  # one line output
                "-m",
                "lineinfile",
                "-a",
                f'path={role_name}/meta/main.yml line="  namespace: {namespace}" insertafter="  author: your name"',
            ]
            util.run_command(cmd, check=True)

        scenario_base_directory = os.path.join(role_directory, role_name)
        templates = [
            api.drivers()[self._command_args["driver_name"]].template_dir(),
            api.verifiers()[self._command_args["verifier_name"]].template_dir(),
        ]
        self._process_templates(
            "molecule", {**self._command_args, "role_name": role_name}, role_directory
        )
        for template in templates:
            self._process_templates(
                template, self._command_args, scenario_base_directory
            )

        role_directory = os.path.join(role_directory, role_name)
        msg = f"Initialized role in {role_directory} successfully."
        LOG.info(msg)


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
    "--lint-name",
    type=click.Choice(["yamllint"]),
    default="yamllint",
    help="Name of lint to initialize. (yamllint)",
)
@click.option(
    "--provisioner-name",
    type=click.Choice(["ansible"]),
    default="ansible",
    help="Name of provisioner to initialize. (ansible)",
)
@click.argument("ROLE-NAME", required=True)
@click.option(
    "--verifier-name",
    type=click.Choice([str(s) for s in api.verifiers()]),
    default="ansible",
    help="Name of verifier to initialize. (ansible)",
)
def role(
    ctx,
    dependency_name,
    driver_name,
    lint_name,
    provisioner_name,
    role_name,
    verifier_name,
):  # pragma: no cover
    """Initialize a new role for use with Molecule, namespace is required outside collections, like acme.myrole."""
    command_args = {
        "dependency_name": dependency_name,
        "driver_name": driver_name,
        "lint_name": lint_name,
        "provisioner_name": provisioner_name,
        "role_name": role_name,
        "scenario_name": command_base.MOLECULE_DEFAULT_SCENARIO_NAME,
        "subcommand": __name__,
        "verifier_name": verifier_name,
    }

    r = Role(command_args)
    r.execute()

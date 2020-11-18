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

import os

import click

from molecule import api, config, logger, util
from molecule.command import base as command_base
from molecule.command.init import base
from molecule.config import DEFAULT_DRIVER

LOG = logger.get_logger(__name__)


class Scenario(base.Base):
    """
    Scenario Class.

    .. program:: molecule init scenario bar --role-name foo

    .. option:: molecule init scenario bar --role-name foo

        Initialize a new scenario. In order to customise the role, please refer
        to the `init role` command.

    .. program:: cd foo; molecule init scenario bar --role-name foo

    .. option:: cd foo; molecule init scenario bar --role-name foo

        Initialize an existing role with Molecule:

    .. program:: cd foo; molecule init scenario bar --role-name foo

    .. option:: cd foo; molecule init scenario bar --role-name foo

        Initialize a new scenario using a local *cookiecutter* template for the
        driver configuration.
    """  # noqa

    def __init__(self, command_args):
        """Construct Scenario."""
        self._command_args = command_args

    def execute(self):
        """
        Execute the actions necessary to perform a `molecule init scenario` and \
        returns None.

        :return: None
        """
        scenario_name = self._command_args["scenario_name"]
        role_name = os.getcwd().split(os.sep)[-1]
        role_directory = util.abs_path(os.path.join(os.getcwd(), os.pardir))

        msg = "Initializing new scenario {}...".format(scenario_name)
        LOG.info(msg)
        molecule_directory = config.molecule_directory(
            os.path.join(role_directory, role_name)
        )
        scenario_directory = os.path.join(molecule_directory, scenario_name)

        if os.path.isdir(scenario_directory):
            msg = (
                "The directory molecule/{} exists. " "Cannot create new scenario."
            ).format(scenario_name)
            util.sysexit_with_message(msg)

        driver_template = api.drivers()[
            self._command_args["driver_name"]
        ].template_dir()
        if "driver_template" in self._command_args:
            self._validate_template_dir(self._command_args["driver_template"])
            cli_driver_template = "{driver_template}/{driver_name}".format(
                **self._command_args
            )
            if os.path.isdir(cli_driver_template):
                driver_template = cli_driver_template
            else:
                LOG.warning(
                    "Driver not found in custom template directory({}), "
                    "using the default template instead".format(cli_driver_template)
                )
        scenario_base_directory = os.path.join(role_directory, role_name)
        templates = [
            driver_template,
            api.verifiers()[self._command_args["verifier_name"]].template_dir(),
        ]
        self._process_templates("molecule", self._command_args, role_directory)
        for template in templates:
            self._process_templates(
                template, self._command_args, scenario_base_directory
            )

        role_directory = os.path.join(role_directory, role_name)
        msg = "Initialized scenario in {} successfully.".format(scenario_directory)
        LOG.info(msg)


def _role_exists(ctx, param, value):  # pragma: no cover
    # if role name was not mentioned we assume that current directory is the
    # one hosting the role and determining the role name.
    if not value:
        value = os.path.basename(os.getcwd())

    role_directory = os.path.join(os.pardir, value)
    if not os.path.exists(role_directory):
        msg = (
            "The role '{}' not found. " "Please choose the proper role name."
        ).format(value)
        util.sysexit_with_message(msg)
    return value


def _default_scenario_exists(ctx, param, value):  # pragma: no cover
    if value == command_base.MOLECULE_DEFAULT_SCENARIO_NAME:
        return value

    default_scenario_directory = os.path.join(
        "molecule", command_base.MOLECULE_DEFAULT_SCENARIO_NAME
    )
    if not os.path.exists(default_scenario_directory):
        msg = (
            "The default scenario not found.  Please create a scenario "
            "named '{}' first."
        ).format(command_base.MOLECULE_DEFAULT_SCENARIO_NAME)
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
    "--lint-name",
    type=click.Choice(["yamllint"]),
    default="yamllint",
    help="Name of lint to initialize. (ansible-lint)",
)
@click.option(
    "--provisioner-name",
    type=click.Choice(["ansible"]),
    default="ansible",
    help="Name of provisioner to initialize. (ansible)",
)
@click.option(
    "--role-name",
    "-r",
    required=False,
    callback=_role_exists,
    help="Name of the role to create.",
)
@click.argument(
    "scenario-name",
    default=command_base.MOLECULE_DEFAULT_SCENARIO_NAME,
    required=False,
    callback=_default_scenario_exists,
)
@click.option(
    "--verifier-name",
    type=click.Choice([str(s) for s in api.verifiers()]),
    default="ansible",
    help="Name of verifier to initialize. (ansible)",
)
def scenario(
    ctx,
    dependency_name,
    driver_name,
    lint_name,
    provisioner_name,
    role_name,
    scenario_name,
    verifier_name,
):  # pragma: no cover
    """Initialize a new scenario for use with Molecule.

    If name is not specified the 'default' value will be used.
    """
    command_args = {
        "dependency_name": dependency_name,
        "driver_name": driver_name,
        "lint_name": lint_name,
        "provisioner_name": provisioner_name,
        "role_name": role_name,
        "scenario_name": scenario_name,
        "subcommand": __name__,
        "verifier_name": verifier_name,
    }

    s = Scenario(command_args)
    s.execute()

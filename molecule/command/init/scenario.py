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

import os

import click

from molecule import api
from molecule import config
from molecule import logger
from molecule import util
from molecule.command import base as command_base
from molecule.command.init import base

LOG = logger.get_logger(__name__)


class Scenario(base.Base):
    """
    .. program:: molecule init scenario --scenario-name bar --role-name foo

    .. option:: molecule init scenario --scenario-name bar --role-name foo

        Initialize a new scenario. In order to customise the role, please refer
        to the `init role` command.

    .. program:: cd foo; molecule init scenario --scenario-name bar --role-name foo

    .. option:: cd foo; molecule init scenario --scenario-name bar --role-name foo

        Initialize an existing role with Molecule:

    .. program:: cd foo; molecule init scenario --scenario-name bar --role-name foo --driver-template path

    .. option:: cd foo; molecule init scenario --scenario-name bar --role-name foo --driver-template path

        Initialize a new scenario using a local *cookiecutter* template for the
        driver configuration.
    """  # noqa

    def __init__(self, command_args):
        self._command_args = command_args

    def execute(self):
        """
        Execute the actions necessary to perform a `molecule init scenario` and
        returns None.

        :return: None
        """
        scenario_name = self._command_args['scenario_name']
        role_name = os.getcwd().split(os.sep)[-1]
        role_directory = util.abs_path(os.path.join(os.getcwd(), os.pardir))

        msg = 'Initializing new scenario {}...'.format(scenario_name)
        LOG.info(msg)
        molecule_directory = config.molecule_directory(
            os.path.join(role_directory, role_name)
        )
        scenario_directory = os.path.join(molecule_directory, scenario_name)

        if os.path.isdir(scenario_directory):
            msg = (
                'The directory molecule/{} exists. ' 'Cannot create new scenario.'
            ).format(scenario_name)
            util.sysexit_with_message(msg)

        driver_template = api.drivers()[
            self._command_args['driver_name']
        ].template_dir()
        if 'driver_template' in self._command_args:
            self._validate_template_dir(self._command_args['driver_template'])
            cli_driver_template = '{driver_template}/{driver_name}'.format(
                **self._command_args
            )
            if os.path.isdir(cli_driver_template):
                driver_template = cli_driver_template
            else:
                LOG.warn(
                    "Driver not found in custom template directory({}), "
                    "using the default template instead".format(cli_driver_template)
                )
        scenario_base_directory = os.path.join(role_directory, role_name)
        templates = [
            driver_template,
            api.verifiers()[self._command_args['verifier_name']].template_dir(),
        ]
        for template in templates:
            self._process_templates(
                template, self._command_args, scenario_base_directory
            )
        self._process_templates('molecule', self._command_args, role_directory)

        role_directory = os.path.join(role_directory, role_name)
        msg = 'Initialized scenario in {} successfully.'.format(scenario_directory)
        LOG.success(msg)


def _role_exists(ctx, param, value):  # pragma: no cover
    # if role name was not mentioned we assume that current directory is the
    # one hosting the role and determining the role name.
    if not value:
        value = os.path.basename(os.getcwd())

    role_directory = os.path.join(os.pardir, value)
    if not os.path.exists(role_directory):
        msg = (
            "The role '{}' not found. " 'Please choose the proper role name.'
        ).format(value)
        util.sysexit_with_message(msg)
    return value


def _default_scenario_exists(ctx, param, value):  # pragma: no cover
    if value == command_base.MOLECULE_DEFAULT_SCENARIO_NAME:
        return value

    default_scenario_directory = os.path.join(
        'molecule', command_base.MOLECULE_DEFAULT_SCENARIO_NAME
    )
    if not os.path.exists(default_scenario_directory):
        msg = (
            'The default scenario not found.  Please create a scenario '
            "named '{}' first."
        ).format(command_base.MOLECULE_DEFAULT_SCENARIO_NAME)
        util.sysexit_with_message(msg)
    return value


@click.command()
@click.pass_context
@click.option(
    '--dependency-name',
    type=click.Choice(['galaxy']),
    default='galaxy',
    help='Name of dependency to initialize. (galaxy)',
)
@click.option(
    '--driver-name',
    '-d',
    type=click.Choice(api.drivers()),
    default='docker',
    help='Name of driver to initialize. (docker)',
)
@click.option(
    '--lint-name',
    type=click.Choice(['yamllint']),
    default='yamllint',
    help='Name of lint to initialize. (ansible-lint)',
)
@click.option(
    '--provisioner-name',
    type=click.Choice(['ansible']),
    default='ansible',
    help='Name of provisioner to initialize. (ansible)',
)
@click.option(
    '--role-name',
    '-r',
    required=False,
    callback=_role_exists,
    help='Name of the role to create.',
)
@click.option(
    '--scenario-name',
    '-s',
    default=command_base.MOLECULE_DEFAULT_SCENARIO_NAME,
    required=True,
    callback=_default_scenario_exists,
    help='Name of the scenario to create. ({})'.format(
        command_base.MOLECULE_DEFAULT_SCENARIO_NAME
    ),
)
@click.option(
    '--verifier-name',
    type=click.Choice([str(s) for s in api.verifiers()]),
    default='testinfra',
    help='Name of verifier to initialize. (testinfra)',
)
@click.option(
    '--driver-template',
    type=click.Path(exists=True, dir_okay=True, readable=True, resolve_path=True),
    help="Path to a cookiecutter custom driver template to initialize the "
    "scenario. If the driver template is not found locally, default "
    "template will be used instead.",
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
    driver_template,
):  # pragma: no cover
    """ Initialize a new scenario for use with Molecule. """
    command_args = {
        'dependency_name': dependency_name,
        'driver_name': driver_name,
        'lint_name': lint_name,
        'provisioner_name': provisioner_name,
        'role_name': role_name,
        'scenario_name': scenario_name,
        'subcommand': __name__,
        'verifier_name': verifier_name,
    }

    command_args['verifier_lint_name'] = api.verifiers()[verifier_name].default_linter

    driver_template = driver_template or os.environ.get(
        'MOLECULE_SCENARIO_DRIVER_TEMPLATE', None
    )
    if driver_template:
        command_args['driver_template'] = driver_template

    s = Scenario(command_args)
    s.execute()

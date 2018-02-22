#  Copyright (c) 2015-2017 Cisco Systems, Inc.
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

from molecule import config
from molecule import logger
from molecule import util
from molecule.command.init import base

LOG = logger.get_logger(__name__)


class Scenario(base.Base):
    """
    Initialize a new scenario:

    $ molecule init scenario --scenario-name default --role-name foo

    Initialize an existing role with Molecule:

    $ cd foo
    $ molecule init scenario --scenario-name default --role-name foo
    """

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
            os.path.join(role_directory, role_name))
        scenario_directory = os.path.join(molecule_directory, scenario_name)
        scenario_base_directory = os.path.dirname(scenario_directory)

        if os.path.isdir(scenario_directory):
            msg = ('The directory molecule/{} exists. '
                   'Cannot create new scenario.').format(scenario_name)
            util.sysexit_with_message(msg)

        scenario_base_directory = os.path.join(role_directory, role_name)
        templates = [
            'scenario/driver/{driver_name}'.format(**self._command_args),
            'scenario/verifier/{verifier_name}'.format(**self._command_args),
        ]
        for template in templates:
            self._process_templates(template, self._command_args,
                                    scenario_base_directory)
        self._process_templates('molecule', self._command_args, role_directory)

        role_directory = os.path.join(role_directory, role_name)
        msg = 'Initialized scenario in {} successfully.'.format(
            scenario_directory)
        LOG.success(msg)


def _role_exists(ctx, param, value):  # pragma: no cover
    role_directory = os.path.join(os.pardir, value)
    if not os.path.exists(role_directory):
        msg = ("The role '{}' not found. "
               'Please choose the proper role name.').format(value)
        util.sysexit_with_message(msg)
    return value


def _default_scenario_exists(ctx, param, value):  # pragma: no cover
    if value == 'default':
        return value

    default_scenario_directory = os.path.join('molecule', 'default')
    if not os.path.exists(default_scenario_directory):
        msg = ('The default scenario not found.  Please create a scenario '
               "named 'default' first.")
        util.sysexit_with_message(msg)
    return value


@click.command()
@click.pass_context
@click.option(
    '--dependency-name',
    type=click.Choice(['galaxy']),
    default='galaxy',
    help='Name of dependency to initialize. (galaxy)')
@click.option(
    '--driver-name',
    '-d',
    type=click.Choice(config.molecule_drivers()),
    default='docker',
    help='Name of driver to initialize. (docker)')
@click.option(
    '--lint-name',
    type=click.Choice(['yamllint']),
    default='yamllint',
    help='Name of lint to initialize. (ansible-lint)')
@click.option(
    '--provisioner-name',
    type=click.Choice(['ansible']),
    default='ansible',
    help='Name of provisioner to initialize. (ansible)')
@click.option(
    '--role-name',
    '-r',
    required=True,
    callback=_role_exists,
    help='Name of the role to create.')
@click.option(
    '--scenario-name',
    '-s',
    default='default',
    required=True,
    callback=_default_scenario_exists,
    help='Name of the scenario to create.')
@click.option(
    '--verifier-name',
    type=click.Choice(config.molecule_verifiers()),
    default='testinfra',
    help='Name of verifier to initialize. (testinfra)')
def scenario(ctx, dependency_name, driver_name, lint_name, provisioner_name,
             role_name, scenario_name, verifier_name):  # pragma: no cover
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

    if verifier_name == 'goss':
        command_args.update({'verifier_lint_name': "'None'"})

    s = Scenario(command_args)
    s.execute()

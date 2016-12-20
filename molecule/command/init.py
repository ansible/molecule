#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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
import cookiecutter
import cookiecutter.main

from molecule import config
from molecule import util


def _process_templates(template_dir,
                       extra_context,
                       output_dir,
                       debug=True,
                       overwrite=True):
    """
    Process templates as found in the named directory.
    :param template_dir: An absolute or relative path to a directory where
     the templates are located. If the provided directory is a relative
     path, it is resolved using a known location.
    :type template_dir: str
    :param extra_context: A set of values that are used to override default
     or user specified values.
    :type extra_context: dict or None
    :param output_dir: An absolute path to a directory where the templates
     should be written to.
    :type output_dir: str
    :param overwrite: Whether or not to overwrite existing templates.
     Defaults to True.
    :type overwrite: bool
    :return: None
    """
    template_dir = _resolve_template_dir(template_dir)

    cookiecutter.main.cookiecutter(
        template_dir,
        extra_context=extra_context,
        output_dir=output_dir,
        overwrite_if_exists=overwrite,
        no_input=True, )


def _resolve_template_dir(template_dir):
    if not os.path.isabs(template_dir):
        template_dir = os.path.join(
            os.path.dirname(__file__), os.path.pardir, os.path.pardir,
            'cookiecutter', template_dir)

    return template_dir


def _init_new_role(command_args):
    role_name = command_args['role_name']
    role_directory = os.getcwd()
    util.print_info('Initializing new role {}...'.format(role_name))

    if os.path.isdir(role_name):
        msg = ('The directory {} exists. '
               'Cannot create new role.').format(role_name)
        util.print_error(msg)
        util.sysexit()

    extra_context = command_args
    _process_templates('role', extra_context, role_directory)
    scenario_base_directory = os.path.join(role_directory, role_name)
    _process_templates('scenario/driver/docker', extra_context,
                       scenario_base_directory)
    _process_templates('scenario/verifier/testinfra', extra_context,
                       scenario_base_directory)

    role_directory = os.path.join(role_directory, role_name)
    msg = 'Successfully initialized role in {}.'.format(role_directory)
    util.print_success(msg)


def _init_new_scenario(command_args):
    scenario_name = command_args['scenario_name']
    role_name = os.getcwd().split(os.sep)[-1]
    role_directory = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

    util.print_info('Initializing new scenario {}...'.format(scenario_name))
    molecule_directory = config.molecule_directory(
        os.path.join(role_directory, role_name))
    scenario_directory = os.path.join(molecule_directory, scenario_name)
    scenario_base_directory = os.path.dirname(scenario_directory)

    if os.path.isdir(scenario_directory):
        msg = ('The directory molecule/{} exists. '
               'Cannot create new scenario.').format(scenario_name)
        util.print_error(msg)
        util.sysexit()

    extra_context = command_args
    scenario_base_directory = os.path.join(role_directory, role_name)
    _process_templates('scenario/driver/docker', extra_context,
                       scenario_base_directory)
    _process_templates('scenario/verifier/testinfra', extra_context,
                       scenario_base_directory)

    role_directory = os.path.join(role_directory, role_name)
    msg = 'Successfully initialized scenario in {}.'.format(scenario_directory)
    util.print_success(msg)


@click.group()
@click.pass_context
def init(ctx):
    """ Initialize a new role or scenario. """


@init.command()
@click.option(
    '--dependency-name',
    type=click.Choice(['galaxy']),
    default='galaxy',
    help='Name of dependency to initialize. (galaxy)')
@click.option(
    '--driver-name',
    type=click.Choice(['docker']),
    default='docker',
    help='Name of driver to initialize. (docker)')
@click.option(
    '--lint-name',
    type=click.Choice(['ansible-lint']),
    default='ansible-lint',
    help='Name of lint to initialize. (ansible-lint)')
@click.option(
    '--provisioner-name',
    type=click.Choice(['ansible']),
    default='ansible',
    help='Name of provisioner to initialize. (ansible)')
@click.option('--role-name', required=True, help='Name of the role to create.')
@click.option(
    '--verifier-name',
    type=click.Choice(['testinfra']),
    default='testinfra',
    help='Name of verifier to initialize. (testinfra)')
@click.pass_context
def role(ctx, dependency_name, driver_name, lint_name, provisioner_name,
         role_name, verifier_name):  # pragma: no cover
    """ Initialize a new role for use with Molecule. """
    # args = ctx.obj.get('args')
    command_args = {
        'dependency_name': dependency_name,
        'driver_name': driver_name,
        'lint_name': lint_name,
        'provisioner_name': provisioner_name,
        'role_name': role_name,
        'scenario_name': 'default',
        'subcommand': __name__,
        'verifier_name': verifier_name
    }

    _init_new_role(command_args)


@init.command()
@click.option(
    '--driver-name',
    type=click.Choice(['docker']),
    default='docker',
    help='Name of driver to initialize. (docker)')
@click.option('--role-name', required=True, help='Name of the role to create.')
@click.option(
    '--scenario-name', required=True, help='Name of the scenario to create.')
@click.option(
    '--verifier-name',
    type=click.Choice(['testinfra']),
    default='testinfra',
    help='Name of verifier to initialize. (testinfra)')
@click.pass_context
def scenario(ctx, driver_name, role_name, scenario_name,
             verifier_name):  # pragma: no cover
    """ Initialize a new scenario for use with Molecule. """
    # args = ctx.obj.get('args')
    command_args = {
        'driver_name': driver_name,
        'role_name': role_name,
        'scenario_name': scenario_name,
        'subcommand': __name__,
        'verifier_name': verifier_name
    }

    _init_new_scenario(command_args)

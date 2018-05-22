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

import distutils
import distutils.version
import os
import sys

import ansible
import click
import click_completion

import molecule
from molecule import command
from molecule import util

click_completion.init()

LOCAL_CONFIG = os.path.expanduser('~/.config/molecule/config.yml')
ENV_FILE = '.env.yml'


def _get_python_version():  # pragma: no cover
    return sys.version_info[:2]


def _get_ansible_version():  # pragma: no cover
    return ansible.__version__


def _supported_python2_version():  # pragma: no cover
    return _get_python_version() == (2, 7)


def _supported_python3_version():  # pragma: no cover
    return _get_python_version() == (3, 6)


def _supported_ansible_version():  # pragma: no cover
    if (distutils.version.LooseVersion(_get_ansible_version()) <=
            distutils.version.LooseVersion('2.2')):
        msg = ("Ansible version '{}' not supported.  "
               'Molecule only supports Ansible versions '
               "'>= 2.2'.").format(_get_ansible_version())
        util.sysexit_with_message(msg)

    if _supported_python2_version():
        pass
    elif _supported_python3_version():
        if (distutils.version.LooseVersion(_get_ansible_version()) <
                distutils.version.LooseVersion('2.4')):
            msg = ("Ansible version '{}' not supported.  "
                   'Molecule only supports Ansible versions '
                   "'>=2.5' with Python version '{}'").format(
                       _get_ansible_version(), _get_python_version())
            util.sysexit_with_message(msg)
    else:
        msg = ("Python version '{}' not supported.  "
               'Molecule only supports Python versions '
               "'2.7' and '3.6'.").format(_get_python_version())
        util.sysexit_with_message(msg)


def _allowed(ctx, param, value):  # pragma: no cover
    _supported_ansible_version()

    return value


@click.group()
@click.option(
    '--debug/--no-debug',
    default=False,
    callback=_allowed,
    help='Enable or disable debug mode. Default is disabled.')
@click.option(
    '--base-config',
    '-c',
    default=LOCAL_CONFIG,
    help=('Path to a base config.  If provided Molecule will load '
          "this config first, and deep merge each scenario's "
          'molecule.yml on top. ({})').format(LOCAL_CONFIG))
@click.option(
    '--env-file',
    '-e',
    default=ENV_FILE,
    help=('The file to read variables from when rendering molecule.yml. '
          '(.env.yml)'))
@click.version_option(version=molecule.__version__)
@click.pass_context
def main(ctx, debug, base_config, env_file):  # pragma: no cover
    """
    \b
     _____     _             _
    |     |___| |___ ___ _ _| |___
    | | | | . | | -_|  _| | | | -_|
    |_|_|_|___|_|___|___|___|_|___|

    Molecule aids in the development and testing of Ansible roles.

    Enable autocomplete issue:

      eval "$(_MOLECULE_COMPLETE=source molecule)"
    """
    ctx.obj = {}
    ctx.obj['args'] = {}
    ctx.obj['args']['debug'] = debug
    ctx.obj['args']['base_config'] = base_config
    ctx.obj['args']['env_file'] = env_file


main.add_command(command.check.check)
main.add_command(command.converge.converge)
main.add_command(command.create.create)
main.add_command(command.dependency.dependency)
main.add_command(command.destroy.destroy)
main.add_command(command.idempotence.idempotence)
main.add_command(command.init.init)
main.add_command(command.lint.lint)
main.add_command(command.list.list)
main.add_command(command.login.login)
main.add_command(command.prepare.prepare)
main.add_command(command.side_effect.side_effect)
main.add_command(command.syntax.syntax)
main.add_command(command.test.test)
main.add_command(command.verify.verify)

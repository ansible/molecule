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

from molecule import util
from molecule.command import base


class Init(base.Base):
    def main(self):
        """
        Overriden to prevent the initialization of a molecule object, since
        :class:`.Config` cannot parse a non-existent `molecule.yml`.

        :returns: None
        """
        pass

    def execute(self, exit=True):
        """
        Execute the actions necessary to perform a `molecule init` and exit.

        :param exit: (Unused) Provided to complete method signature.
        :return: None
        """
        role = self.command_args.get('role')
        role_path = os.getcwd()
        driver = self._get_driver()
        verifier = self._get_verifier()
        if not role:
            role = os.getcwd().split(os.sep)[-1]
            role_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
            self._init_existing_role(role, role_path, driver, verifier)
        else:
            if os.path.isdir(role):
                msg = ('The directory {} exists. '
                       'Cannot create new role.').format(role)
                util.print_error(msg)
                util.sysexit()
            self._init_new_role(role, role_path, driver, verifier)

        path = os.path.join(role_path, role)
        msg = 'Successfully initialized new role in {}.'.format(path)
        util.print_success(msg)
        util.sysexit(0)

    def _init_existing_role(self, role, role_path, driver, verifier):
        extra_context = self._get_cookiecutter_context(role, driver, verifier)

        util.print_info('Initializing molecule in current directory...')
        for template in [
                'playbook', 'driver/{}'.format(driver),
                'verifier/{}'.format(verifier)
        ]:
            util.process_templates(template, extra_context, role_path)

    def _init_new_role(self, role, role_path, driver, verifier):
        extra_context = self._get_cookiecutter_context(role, driver, verifier)

        util.print_info('Initializing role {}...'.format(role))
        for template in [
                'galaxy_init', 'playbook', 'driver/{}'.format(driver),
                'verifier/{}'.format(verifier)
        ]:
            util.process_templates(template, extra_context, role_path)

    def _get_cookiecutter_context(self, role, driver, verifier):
        md = self.molecule.config.config['molecule']['init']
        platform = md.get('platform')
        provider = md.get('provider')

        d = {
            'repo_name': role,
            'role_name': role,
            'driver_name': driver,
            'dependency_name': 'galaxy',  # static for now
            'verifier_name': verifier,
        }
        if driver == 'vagrant':
            d.update({
                'platform_name': platform.get('name'),
                'platform_box': platform.get('box'),
                'platform_box_url': platform.get('box_url'),
                'provider_name': provider.get('name'),
                'provider_type': provider.get('type')
            })

        return d

    def _get_driver(self):
        return self.command_args.get('driver')

    def _get_verifier(self):
        return self.command_args.get('verifier')


@click.command()
@click.option(
    '--role',
    help=('Name of role to create, otherwise initalize molecule inside '
          'existing directory.'))
@click.option(
    '--driver',
    type=click.Choice(['vagrant', 'docker', 'openstack']),
    default='vagrant',
    help='Name of driver to initialize.')
@click.option(
    '--verifier',
    type=click.Choice(['testinfra', 'serverspec', 'goss']),
    default='testinfra',
    help='Name of verifier to initialize.')
@click.pass_context
def init(ctx, role, driver, verifier):  # pragma: no cover
    """
    Creates the scaffolding for a new role intended for use with molecule.
    """
    command_args = {'role': role, 'driver': driver, 'verifier': verifier}

    i = Init(ctx.obj.get('args'), command_args)
    i.execute
    util.sysexit(i.execute()[0])

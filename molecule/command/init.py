#  Copyright (c) 2015-2016 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

import os

import cookiecutter
import cookiecutter.main

from molecule import util
from molecule.command import base

LOG = util.get_logger(__name__)


class Init(base.Base):
    """
    Creates the scaffolding for a new role intended for use with molecule.

    Usage:
        init [<role>] [--docker | --openstack] [--serverspec | --goss] [--offline]
    """

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
        role = self.molecule.args['<role>']
        role_path = os.getcwd()
        if not role:
            role = os.getcwd().split(os.sep)[-1]
            role_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
            self._init_existing_role(role, role_path)
        else:
            if os.path.isdir(role):
                msg = 'The directory {} already exists. Cannot create new role.'
                LOG.error(msg.format(role))
                util.sysexit()
            self._init_new_role(role, role_path)

        msg = 'Successfully initialized new role in {}...'
        util.print_success(msg.format(os.path.join(role_path, role)))
        util.sysexit(0)

    def _init_existing_role(self, role, role_path):
        driver = self._get_driver()
        extra_context = self._get_cookiecutter_context(role, driver)

        util.print_info("Initializing molecule in current directory...")
        for template in ['playbook', 'driver/{}'.format(driver)]:
            self._create_template(template, extra_context, role_path)

    def _init_new_role(self, role, role_path):
        driver = self._get_driver()
        verifier = self._get_verifier()
        extra_context = self._get_cookiecutter_context(role, driver)

        util.print_info("Initializing role {}...".format(role))
        for template in ['galaxy_init', 'playbook', 'driver/{}'.format(driver),
                         'verifier/{}'.format(verifier)]:
            self._create_template(template, extra_context, role_path)

    def _create_template(self,
                         template,
                         extra_context,
                         output_dir,
                         no_input=True,
                         overwrite=True):
        t = self._get_cookiecutter_template_dir(template)

        cookiecutter.main.cookiecutter(t,
                                       extra_context=extra_context,
                                       output_dir=output_dir,
                                       no_input=no_input,
                                       overwrite_if_exists=overwrite)

    def _get_cookiecutter_context(self, role, driver):
        md = self.molecule.config.config['molecule']['init']
        platform = md.get('platform')
        provider = md.get('provider')

        d = {
            'repo_name': role,
            'role_name': role,
            'driver': driver,
        }
        if driver == 'vagrant':
            d.update({'platform_name': platform.get('name'),
                      'platform_box': platform.get('box'),
                      'platform_box_url': platform.get('box_url'),
                      'provider_name': provider.get('name'),
                      'provider_type': provider.get('type')})

        return d

    def _get_cookiecutter_template_dir(self, template):
        return os.path.join(
            os.path.dirname(__file__), '..', 'cookiecutter', template)

    def _get_driver(self):
        if self.molecule.args['--docker']:
            return 'docker'
        elif self.molecule.args['--openstack']:
            return 'openstack'
        else:
            return 'vagrant'

    def _get_verifier(self):
        if self.molecule.args['--serverspec']:
            return 'serverspec'
        elif self.molecule.args['--goss']:
            return 'goss'
        else:
            return 'testinfra'

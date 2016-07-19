#  Copyright (c) 2015-2016 Cisco Systems
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
import re
import subprocess

import jinja2
import sh

from molecule import utilities
from molecule.commands import base


class Init(base.BaseCommand):
    """
    Creates the scaffolding for a new role intended for use with molecule.

    Usage:
        init [<role>] [--docker | --openstack] [--offline]
    """

    def clean_meta_main(self, role_path):
        main_path = os.path.join(role_path, 'meta', 'main.yml')
        temp_path = os.path.join(role_path, 'meta', 'main.yml.tmp')
        with open(temp_path, 'w') as temp:
            for line in file(main_path):
                line = re.sub(r'[ \t]*$', '', line)
                if line != '\n':
                    temp.write(line)
        os.rename(temp_path, main_path)

    def execute(self):
        role = self.molecule._args['<role>']

        if not role:
            role = os.getcwd().split(os.sep)[-1]
            role_path = os.getcwd()
            utilities.print_info(
                "Initializing molecule in current directory...")
            if not os.path.isdir(os.path.join(role_path, "tests")):
                os.mkdir(os.path.join(role_path, "tests"))

        else:

            if os.path.isdir(role):
                msg = 'The directory {} already exists. Cannot create new role.'
                utilities.logger.error(msg.format(role))
                utilities.sysexit()

            role_path = os.path.join(os.curdir, role)

            utilities.print_info("Initializing role {}...".format(role))

            try:
                if self.molecule._args['--offline']:
                    sh.ansible_galaxy('init', '--offline', role)
                else:
                    sh.ansible_galaxy('init', role)
            except (subprocess.CalledProcessError, sh.ErrorReturnCode_1) as e:
                utilities.logger.error('ERROR: {}'.format(e))
                utilities.sysexit(e.returncode)

            self.clean_meta_main(role_path)

        env = jinja2.Environment(
            loader=jinja2.PackageLoader('molecule', 'templates'),
            keep_trailing_newline=True)

        t_molecule = env.get_template(self.molecule._config.config['molecule'][
            'init']['templates']['molecule'])
        t_playbook = env.get_template(self.molecule._config.config['molecule'][
            'init']['templates']['playbook'])
        t_test_default = env.get_template(self.molecule._config.config[
            'molecule']['init']['templates']['test_default'])

        if (self.molecule._args['--docker']):
            t_molecule = env.get_template(self.molecule._config.config[
                'molecule']['init']['templates']['molecule_docker'])
        if (self.molecule._args['--openstack']):
            t_molecule = env.get_template(self.molecule._config.config[
                'molecule']['init']['templates']['molecule_openstack'])

        sanitized_role = re.sub('[._]', '-', role)
        with open(
                os.path.join(
                    role_path,
                    self.molecule._config.config['molecule']['molecule_file']),
                'w') as f:
            f.write(t_molecule.render(config=self.molecule._config.config,
                                      role=sanitized_role))

        with open(
                os.path.join(
                    role_path,
                    self.molecule._config.config['ansible']['playbook']),
                'w') as f:
            f.write(t_playbook.render(role=role))

        testinfra_path = os.path.join(
            role_path,
            self.molecule._config.config['molecule']['testinfra_dir'])

        with open(os.path.join(testinfra_path, 'test_default.py'), 'w') as f:
            f.write(t_test_default.render())

        msg = 'Successfully initialized new role in {}'
        utilities.print_success(msg.format(role_path))
        utilities.sysexit(0)

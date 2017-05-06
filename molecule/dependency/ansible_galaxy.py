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

import sh

from molecule import logger
from molecule import util
from molecule.dependency import base

LOG = logger.get_logger(__name__)


class AnsibleGalaxy(base.Base):
    """
    `Ansible Galaxy`_ is the default dependency manager.

    Additional options can be passed to `ansible-galaxy install` through the
    options dict.  Any option set in this section will override the defaults.

    .. code-block:: yaml

        dependency:
          name: galaxy
          options:
            ignore-certs: True
            ignore-errors: True


    The dependency manager can be disabled by setting `enabled` to False.

    .. code-block:: yaml

        dependency:
          name: galaxy
          enabled: False

    Environment variables can be passed to the dependency.

    .. code-block:: yaml

        dependency:
          name: galaxy
          env:
            FOO: bar

    .. _`Ansible Galaxy`: http://docs.ansible.com/ansible/galaxy.html
    """

    def __init__(self, config):
        super(AnsibleGalaxy, self).__init__(config)
        self._ansible_galaxy_command = None

    @property
    def default_options(self):
        """
        Default CLI arguments provided to `ansible-galaxy` and returns a dict.

        :return: dict
        """
        d = {
            'force': True,
            'role-file':
            os.path.join(self._config.scenario.directory, 'requirements.yml'),
            'roles-path':
            os.path.join(self._config.ephemeral_directory, 'roles'),
        }
        if self._config.args.get('debug'):
            d['vvv'] = True

        return d

    @property
    def default_env(self):
        """
        Default env variables provided to `testinfra` and returns a
        dict.

        :return: dict
        """
        return self._config.merge_dicts(os.environ.copy(), self._config.env)

    def bake(self):
        """
        Bake an `ansible-galaxy` command so it's ready to execute and returns
        None.

        :return: None
        """
        options = self.options
        verbose_flag = util.verbose_flag(options)

        self._ansible_galaxy_command = sh.ansible_galaxy.bake(
            'install',
            options,
            *verbose_flag,
            _env=self.env,
            _out=LOG.out,
            _err=LOG.error)

    def execute(self):
        """
        Executes `ansible-galaxy` and returns None.

        :return: None
        """
        if not self.enabled:
            LOG.warn('Skipping, dependency is disabled.')
            return

        if not self._has_requirements_file():
            LOG.warn('Skipping, missing the requirements file.')
            return

        if self._ansible_galaxy_command is None:
            self.bake()

        self._setup()
        try:
            util.run_command(
                self._ansible_galaxy_command,
                debug=self._config.args.get('debug'))
            LOG.success('Dependency completed successfully.')
        except sh.ErrorReturnCode as e:
            util.sysexit(e.exit_code)

    def _setup(self):
        """
        Prepare the system for using `ansible-galaxy` and returns None.

        :return: None
        """
        role_directory = os.path.join(self._config.scenario.directory,
                                      self.options['roles-path'])
        if not os.path.isdir(role_directory):
            os.makedirs(role_directory)

    def _has_requirements_file(self):
        role_file = self.options.get('role-file')

        return role_file and os.path.isfile(role_file)

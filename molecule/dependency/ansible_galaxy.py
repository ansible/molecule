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
"""Ansible-Galaxy Dependency Module."""

import os

import sh

from molecule import logger
from molecule import util
from molecule.dependency import base

LOG = logger.get_logger(__name__)


class AnsibleGalaxy(base.Base):
    """
    :std:doc:`Galaxy <galaxy/user_guide>` is the default dependency manager.

    Additional options can be passed to ``ansible-galaxy install`` through the
    options dict.  Any option set in this section will override the defaults.

    .. note::

        Molecule will remove any options matching '^[v]+$', and pass ``-vvv``
        to the underlying ``ansible-galaxy`` command when executing
        `molecule --debug`.

    .. code-block:: yaml

        dependency:
          name: galaxy
          options:
            ignore-certs: True
            ignore-errors: True
            role-file: requirements.yml


    The dependency manager can be disabled by setting ``enabled`` to False.

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
    """

    def __init__(self, config):
        """Construct AnsibleGalaxy."""
        super(AnsibleGalaxy, self).__init__(config)
        self._sh_command = None

        self.command = 'ansible-galaxy'

    @property
    def default_options(self):
        d = {
            'force': True,
            'role-file': os.path.join(
                self._config.scenario.directory, 'requirements.yml'
            ),
            'roles-path': os.path.join(
                self._config.scenario.ephemeral_directory, 'roles'
            ),
        }
        if self._config.debug:
            d['vvv'] = True

        return d

    # NOTE(retr0h): Override the base classes' options() to handle
    # ``ansible-galaxy`` one-off.
    @property
    def options(self):
        o = self._config.config['dependency']['options']
        # NOTE(retr0h): Remove verbose options added by the user while in
        # debug.
        if self._config.debug:
            o = util.filter_verbose_permutation(o)

        return util.merge_dicts(self.default_options, o)

    @property
    def default_env(self):
        return util.merge_dicts(os.environ, self._config.env)

    def bake(self):
        """
        Bake an ``ansible-galaxy`` command so it's ready to execute and returns \
        None.

        :return: None
        """
        options = self.options
        verbose_flag = util.verbose_flag(options)

        self._sh_command = getattr(sh, self.command)
        self._sh_command = self._sh_command.bake(
            'install',
            options,
            *verbose_flag,
            _env=self.env,
            _out=LOG.out,
            _err=LOG.error
        )

    def execute(self):
        if not self.enabled:
            msg = 'Skipping, dependency is disabled.'
            LOG.warn(msg)
            return

        if not self._has_requirements_file():
            msg = 'Skipping, missing the requirements file.'
            LOG.warn(msg)
            return

        if self._sh_command is None:
            self.bake()

        self._setup()
        self.execute_with_retries()

    def _setup(self):
        """
        Prepare the system for using ``ansible-galaxy`` and returns None.

        :return: None
        """
        role_directory = os.path.join(
            self._config.scenario.directory, self.options['roles-path']
        )
        if not os.path.isdir(role_directory):
            os.makedirs(role_directory)

    def _role_file(self):
        return self.options.get('role-file')

    def _has_requirements_file(self):
        return os.path.isfile(self._role_file())

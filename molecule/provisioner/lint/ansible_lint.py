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
from molecule.provisioner.lint import base

LOG = logger.get_logger(__name__)


class AnsibleLint(base.Base):
    """
    `Ansible Lint`_ is the default role linter.

    `Ansible Lint`_ checks playbooks for practices, and behaviour that could
    potentially be improved.

    Additional options can be passed to `ansible-lint` through the options
    dict.  Any option set in this section will override the defaults.

    .. code-block:: yaml

        provisioner:
          name: ansible
          lint:
            name: ansible-lint
            options:
              exclude:
                - path/exclude1
                - path/exclude2
              x:
                - ANSIBLE0011
                - ANSIBLE0012
              force-color: True

    The role linting can be disabled by setting `enabled` to False.

    .. code-block:: yaml

        provisioner:
          name: ansible
          lint:
            name: ansible-lint
            enabled: False

    Environment variables can be passed to lint.

    .. code-block:: yaml

        provisioner:
          name: ansible
          lint:
            name: ansible-lint
            env:
              FOO: bar

    .. _`Ansible Lint`: https://github.com/willthames/ansible-lint
    """

    def __init__(self, config):
        """
        Sets up the requirements to execute `ansible-lint` and returns None.

        :param config: An instance of a Molecule config.
        :return: None
        """
        super(AnsibleLint, self).__init__(config)
        self._ansible_lint_command = None

    @property
    def default_options(self):
        d = {
            'default_exclude': [self._config.scenario.ephemeral_directory],
            'exclude': [],
            'x': [],
        }
        if self._config.debug:
            d['v'] = True

        return d

    @property
    def default_env(self):
        env = self._config.merge_dicts(os.environ.copy(), self._config.env)
        env = self._config.merge_dicts(env, self._config.provisioner.env)

        return env

    def bake(self):
        """
        Bake an `ansible-lint` command so it's ready to execute and returns
        None.

        :return: None
        """
        options = self.options
        default_exclude_list = options.pop('default_exclude')
        options_exclude_list = options.pop('exclude')
        excludes = default_exclude_list + options_exclude_list
        x_list = options.pop('x')

        exclude_args = ['--exclude={}'.format(exclude) for exclude in excludes]
        x_args = tuple(('-x', x) for x in x_list)
        self._ansible_lint_command = sh.ansible_lint.bake(
            options,
            exclude_args,
            sum(x_args, ()),
            self._config.provisioner.playbooks.converge,
            _env=self.env,
            _out=LOG.out,
            _err=LOG.error)

    def execute(self):
        if not self.enabled:
            msg = 'Skipping, lint is disabled.'
            LOG.warn(msg)
            return

        if self._ansible_lint_command is None:
            self.bake()

        msg = 'Executing Ansible Lint on {}...'.format(
            self._config.provisioner.playbooks.converge)
        LOG.info(msg)

        try:
            util.run_command(
                self._ansible_lint_command, debug=self._config.debug)
            msg = 'Lint completed successfully.'
            LOG.success(msg)
        except sh.ErrorReturnCode as e:
            util.sysexit(e.exit_code)

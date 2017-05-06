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


class Gilt(base.Base):
    """
    `Gilt`_ is an alternate dependency manager.

    Additional options can be passed to `gilt overlay` through the options
    dict.  Any option set in this section will override the defaults.

    .. code-block:: yaml

        dependency:
          name: gilt
          options:
            debug: True


    The dependency manager can be disabled by setting `enabled` to False.

    .. code-block:: yaml

        dependency:
          name: gilt
          enabled: False

    Environment variables can be passed to the dependency.

    .. code-block:: yaml

        dependency:
          name: gilt
          env:
            FOO: bar

    .. _`Gilt`: http://gilt.readthedocs.io
    """

    def __init__(self, config):
        super(Gilt, self).__init__(config)
        self._gilt_command = None

    @property
    def default_options(self):
        """
        Default CLI arguments provided to `gilt` and returns a dict.

        :return: dict
        """
        config = os.path.join(self._config.scenario.directory, 'gilt.yml')
        d = {'config': config}
        if self._config.args.get('debug'):
            d['debug'] = True

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
        Bake a `gilt` command so it's ready to execute and returns None.

        :return: None
        """
        self._gilt_command = sh.gilt.bake(
            self.options,
            'overlay',
            _env=self.env,
            _out=LOG.out,
            _err=LOG.error)

    def execute(self):
        """
        Executes `gilt` and returns None.

        :return: None
        """
        if not self.enabled:
            LOG.warn('Skipping, dependency is disabled.')
            return

        if not self._has_requirements_file():
            LOG.warn('Skipping, missing the requirements file.')
            return

        if self._gilt_command is None:
            self.bake()

        try:
            util.run_command(
                self._gilt_command, debug=self._config.args.get('debug'))
            LOG.success('Dependency completed successfully.')
        except sh.ErrorReturnCode as e:
            util.sysexit(e.exit_code)

    def _has_requirements_file(self):
        config_file = self.options.get('config')

        return config_file and os.path.isfile(config_file)

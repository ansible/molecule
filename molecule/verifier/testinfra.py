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
from molecule.verifier import base
from molecule.verifier import flake8

LOG = logger.get_logger(__name__)


class Testinfra(base.Base):
    """
    `Testinfra`_ is the default test runner.

    Additional options can be passed to `testinfra` through the options
    dict.  Any option set in this section will override the defaults.

    .. code-block:: yaml

        verifier:
          name: testinfra
          options:
            n: 1

    The testing can be disabled by setting `enabled` to False.

    .. code-block:: yaml

        verifier:
          name: testinfra
          enabled: False

    Environment variables can be passed to the verifier.

    .. code-block:: yaml

        verifier:
          name: testinfra
          env:
            FOO: bar

    .. _`Testinfra`: http://testinfra.readthedocs.io
    """

    def __init__(self, config):
        """
        Sets up the requirements to execute `testinfra` and returns None.

        :param config: An instance of a Molecule config.
        :return: None
        """
        super(Testinfra, self).__init__(config)
        self._testinfra_command = None
        self._tests = self._get_tests()

    @property
    def default_options(self):
        """
        Default CLI arguments provided to `testinfra` and returns a dict.

        :return: dict
        """
        d = self._config.driver.testinfra_options
        if self._config.args.get('debug'):
            d['debug'] = True
        if self._config.args.get('sudo'):
            d['sudo'] = True

        return d

    @property
    def default_env(self):
        """
        Default env variables provided to `testinfra` and returns a
        dict.

        :return: dict
        """
        return os.environ.copy()

    def bake(self):
        """
        Bake a `testinfra` command so it's ready to execute and returns None.

        :return: None
        """

        options = self.options
        verbose_flag = util.verbose_flag(options)

        self._testinfra_command = sh.testinfra.bake(
            options,
            self._tests,
            *verbose_flag,
            _cwd=self._config.scenario.directory,
            _env=self.env,
            _out=LOG.out,
            _err=LOG.error)

    def execute(self):
        """
        Executes `testinfra` and returns None.

        :return: None
        """
        if not self.enabled:
            LOG.warn('Skipping, verifier is disabled.')
            return

        if not len(self._tests) > 0:
            LOG.warn('Skipping, no tests found.')
            return

        if self._testinfra_command is None:
            self.bake()

        f = flake8.Flake8(self._config)
        f.execute()

        msg = 'Executing testinfra tests found in {}/...'.format(
            self.directory)
        LOG.info(msg)

        try:
            util.run_command(
                self._testinfra_command, debug=self._config.args.get('debug'))
            LOG.success('Verifier completed successfully.')

        except sh.ErrorReturnCode as e:
            util.sysexit(e.exit_code)

    def _get_tests(self):
        """
        Walk the verifier's directory for tests and returns a list.

        :return: list
        """
        return [
            filename for filename in util.os_walk(self.directory, 'test_*.py')
        ]

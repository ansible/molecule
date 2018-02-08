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

import glob
import os

import sh

from molecule import logger
from molecule import util
from molecule.verifier import base

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

    Change path to the test directory.

    .. code-block:: yaml

        verifier:
          name: testinfra
          directory: /foo/bar/

    Additional tests from another file or directory relative to the scenario's
    tests directory (supports regexp).

    .. code-block:: yaml

        verifier:
          name: testinfra
          additional_files_or_dirs:
            - ../path/to/test_1.py
            - ../path/to/test_2.py
            - ../path/to/directory/*

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
        if config:
            self._tests = self._get_tests()

    @property
    def name(self):
        return 'testinfra'

    @property
    def default_options(self):
        d = self._config.driver.testinfra_options
        if self._config.debug:
            d['debug'] = True
        if self._config.args.get('sudo'):
            d['sudo'] = True

        return d

    @property
    def default_env(self):
        env = self._config.merge_dicts(os.environ.copy(), self._config.env)
        env = self._config.merge_dicts(env, self._config.provisioner.env)

        return env

    @property
    def additional_files_or_dirs(self):
        files_list = []
        c = self._config.config
        for f in c['verifier']['additional_files_or_dirs']:
            glob_path = os.path.join(self._config.verifier.directory, f)
            glob_list = glob.glob(glob_path)
            if glob_list:
                files_list.extend(glob_list)

        return files_list

    def bake(self):
        """
        Bake a `testinfra` command so it's ready to execute and returns None.

        :return: None
        """

        options = self.options
        verbose_flag = util.verbose_flag(options)
        args = verbose_flag + self.additional_files_or_dirs

        self._testinfra_command = sh.Command('py.test').bake(
            options,
            self._tests,
            *args,
            _cwd=self._config.scenario.directory,
            _env=self.env,
            _out=LOG.out,
            _err=LOG.error)

    def execute(self):
        if not self.enabled:
            msg = 'Skipping, verifier is disabled.'
            LOG.warn(msg)
            return

        if not len(self._tests) > 0:
            msg = 'Skipping, no tests found.'
            LOG.warn(msg)
            return

        if self._testinfra_command is None:
            self.bake()

        msg = 'Executing Testinfra tests found in {}/...'.format(
            self.directory)
        LOG.info(msg)

        try:
            util.run_command(self._testinfra_command, debug=self._config.debug)
            msg = 'Verifier completed successfully.'
            LOG.success(msg)

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

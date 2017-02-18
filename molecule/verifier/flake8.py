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

LOG = logger.get_logger(__name__)


class Flake8(base.Base):
    """
    `Flake8`_ is the default code linter when using the testinfra verifier.
    It cannot be disabled without disabling the Testinfra verifier.

    .. _`Flake8`: http://flake8.pycqa.org/en/latest/
    """

    def __init__(self, config):
        """
        Sets up the requirements to execute `flake8` and returns None.

        :param config: An instance of a Molecule config.
        :return: None
        """
        super(Flake8, self).__init__(config)
        self._flake8_command = None
        if config:
            self._tests = self._get_tests()

    @property
    def name(self):
        return 'testinfra'

    @property
    def default_options(self):
        """
        Default CLI arguments provided to `flake8` and returns a dict.

        :return: dict
        """
        return {}

    def bake(self):
        """
        Bake a `flake8` command so it's ready to execute and returns None.

        :return: None
        """
        self._flake8_command = sh.flake8.bake(
            self.default_options,
            self._tests,
            _env=os.environ,
            _out=LOG.out,
            _err=LOG.error)

    def execute(self):
        """
        Executes `flake8` and returns None.

        :return: None
        """
        if self._flake8_command is None:
            self.bake()

        msg = 'Executing Flake8 on files found in {}/...'.format(
            self.directory)
        LOG.info(msg)

        try:
            util.run_command(
                self._flake8_command, debug=self._config.args.get('debug'))
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

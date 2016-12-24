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

import sh

from molecule import util
from molecule.verifier import base
from molecule.verifier import flake8


class Testinfra(base.Base):
    def __init__(self, config):
        super(Testinfra, self).__init__(config)
        self._testinfra_command = None
        self._tests = self._get_tests()

    @property
    def default_options(self):
        d = self._config.driver.testinfra_options
        if self._config.args.get('debug'):
            d['debug'] = True
        if self._config.args.get('sudo'):
            d['sudo'] = True

        return d

    def bake(self):
        """
        Bake a `testinfra` command so it's ready to execute and returns None.

        :return: None
        """
        self._testinfra_command = sh.testinfra.bake(
            self.options,
            self._tests,
            _cwd=self._config.scenario.directory,
            _env=os.environ,
            _out=util.callback_info,
            _err=util.callback_error)

    def execute(self):
        """
        Executes `testinfra` and returns None.

        :return: None
        """
        if not self.enabled:
            return

        if self._testinfra_command is None:
            self.bake()

        if len(self._tests) > 0:
            f = flake8.Flake8(self._config)
            f.execute()

            msg = 'Executing testinfra tests found in {}/...'.format(
                self.directory)
            util.print_info(msg)

            try:
                util.run_command(
                    self._testinfra_command,
                    debug=self._config.args.get('debug'))
            except sh.ErrorReturnCode as e:
                util.sysexit(e.exit_code)

    def _get_tests(self):
        return [
            filename for filename in util.os_walk(self.directory, 'test_*.py')
        ]

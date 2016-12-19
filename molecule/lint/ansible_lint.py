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
from molecule.lint import base


class AnsibleLint(base.Base):
    def __init__(self, config):
        """
        Sets up the requirements to execute `ansible-lint` and returns None.

        :param config: An instance of a Molecule config.
        :return: None
        """
        super(AnsibleLint, self).__init__(config)
        self._ansible_lint_command = None

    @property
    def options(self):
        return {}

    def bake(self):
        """
        Bake an `ansible-lint` command so it's ready to execute and returns
        None.

        :return: None
        """
        self._ansible_lint_command = sh.ansible_lint.bake(
            self._config.scenario_converge,
            self._config.lint_options,
            _env=os.environ,
            _out=util.callback_info,
            _err=util.callback_error)

    def execute(self):
        """
        Executes `ansible-lint` and returns None.

        :return: None
        """
        if not self._config.lint_enabled:
            return

        if self._ansible_lint_command is None:
            self.bake()

        try:
            util.run_command(
                self._ansible_lint_command,
                debug=self._config.args.get('debug'))
        except sh.ErrorReturnCode as e:
            util.sysexit(e.exit_code)

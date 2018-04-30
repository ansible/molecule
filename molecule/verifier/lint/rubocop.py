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

import os

import sh

from molecule import logger
from molecule import util
from molecule.verifier.lint import base

LOG = logger.get_logger(__name__)


class RuboCop(base.Base):
    """
    `RuboCop`_ is not the default verifier linter.

    `RuboCop`_ is a linter for ruby files.

    Additional options can be passed to `rubocop` through the options
    dict.  Any option set in this section will override the defaults.

    .. code-block:: yaml

        verifier:
          name: inspec
          lint:
            name: rubocop
            options:
              auto-correct: True

    Test file linting can be disabled by setting `enabled` to False.

    .. code-block:: yaml

        verifier:
          name: inspec
          lint:
            name: rubocop
            enabled: False

    Environment variables can be passed to lint.

    .. code-block:: yaml

        verifier:
          name: inspec
          lint:
            name: rubocop
            env:
              FOO: bar

    .. _`RuboCop`: https://rubocop.readthedocs.io/en/latest/
    """

    def __init__(self, config):
        """
        Sets up the requirements to execute `rubocop` and returns None.

        :param config: An instance of a Molecule config.
        :return: None
        """
        super(RuboCop, self).__init__(config)
        self._rubocop_command = None
        if config:
            self._tests = self._get_tests()

    @property
    def default_options(self):
        d = {}
        if self._config.debug:
            d['d'] = True

        return d

    @property
    def default_env(self):
        return util.merge_dicts(os.environ.copy(), self._config.env)

    def bake(self):
        """
        Bake a `rubocop` command so it's ready to execute and returns None.

        :return: None
        """
        self._rubocop_command = sh.rubocop.bake(
            self.options,
            self._tests,
            _env=self.env,
            _out=LOG.out,
            _err=LOG.error)

    def execute(self):
        if not self.enabled:
            msg = 'Skipping, verifier_lint is disabled.'
            LOG.warn(msg)
            return

        if not len(self._tests) > 0:
            msg = 'Skipping, no tests found.'
            LOG.warn(msg)
            return

        if self._rubocop_command is None:
            self.bake()

        msg = 'Executing RuboCop on files found in {}/...'.format(
            self._config.verifier.directory)
        LOG.info(msg)

        try:
            util.run_command(self._rubocop_command, debug=self._config.debug)
            msg = 'Lint completed successfully.'
            LOG.success(msg)
        except sh.ErrorReturnCode as e:
            util.sysexit(e.exit_code)

    def _get_tests(self):
        """
        Walk the verifier's directory for tests and returns a list.

        :return: list
        """
        return [
            filename for filename in util.os_walk(
                self._config.verifier.directory, 'test_*.rb')
        ]

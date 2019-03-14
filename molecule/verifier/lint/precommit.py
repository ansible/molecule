#  Copyright (c) 2019 Red Hat, Inc.
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
"""Linter module for pre-commit related code."""

import os

import sh

from molecule import logger
from molecule import util
from molecule.verifier.lint import base

LOG = logger.get_logger(__name__)


class PreCommit(base.Base):
    """
    Pre-commit linter class.

    This class is used to lint files by executing the pre-commit
    command line tool for linting files.

    `Pre-Commit`_ is not the default verifier linter.

    `Pre-Commit`_ is a linter for python files and more.

    Additional options can be passed to ``pre-commit`` through the options
    dict.  Any option set in this section will override the defaults.

    .. code-block:: yaml

        verifier:
          name: testinfra
          lint:
            name: pre-commit
            options:
              remove-tabs:

    Test file linting can be disabled by setting ``enabled`` to False.

    .. code-block:: yaml

        verifier:
          name: testinfra
          lint:
            name: pre-commit
            enabled: False

    Environment variables can be passed to lint.

    .. code-block:: yaml

        verifier:
          name: testinfra
          lint:
            name: pre-commit
            env:
              FOO: bar

    .. _`Pre-Commit`: https://pre-commit.com/
    """

    def __init__(self, config):
        """
        Set up the requirements to execute `pre-commit` tool.

        :param config: An instance of a Molecule config.
        """
        super(PreCommit, self).__init__(config)
        self._precommit_command = None
        if config:
            self._tests = self._get_tests()

    @property
    def default_options(self):
        """Default options for pre-commit tool runtime."""
        return {}

    @property
    def default_env(self):
        """Default environment variables for pre-commit tool runtime."""
        return util.merge_dicts(os.environ.copy(), self._config.env)

    def bake(self):
        """Bake a ready to execute ``pre-commit`` command."""
        self._precommit_command = sh.Command('pre-commit').bake(
            'run',
            self.options,
            '--files',
            self._tests,
            _env=self.env,
            _out=LOG.out,
            _err=LOG.error)

    def execute(self):
        """Execute the pre-commit command."""
        if not self.enabled:
            msg = 'Skipping, verifier_lint is disabled.'
            LOG.warn(msg)
            return

        if not self._tests:
            msg = 'Skipping, no tests found.'
            LOG.warn(msg)
            return

        if self._precommit_command is None:
            self.bake()

        msg = 'Executing pre-commit on files found in {}/...'.format(
            self._config.verifier.directory)
        LOG.info(msg)

        try:
            util.run_command(self._precommit_command, debug=self._config.debug)
            msg = 'Lint completed successfully.'
            LOG.success(msg)
        except sh.ErrorReturnCode as e:
            util.sysexit(e.exit_code)

    def _get_tests(self):
        """
        Get a list of test files from the verifier's directory.

        :return: list
        """
        return list(util.os_walk(self._config.verifier.directory, 'test_*.py'))

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
from molecule.lint import base

LOG = logger.get_logger(__name__)


class Yamllint(base.Base):
    """
    `Yamllint`_ is the default projet linter.

    `Yamllint`_ is a linter for YAML files.  In addition to checking for syntax
    validity, also checks for key repetition, and cosmetic problems such as
    lines length, trailing spaces, and indentation.

    Additional options can be passed to `yamllint` through the options
    dict.  Any option set in this section will override the defaults.

    .. code-block:: yaml

        lint:
          name: yamllint
          options:
            config-file: foo/bar

    The project linting can be disabled by setting `enabled` to False.

    .. code-block:: yaml

        lint:
          name: yamllint
          enabled: False

    Environment variables can be passed to lint.

    .. code-block:: yaml

        lint:
          name: yamllint
          env:
            FOO: bar

    .. _`Yamllint`: https://github.com/adrienverge/yamllint
    """

    def __init__(self, config):
        """
        Sets up the requirements to execute `yamllint` and returns None.

        :param config: An instance of a Molecule config.
        :return: None
        """
        super(Yamllint, self).__init__(config)
        self._yamllint_command = None
        self._files = self._get_files()

    @property
    def default_options(self):
        return {}

    @property
    def default_env(self):
        return self._config.merge_dicts(os.environ.copy(), self._config.env)

    def bake(self):
        """
        Bake a `yamllint` command so it's ready to execute and returns None.

        :return: None
        """
        self._yamllint_command = sh.yamllint.bake(
            self.options,
            self._files,
            _env=self.env,
            _out=LOG.out,
            _err=LOG.error)

    def execute(self):
        if not self.enabled:
            msg = 'Skipping, lint is disabled.'
            LOG.warn(msg)
            return

        if self._yamllint_command is None:
            self.bake()

        msg = 'Executing Yamllint on files found in {}/...'.format(
            self._config.project_directory)
        LOG.info(msg)

        try:
            util.run_command(self._yamllint_command, debug=self._config.debug)
            msg = 'Lint completed successfully.'
            LOG.success(msg)
        except sh.ErrorReturnCode as e:
            util.sysexit(e.exit_code)

    def _get_files(self):
        """
        Walk the project directory for tests and returns a list.

        :return: list
        """
        excludes = [
            '.tox',
            '.git',
            '.vagrant',
            '.molecule',
        ]
        generators = [
            util.os_walk(self._config.project_directory, '*.yml', excludes),
            util.os_walk(self._config.project_directory, '*.yaml', excludes),
        ]

        return [f for g in generators for f in g]

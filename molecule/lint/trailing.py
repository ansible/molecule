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
import re

from molecule import logger
from molecule import util
from molecule.lint import base

LOG = logger.get_logger(__name__)


class Trailing(base.Base):
    """
    A linter which scans selected source files for trailing issues.  This
    linter `cannot` be disabled.
    """

    def __init__(self, config):
        """
        Sets up the requirements to execute `trailing whitespace` and returns
        None.

        :param config: An instance of a Molecule config.
        :return: None
        """
        super(Trailing, self).__init__(config)
        self._tests = self._get_tests()

    @property
    def default_options(self):
        return {}

    @property
    def default_env(self):
        return self._config.merge_dicts(os.environ.copy(), self._config.env)

    @property
    def default_ignore_paths(self):
        return []

    def execute(self):
        for f in self._tests:
            with util.open_file(f) as stream:
                data = [line for line in stream]
                newline = self._get_trailing_newline(data)
                whitespace = self._get_trailing_whitespace(data)

            if newline:
                msg = 'Trailing newline found at the end of {}.'.format(f)
                util.sysexit_with_message(msg)

            if len(whitespace) > 0:
                lines = ', '.join(str(x) for x in whitespace)
                msg = ('Trailing whitespace found in {} '
                       'on lines: {}').format(f, lines)
                util.sysexit_with_message(msg)

    def _get_trailing_newline(self, source):
        """
        Checks last item in source list for a trailing newline and returns
        a bool.

        :param source: A list of strings to check for trailing newline(s).
        :return: bool
        """
        if re.match(r'^\n$', source[-1]):
            return True
        return False

    def _get_trailing_whitespace(self, source):
        """
        Checks each item in source list for a trailing whitespace and returns
        a list.

        :param source: A list of lines to check for trailing whitespace.
        :return: list
        """
        lines = []
        for counter, line in enumerate(source):
            l = line.rstrip('\n\r')
            if re.search(r'\s+$', l):
                lines.append(counter + 1)

        if lines:
            return lines
        return []

    def _get_tests(self):
        """
        Walk the source for desired files and returns a list.

        :return: list
        """
        generators = [
            util.os_walk(self._config.project_directory, '*.py'),
            util.os_walk(self._config.project_directory, '*.yml'),
            util.os_walk(self._config.project_directory, '*.yaml'),
        ]

        return [
            f for g in generators for f in g
            if not any(ignore in f for ignore in self.ignore_paths)
        ]

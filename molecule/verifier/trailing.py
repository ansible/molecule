#  Copyright (c) 2015-2016 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

import os
import re

from molecule import util
from molecule.verifier import base

LOG = util.get_logger(__name__)


class Trailing(base.Base):
    def __init__(self, molecule):
        super(Trailing, self).__init__(molecule)
        self._ignore_paths = molecule.config.config['molecule']['ignore_paths']

    def execute(self, exit=True):
        """
        Recursively finds all files relative to CWD, and checks them for
        trailing whitespace and newlines.

        :param ignore_paths: List of paths to ignore during checks.
        :return: A ``sys.exit`` code if found an error, otherwise None.
        """
        filenames = []
        pruned_filenames = []
        found_error = False
        valid_extensions = ['py', 'yml', 'rb']
        for root, dirs, files in os.walk('.'):
            # gets ./subdirectory/filename
            filenames.extend(
                [os.path.join(root, name) for name in files
                 if name.split(os.extsep)[-1] in valid_extensions])
            # gets ./filename
            filenames.extend(
                [os.path.join(root, name) for name in dirs
                 if name.split(os.extsep)[-1] in valid_extensions])

        # only work on files not in our ignore paths
        for f in filenames:
            f_parts = f.split(os.sep)

            try:
                if f_parts[1] in self._ignore_paths:
                    continue
            except IndexError:
                continue

            # don't add directories
            if os.path.isfile(f):
                pruned_filenames.append(f)

        for filename in pruned_filenames:
            # don't process blank files
            if os.path.getsize(filename) < 1:
                continue

            data = [line for line in open(filename, 'r')]
            newline = self._trailing_newline(data)
            whitespace = self._trailing_whitespace(data)

            if newline:
                msg = 'Trailing newline found at the end of {}'
                LOG.error(msg.format(filename))
                found_error = True

            if whitespace:
                msg = 'Trailing whitespace found in {} on lines: {}'
                lines = ', '.join(str(x) for x in whitespace)
                LOG.error(msg.format(filename,
                                     lines, ))
                found_error = True

        if exit and found_error:
            util.sysexit()

    def _trailing_newline(self, source):
        """
        Checks last item in source list for a trailing newline.

        :param source: list to check for trailing newline
        :return: True if a trailing newline is found, otherwise None
        """
        if re.match(r'^\n$', source[-1]):
            return True
        return

    def _trailing_whitespace(self, source):
        """
        Checks each item in source list for a trailing whitespace.

        :param source: list of lines to check for trailing whitespace
        :return: List of offending line numbers with trailing whitespace,
                 otherwise None
        """
        lines = []
        for counter, line in enumerate(source):
            l = line.rstrip('\n\r')
            if re.search(r'\s+$', l):
                lines.append(counter + 1)

        return lines if lines else None

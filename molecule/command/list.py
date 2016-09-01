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

from molecule.command import base


class List(base.Base):
    """
    Prints a list of currently available platforms

    Usage:
        list [--debug] ([-m]|[--porcelain])

    Options:
        --debug         get more detail
        -m              synonym for '--porcelain' (deprecated)
        --porcelain     machine readable output
    """

    def execute(self, exit=True):
        """
        Execute the actions necessary to perform a `molecule list` and
        return a tuple.

        :param exit: (Unused) Provided to complete method signature.
        :return: Return a tuple of None.
        """
        porcelain = self.molecule.args['-m'] or self.molecule.args[
            '--porcelain']
        self.molecule._print_valid_platforms(porcelain=porcelain)
        return None, None

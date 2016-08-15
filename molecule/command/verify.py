#  Copyright (c) 2015-2016 Cisco Systems
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

import sh

from molecule import utilities
from molecule import validators
from molecule.command import base

LOG = utilities.get_logger(__name__)


class Verify(base.Base):
    """
    Performs verification steps on running instances.

    Usage:
        verify [--platform=<platform>] [--provider=<provider>] [--debug] [--sudo]

    Options:
        --platform=<platform>  specify a platform
        --provider=<provider>  specify a provider
        --debug                get more detail
        --sudo                 runs tests with sudo
    """

    def execute(self, exit=True):
        tw = trailing.Trailing(self.molecule)
        tw.execute()

        self.molecule._write_ssh_config()

        try:
            ti = testinfra.Testinfra(self.molecule)
            ti.execute()

            ss = serverspec.Serverspec(self.molecule)
            ss.execute()
        except sh.ErrorReturnCode as e:
            LOG.error('ERROR: {}'.format(e))
            if exit:
                utilities.sysexit(e.exit_code)
            return e.exit_code, e.stdout

        return None, None

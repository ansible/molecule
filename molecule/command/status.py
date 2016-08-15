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

import subprocess

from molecule import util
from molecule.command import base

LOG = util.get_logger(__name__)


class Status(base.Base):
    """
    Prints status of configured instances.

    Usage:
        status [--debug][--porcelain] ([--hosts] [--platforms][--providers])

    Options:
        --debug         get more detail
        --porcelain     machine readable output
        --hosts         display the available hosts
        --platforms     display the available platforms
        --providers     display the available providers
    """

    def execute(self):
        display_all = not any([self.args['--hosts'], self.args['--platforms'],
                               self.args['--providers']])

        # Retrieve the status.
        try:
            status = self.molecule._driver.status()
        except subprocess.CalledProcessError as e:
            LOG.error(e.message)
            return e.returncode, e.message

        # Display the results in procelain mode.
        porcelain = self.molecule._args['--porcelain']

        # Display hosts information.
        if display_all or self.molecule._args['--hosts']:

            # Prepare the table for the results.
            headers = [] if porcelain else ['Name', 'State', 'Provider']
            data = []

            for item in status:
                if item.state != 'not_created':
                    state = item.state
                else:
                    state = item.state

                data.append([item.name, state, item.provider])

            self.molecule._display_tabulate_data(data, headers=headers)

        # Display the platforms.
        if display_all or self.molecule._args['--platforms']:
            self.molecule._print_valid_platforms(porcelain=porcelain)

        # Display the providers.
        if display_all or self.molecule._args['--providers']:
            self.molecule._print_valid_providers(porcelain=porcelain)

        return None, None

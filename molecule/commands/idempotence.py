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

from molecule import utilities
from molecule.commands import base
from molecule.commands import converge


class Idempotence(base.BaseCommand):
    """
    Provisions instances and parses output to determine idempotence.

    Usage:
        idempotence [--platform=<platform>] [--provider=<provider>] [--debug]

    Options:
        --platform=<platform>  specify a platform
        --provider=<provider>  specify a provide
        --debug                get more detail
    """

    def execute(self, exit=True):
        if self.static:
            self.disabled('idempotence')

        utilities.print_info(
            'Idempotence test in progress (can take a few minutes)...')

        c = converge.Converge(self.command_args, self.args, self.molecule)
        status, output = c.execute(idempotent=True,
                                   exit=False,
                                   hide_errors=True)
        if status is not None:
            msg = 'Skipping due to errors during converge.\n'
            utilities.print_info(msg)
            return status, None

        idempotent, changed_tasks = self.molecule._parse_provisioning_output(
            output)

        if idempotent:
            utilities.print_success('Idempotence test passed.')
            return None, None

        # Display the details of the idempotence test.
        if changed_tasks:
            utilities.logger.error(
                'Idempotence test failed because of the following tasks:')
            utilities.logger.error('{}'.format('\n'.join(changed_tasks)))
        else:
            # But in case the idempotence callback plugin was not found, we just display an error message.
            utilities.logger.error('Idempotence test failed.')
            warning_msg = "The idempotence plugin was not found or did not provide the required information. " \
                          "Therefore the failure details cannot be displayed."

            utilities.logger.warning(warning_msg)
        if exit:
            utilities.sysexit()
        return 1, None

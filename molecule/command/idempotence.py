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

import re

import click

from molecule import util
from molecule.command import base
from molecule.command import converge

LOG = util.get_logger(__name__)


class Idempotence(base.Base):
    def execute(self, exit=True):
        """
        Execute the actions necessary to perform a `molecule idempotence` and
        return a tuple.

        :param exit: An optional flag to toggle the exiting of the module
         on command failure.
        :return: Return a tuple of (`exit status`, `command output`), otherwise
         sys.exit on command failure.
        """
        util.print_info(
            'Idempotence test in progress (can take a few minutes) ...')

        c = converge.Converge(self.command_args, self.args, self.molecule)
        status, output = c.execute(
            idempotent=True, exit=False, hide_errors=True)
        if status is not None:
            msg = 'Skipping due to errors during converge.'
            util.print_info(msg)
            return status, None

        idempotent = self._is_idempotent(output)
        if idempotent:
            util.print_success('Idempotence test passed.')
            return None, None
        else:
            LOG.error('Idempotence test failed.')
            if exit:
                util.sysexit()

            return 1, None

    def _is_idempotent(self, output):
        """
        Parses the output of the provisioning for changed, and return a bool.

        :param output: A string containing the output of the ansible run.
        :return: bool
        """

        # Remove blank lines to make regex matches easier
        output = re.sub("\n\s*\n*", "\n", output)

        # Look for any non-zero changed lines
        changed = re.search(r'(changed=[1-9][0-9]*)', output)

        if changed:
            # Not idempotent
            return False

        return True


@click.command()
@click.option('--platform', default=None, help='Specify a platform.')
@click.option('--provider', default=None, help='Specify a provider.')
@click.pass_context
def idempotence(ctx, platform, provider):  # pragma: no cover
    """ Provisions instances and parses output to determine idempotence. """
    command_args = {'platform': platform, 'provider': provider}

    i = Idempotence(ctx.obj.get('args'), command_args)
    i.execute
    util.sysexit(i.execute()[0])

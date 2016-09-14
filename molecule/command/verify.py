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

import click
import sh

from molecule import util
from molecule.command import base
from molecule.verifier import ansible_lint
from molecule.verifier import goss
from molecule.verifier import serverspec
from molecule.verifier import testinfra
from molecule.verifier import trailing

LOG = util.get_logger(__name__)


class Verify(base.Base):
    def execute(self, exit=True):
        """
        Execute the actions necessary to perform a `molecule verify` and
        return a tuple.

        :param exit: An optional flag to toggle the exiting of the module
         on command failure.
        :return: Return a tuple of None, otherwise sys.exit on command failure.
        """
        for v in [ansible_lint.AnsibleLint(self.molecule),
                  trailing.Trailing(self.molecule)]:
            v.execute()

        self.molecule.write_ssh_config()

        try:
            if self.molecule.verifier == 'serverspec':
                v = serverspec.Serverspec(self.molecule)
            elif self.molecule.verifier == 'goss':
                v = goss.Goss(self.molecule)
            else:
                v = testinfra.Testinfra(self.molecule)

            v.execute()
        except sh.ErrorReturnCode as e:
            LOG.error('ERROR: {}'.format(e))
            if exit:
                util.sysexit(e.exit_code)
            return e.exit_code, e.stdout

        return None, None


@click.command()
@click.option('--platform', default=None, help='Specify a platform.')
@click.option('--provider', default=None, help='Specify a provider.')
@click.option(
    '--sudo/--no-sudo',
    default=False,
    help='Enable or disable running tests with sudo. Default is disabled.')
@click.pass_context
def verify(ctx, platform, provider, sudo):  # pragma: no cover
    """ Performs verification steps on running instances. """
    command_args = {'platform': platform, 'provider': provider, 'sudo': sudo}

    v = Verify(ctx.obj.get('args'), command_args)
    v.execute
    util.sysexit(v.execute()[0])

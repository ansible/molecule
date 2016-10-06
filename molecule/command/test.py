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

import click

import molecule.command  # prevent circular dependencies
from molecule import util
from molecule.command import base

LOG = util.get_logger(__name__)


class Test(base.Base):
    def execute(self, exit=True):
        """
        Execute the actions necessary to perform a `molecule test` and
        return a tuple.

        :param exit: (Unused) Provided to complete method signature.
        :return: Return a tuple of (`exit status`, `command output`), otherwise
         sys.exit on command failure.
        """
        for task in self.molecule.config.config['molecule']['test'][
                'sequence']:
            command_module = getattr(molecule.command, task)
            command = getattr(command_module, task.capitalize())
            c = command(self.command_args, self.args, self.molecule)

            status, output = c.execute(exit=False)

            # Fail fast
            if status is not 0 and status is not None:
                if output:
                    LOG.error(output)
                util.sysexit(status)

        if self.command_args.get('destroy') == 'always':
            c = molecule.command.destroy.Destroy(self.command_args, self.args)
            c.execute()
            return None, None

        if self.command_args.get('destroy') == 'never':
            return None, None

        # passing (default)
        if status is None:
            c = molecule.command.destroy.Destroy(self.command_args, self.args)
            c.execute()
            return None, None


@click.command()
@click.option('--driver', default=None, help='Specificy a driver.')
@click.option('--platform', default=None, help='Specify a platform.')
@click.option('--provider', default=None, help='Specify a provider.')
@click.option(
    '--destroy',
    type=click.Choice(['passing', 'always', 'never']),
    default=None,
    help='Destroy behavior.')
@click.option(
    '--sudo/--no-sudo',
    default=False,
    help='Enable or disable running tests with sudo. Default is disabled.')
@click.pass_context
def test(ctx, driver, platform, provider, destroy, sudo):  # pragma: no cover
    """
    Runs a series of commands (defined in config) against instances for a full
    test/verify run.
    """
    command_args = {'driver': driver,
                    'platform': platform,
                    'provider': provider,
                    'destroy': destroy,
                    'sudo': sudo}

    t = Test(ctx.obj.get('args'), command_args)
    t.execute
    util.sysexit(t.execute()[0])

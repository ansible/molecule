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

import subprocess

import click

from molecule import util
from molecule.command import base

LOG = util.get_logger(__name__)


class Status(base.Base):
    def execute(self, exit=True):
        """
        Execute the actions necessary to perform a `molecule status` and
        return a tuple.

        :param exit: (Unused) Provided to complete method signature.
        :return: Return a tuple of None.
        """
        display_all = not any([self.command_args.get('hosts'),
                               self.command_args.get('platforms'),
                               self.command_args.get('providers')])

        # Retrieve the status.
        try:
            status = self.molecule.driver.status()
        # TODO(retr0h): Pretty sure this handling is wrong.  We don't always
        # shell out for status.
        except subprocess.CalledProcessError as e:
            LOG.error(e.message)
            return e.returncode, e.message

        # Display the results in procelain mode.
        porcelain = self.command_args.get('porcelain')

        # Display hosts information.
        if display_all or self.command_args.get('hosts'):
            # Prepare the table for the results.
            headers = [] if porcelain else ['Name', 'State', 'Provider']
            data = []

            for item in status:
                if item.state != 'not_created':  # pragma: no cover
                    state = item.state
                else:
                    state = item.state

                data.append([item.name, state, item.provider])

            self.molecule.display_tabulate_data(data, headers=headers)

        # Display the platforms.
        if display_all or self.command_args.get('platforms'):
            self.molecule.print_valid_platforms(porcelain=porcelain)

        # Display the providers.
        if display_all or self.command_args.get('providers'):
            self.molecule.print_valid_providers(porcelain=porcelain)

        return None, None


@click.command()
@click.option(
    '--platforms/--no-platforms',
    default=False,
    help='Enable or disable displaying only platforms. Default is disabled.')
@click.option(
    '--providers/--no-providers',
    default=False,
    help='Enable or disable displaying only providers. Default is disabled.')
@click.option(
    '--hosts/--no-hosts',
    default=False,
    help='Enable or disable displaying only hosts. Default is disabled.')
@click.option(
    '--porcelain/--no-porcelain',
    default=False,
    help='Machine readable output.  Default is disabled.')
@click.pass_context
def status(ctx, platforms, providers, hosts, porcelain):  # pragma: no cover
    """ Prints status of configured instances. """
    command_args = {'platforms': platforms,
                    'providers': providers,
                    'hosts': hosts,
                    'porcelain': porcelain}

    s = Status(ctx.obj.get('args'), command_args)
    s.execute
    util.sysexit(s.execute()[0])

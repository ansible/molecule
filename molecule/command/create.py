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
import subprocess

from molecule import util
from molecule.command import base

LOG = util.get_logger(__name__)


class Create(base.Base):
    def execute(self, exit=True):
        """
        Execute the actions necessary to perform a `molecule create` and
        return a tuple.

        :param exit: An optional flag to toggle the exiting of the module
         on command failure.
        :return: Return a tuple of None, otherwise sys.exit on command failure.
        """
        self.molecule.remove_inventory_file()
        self.molecule.create_templates()
        try:
            util.print_info('Creating instances ...')
            self.molecule.driver.up(no_provision=True)
            self.molecule.state.change_state('created', True)
            if self.command_args.get('platform') == 'all':
                self.molecule.state.change_state('multiple_platforms', True)
        except subprocess.CalledProcessError as e:
            LOG.error('ERROR: {}'.format(e))
            if exit:
                util.sysexit(e.returncode)
            return e.returncode, e.message
        self.molecule.create_inventory_file()
        self.molecule.write_instances_state()
        return None, None


@click.command()
@click.option('--driver', default=None, help='Specificy a driver.')
@click.option('--platform', default=None, help='Specify a platform.')
@click.option('--provider', default=None, help='Specify a provider.')
@click.pass_context
def create(ctx, driver, platform, provider):  # pragma: no cover
    """ Creates all instances defined in molecule.yml. """
    command_args = {
        'driver': driver,
        'platform': platform,
        'provider': provider
    }

    c = Create(ctx.obj.get('args'), command_args)
    c.execute
    util.sysexit(c.execute()[0])

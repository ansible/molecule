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


class Destroy(base.Base):
    def execute(self, exit=True):
        """
        Execute the actions necessary to perform a `molecule destroy` and
        return a tuple.

        Clears state file of all info (default platform).

        :param exit: An optional flag to toggle the exiting of the module
         on command failure.
        :return: Return a tuple of None, otherwise sys.exit on command failure.
        """
        try:
            util.print_info('Destroying instances...')
            self.molecule.driver.destroy()
            self.molecule.state.reset()
        except subprocess.CalledProcessError as e:
            util.print_error(str(e))
            if exit:
                util.sysexit(e.returncode)
            return e.returncode, e.message
        self.molecule.remove_templates()
        self.molecule.remove_inventory_file()
        self.molecule.remove_vars_files()
        return None, None


@click.command()
@click.option('--driver', default=None, help='Specificy a driver.')
@click.option('--platform', default=None, help='Specify a platform.')
@click.option('--provider', default=None, help='Specify a provider.')
@click.pass_context
def destroy(ctx, driver, platform, provider):  # pragma: no cover
    """ Destroys all instances created by molecule. """
    command_args = {
        'driver': driver,
        'platform': platform,
        'provider': provider
    }

    d = Destroy(ctx.obj.get('args'), command_args)
    d.execute
    util.sysexit(d.execute()[0])

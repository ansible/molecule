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

import os

import click

from molecule import util
from molecule.command import base


class Destroy(base.Base):
    def execute(self):
        """
        Execute the actions necessary to perform a `molecule destroy` and
        returns None.

        :return: None
        """
        msg = "Scenario: [{}]".format(self._config.scenario_name)
        util.print_info(msg)
        msg = "Provisioner: [{}]".format(self._config.provisioner_name)
        util.print_info(msg)
        msg = "Playbook: [{}]".format(
            os.path.basename(self._config.scenario_teardown))
        util.print_info(msg)

        self._config.provisioner.converge(self._config.inventory_file,
                                          self._config.scenario_teardown)


@click.command()
@click.pass_context
def destroy(ctx):  # pragma: no cover
    """ Destroy instances. """
    args = ctx.obj.get('args')
    command_args = {}

    for config in base.get_configs(args, command_args):
        d = Destroy(config)
        d.execute()

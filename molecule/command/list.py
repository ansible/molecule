#  Copyright (c) 2015-2017 Cisco Systems, Inc.
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

from __future__ import print_function

import click
import tabulate

from molecule import logger
from molecule.command import base

LOG = logger.get_logger(__name__)


class List(base.Base):
    def execute(self):
        """
        Execute the actions necessary to perform a `molecule list` and
        returns None.

        >>> molecule list

        Targeting a specific scenario:

        >>> molecule list --scenario-name foo

        Executing with `debug`:

        >>> molecule --debug list

        :return: None
        """
        return self._config.driver.status()


@click.command()
@click.pass_context
@click.option('--scenario-name', help='Name of the scenario to target.')
def list(ctx, scenario_name):  # pragma: no cover
    """ Lists status of instances. """
    args = ctx.obj.get('args')
    command_args = {'subcommand': __name__, 'scenario_name': scenario_name}

    statuses = []
    for config in base.get_configs(args, command_args):
        l = List(config)
        statuses.extend(l.execute())

    _print_tabulate_data([
        'Instance', 'Driver', 'Provisioner', 'Scenario', 'Created', 'Converged'
    ], statuses)


def _print_tabulate_data(headers, data):  # pragma: no cover
    """
    Shows the tabulate data on the screen and returns None.

    :param headers: A list of column headers.
    :param data:  A list of tabular data to display.
    :returns: None
    """
    print(tabulate.tabulate(data, headers, tablefmt='orgtbl'))

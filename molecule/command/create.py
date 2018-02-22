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

import click

from molecule import config
from molecule import logger
from molecule import scenarios
from molecule.command import base

LOG = logger.get_logger(__name__)


class Create(base.Base):
    """
    Target the default scenario:

    $ molecule create

    Targeting a specific scenario:

    $ molecule create --scenario-name foo

    Targeting a specific driver:

    $ molecule converge --driver-name foo

    Executing with `debug`:

    $ molecule --debug create
    """

    def execute(self):
        """
        Execute the actions necessary to perform a `molecule create` and
        returns None.

        :return: None
        """
        self.print_info()
        self._config.state.change_state('driver', self._config.driver.name)

        if self._config.driver.delegated and not self._config.driver.managed:
            msg = 'Skipping, instances are delegated.'
            LOG.warn(msg)
            return

        if self._config.state.created:
            msg = 'Skipping, instances already created.'
            LOG.warn(msg)
            return

        self._config.provisioner.create()

        self._config.state.change_state('created', True)


@click.command()
@click.pass_context
@click.option(
    '--scenario-name',
    '-s',
    default='default',
    help='Name of the scenario to target. (default)')
@click.option(
    '--driver-name',
    '-d',
    type=click.Choice(config.molecule_drivers()),
    help='Name of driver to use. (docker)')
def create(ctx, scenario_name, driver_name):  # pragma: no cover
    """ Use the provisioner to start the instances. """
    args = ctx.obj.get('args')
    subcommand = base._get_subcommand(__name__)
    command_args = {
        'subcommand': subcommand,
        'driver_name': driver_name,
    }

    s = scenarios.Scenarios(
        base.get_configs(args, command_args), scenario_name)
    s.print_matrix()
    for scenario in s:
        for action in scenario.sequence:
            scenario.config.action = action
            base.execute_subcommand(scenario.config, action)

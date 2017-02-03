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

import os

import click

from molecule import logger
from molecule.command import base

LOG = logger.get_logger(__name__)


class Create(base.Base):
    def execute(self):
        """
        Execute the actions necessary to perform a `molecule create` and
        returns None.

        >>> molecule create

        Targeting a specific scenario:

        >>> molecule create --scenario-name foo

        Executing with `debug`:

        >>> molecule --debug create

        :return: None
        """
        msg = 'Scenario: [{}]'.format(self._config.scenario.name)
        LOG.info(msg)
        msg = 'Provisioner: [{}]'.format(self._config.provisioner.name)
        LOG.info(msg)
        msg = 'Playbook: [{}]'.format(
            os.path.basename(self._config.scenario.setup))
        LOG.info(msg)

        if self._config.state.created:
            LOG.warn('Skipping, instances already created.')
            return

        self._config.provisioner.converge(self._config.scenario.setup)

        self._config.state.change_state('created', True)
        # Add the driver's connection_options to inventory, once the instances
        # are created.
        self._config.provisioner.write_inventory()


@click.command()
@click.pass_context
@click.option('--scenario-name', help='Name of the scenario to target.')
def create(ctx, scenario_name):  # pragma: no cover
    """ Start instances. """
    args = ctx.obj.get('args')
    command_args = {'subcommand': __name__, 'scenario_name': scenario_name}

    for config in base.get_configs(args, command_args):
        c = Create(config)
        c.execute()

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

from molecule import config
from molecule import logger
from molecule import scenarios
from molecule.command import base

LOG = logger.get_logger(__name__)


class Prepare(base.Base):
    """
    Target the default scenario:

    $ molecule prepare

    Targeting a specific scenario:

    $ molecule prepare --scenario-name foo

    Targeting a specific driver:

    $ molecule prepare --driver-name foo

    Force the execution fo the prepare playbook:

    $ molecule prepare --force

    Executing with `debug`:

    $ molecule --debug prepare
    """

    def execute(self):
        """
        Execute the actions necessary to prepare the instances and returns
        None.

        :return: None
        """
        self.print_info()

        if (self._config.state.prepared
                and not self._config.command_args.get('force')):
            msg = 'Skipping, instances already prepared.'
            LOG.warn(msg)
            return

        if self._has_prepare_playbook():
            self._config.provisioner.prepare()
        else:
            msg = ('[DEPRECATION WARNING]:\n  The prepare playbook not found '
                   'at {}/prepare.yml.  Please add one to the scenarios '
                   'directory.').format(self._config.scenario.directory)
            LOG.warn(msg)

        self._config.state.change_state('prepared', True)

    def _has_prepare_playbook(self):
        return os.path.exists(self._config.provisioner.playbooks.prepare)


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
@click.option(
    '--force/--no-force',
    default=False,
    help='Enable or disable force mode. Default is disabled.')
def prepare(ctx, scenario_name, driver_name, force):  # pragma: no cover
    """
    Use the provisioner to prepare the instances into a particular starting
    state.
    """
    args = ctx.obj.get('args')
    subcommand = base._get_subcommand(__name__)
    command_args = {
        'subcommand': subcommand,
        'driver_name': driver_name,
        'force': force,
    }

    s = scenarios.Scenarios(
        base.get_configs(args, command_args), scenario_name)
    s.print_matrix()
    for scenario in s:
        for action in scenario.sequence:
            scenario.config.action = action
            base.execute_subcommand(scenario.config, action)

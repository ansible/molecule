#  Copyright (c) 2015-2018 Cisco Systems, Inc.
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


class Prepare(base.Base):
    """
    .. program:: molecule prepare

    .. option:: molecule prepare

        Target the default scenario.

    .. program:: molecule prepare --scenario-name foo

    .. option:: molecule prepare --scenario-name foo

        Targeting a specific scenario.

    .. program:: molecule prepare --driver-name foo

    .. option:: molecule prepare --driver-name foo

        Targeting a specific driver.

    .. program:: molecule prepare --force

    .. option:: molecule prepare --force

        Force the execution fo the prepare playbook.

    .. program:: molecule --debug prepare

    .. option:: molecule --debug prepare

        Executing with `debug`.

    .. program:: molecule --base-config base.yml prepare

    .. option:: molecule --base-config base.yml prepare

        Executing with a `base-config`.

    .. program:: molecule --env-file foo.yml prepare

    .. option:: molecule --env-file foo.yml prepare

        Load an env file to read variables from when rendering
        molecule.yml.
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

        if not self._config.provisioner.playbooks.prepare:
            msg = 'Skipping, prepare playbook not configured.'
            LOG.warn(msg)
            return

        self._config.provisioner.prepare()
        self._config.state.change_state('prepared', True)


@click.command()
@click.pass_context
@click.option(
    '--scenario-name',
    '-s',
    default=base.MOLECULE_DEFAULT_SCENARIO_NAME,
    help='Name of the scenario to target. ({})'.format(
        base.MOLECULE_DEFAULT_SCENARIO_NAME))
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

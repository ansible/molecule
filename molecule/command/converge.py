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

from molecule import logger
from molecule import scenarios
from molecule.command import base

LOG = logger.get_logger(__name__)


class Converge(base.Base):
    """
    Target the default scenario:

    $ molecule converge

    Targeting a specific scenario:

    $ molecule converge --scenario-name foo

    Providing additional command line arguments to the `ansible-playbook`
    command.  Use this option with care, as there is no sanitation or
    validation of input.  Options passed on the CLI override options
    provided in provisioner's `options` section of `molecule.yml`.

    $ molecule converge -- -vvv -tags foo,bar

    Executing with `debug`:

    $ molecule --debug converge
    """

    def execute(self):
        """
        Execute the actions necessary to perform a `molecule converge` and
        returns None.

        :return: None
        """
        self.print_info()
        self._config.provisioner.converge()
        self._config.state.change_state('converged', True)


@click.command()
@click.pass_context
@click.option(
    '--scenario-name',
    '-s',
    default='default',
    help='Name of the scenario to target. (default)')
@click.argument('ansible_args', nargs=-1, type=click.UNPROCESSED)
def converge(ctx, scenario_name, ansible_args):  # pragma: no cover
    """
    Use the provisioner to configure instances (dependency, create, prepare
    converge).
    """

    args = ctx.obj.get('args')
    subcommand = base._get_subcommand(__name__)
    command_args = {
        'subcommand': subcommand,
    }

    s = scenarios.Scenarios(
        base.get_configs(args, command_args, ansible_args), scenario_name)
    s.print_matrix()
    for scenario in s:
        for action in scenario.sequence:
            scenario.config.action = action
            base.execute_subcommand(scenario.config, action)

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
from molecule.command import base

LOG = logger.get_logger(__name__)


class Test(base.Base):
    """
    .. program:: molecule test

    .. option:: molecule test

        Target the default scenario.

    .. program:: molecule test --scenario-name foo

    .. option:: molecule test --scenario-name foo

        Targeting a specific scenario.

    .. program:: molecule test --all

    .. option:: molecule test --all

        Target all scenarios.

    .. program:: molecule test --destroy=always

    .. option:: molecule test --destroy=always

        Always destroy instances at the conclusion of a Molecule run.

    .. program:: molecule --debug test

    .. option:: molecule --debug test

        Executing with `debug`.

    .. program:: molecule --base-config base.yml test

    .. option:: molecule --base-config base.yml test

        Executing with a `base-config`.

    .. program:: molecule --env-file foo.yml test

    .. option:: molecule --env-file foo.yml test

        Load an env file to read variables from when rendering
        molecule.yml.
    """

    def execute(self):
        """
        Execute the actions necessary to perform a `molecule test` and
        returns None.

        :return: None
        """


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
    '--all/--no-all',
    '__all',
    default=False,
    help='Test all scenarios. Default is False.')
@click.option(
    '--destroy',
    type=click.Choice(['always', 'never']),
    default='always',
    help=('The destroy strategy used at the conclusion of a '
          'Molecule run (always).'))
def test(ctx, scenario_name, driver_name, __all, destroy):  # pragma: no cover
    """
    Test (lint, cleanup, destroy, dependency, syntax, create, prepare,
          converge, idempotence, side_effect, verify, cleanup, destroy).
    """

    args = ctx.obj.get('args')
    subcommand = base._get_subcommand(__name__)
    command_args = {
        'destroy': destroy,
        'subcommand': subcommand,
        'driver_name': driver_name,
    }

    if __all:
        scenario_name = None

    base.execute_cmdline_scenarios(scenario_name, args, command_args)

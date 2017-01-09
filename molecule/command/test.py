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

import molecule.command
from molecule.command import base


class Test(base.Base):
    def execute(self):
        """
        Execute the actions necessary to perform a `molecule test` and
        returns None.

        >>> molecule test

        Targeting a specific scenario:

        >>> molecule test --scenario-name foo

        Executing with `debug`:

        >>> molecule --debug test

        :return: None
        """


@click.command()
@click.pass_context
@click.option('--scenario-name', help='Name of the scenario to target.')
def test(ctx, scenario_name):  # pragma: no cover
    """ Test (destroy, create, converge, lint, verify, destroy). """
    args = ctx.obj.get('args')
    command_args = {'subcommand': __name__, 'scenario_name': scenario_name}

    for config in base.get_configs(args, command_args):
        for task in config.scenario.test_sequence:
            command_module = getattr(molecule.command, task)
            command = getattr(command_module, task.capitalize())
            c = command(config)
            c.execute()

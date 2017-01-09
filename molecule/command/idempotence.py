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
import re

import click

from molecule import util
from molecule.command import base


class Idempotence(base.Base):
    def execute(self):
        """
        Execute the actions necessary to perform a `molecule idempotence` and
        returns None.

        >>> molecule idempotence

        Targeting a specific scenario:

        >>> molecule idempotence --scenario-name foo

        Executing with `debug`:

        >>> molecule --debug idempotence

        :return: None
        """
        msg = 'Scenario: [{}]'.format(self._config.scenario.name)
        util.print_info(msg)
        msg = 'Provisioner: [{}]'.format(self._config.provisioner.name)
        util.print_info(msg)
        msg = 'Idempotence Verification of Playbook: [{}]'.format(
            os.path.basename(self._config.scenario.converge))
        util.print_info(msg)

        if not self._config.state.converged:
            msg = 'Instances not converged.  Please converge instances first.'
            util.print_error(msg)
            util.sysexit()

        output = self._config.provisioner.converge(
            self._config.scenario.converge, out=None, err=None)

        idempotent = self._is_idempotent(output)
        if idempotent:
            util.print_success('Idempotence test passed.')
        else:
            msg = 'Idempotence test failed because of the following tasks:'
            util.print_error(msg)
            util.print_error('\n'.join(self._non_idempotent_tasks(output)))
            util.sysexit()

    def _is_idempotent(self, output):
        """
        Parses the output of the provisioning for changed and returns a bool.

        :param output: A string containing the output of the ansible run.
        :return: bool
        """

        # Remove blank lines to make regex matches easier
        output = re.sub('\n\s*\n*', '\n', output)

        # Look for any non-zero changed lines
        changed = re.search(r'(changed=[1-9][0-9]*)', output)

        if changed:
            # Not idempotent
            return False

        return True

    def _non_idempotent_tasks(self, output):
        """
        Parses the output to identify the non idempotent tasks.

        :param (str) output: A string containing the output of the ansible run.
        :return: A list containing the names of the non idempotent tasks.
        """
        # Remove blank lines to make regex matches easier.
        output = re.sub(r'\n\s*\n*', '\n', output)

        # Remove ansi escape sequences.
        output = re.sub(r'\x1b[^m]*m', '', output)

        # Split the output into a list and go through it.
        output_lines = output.split('\n')
        res = []
        task_line = ''
        for idx, line in enumerate(output_lines):
            if line.startswith('TASK'):
                task_line = line
            elif line.startswith('changed'):
                host_name = re.search(r'\[(.*)\]', line).groups()[0]
                task_name = re.search(r'\[(.*)\]', task_line).groups()[0]
                res.append('* [{}] => {}'.format(host_name, task_name))

        return res


@click.command()
@click.pass_context
@click.option('--scenario-name', help='Name of the scenario to target.')
def idempotence(ctx, scenario_name):  # pragma: no cover
    """
    Use a provisioner to configure the instances and parse the output to
    determine idempotence.
    """
    args = ctx.obj.get('args')
    command_args = {'subcommand': __name__, 'scenario_name': scenario_name}

    for config in base.get_configs(args, command_args):
        i = Idempotence(config)
        i.execute()

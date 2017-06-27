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


class Syntax(base.Base):
    """
    Target the default scenario:

    >>> molecule syntax

    Targeting a specific scenario:

    >>> molecule syntax --scenario-name foo

    Executing with `debug`:

    >>> molecule --debug syntax
    """

    def execute(self):
        """
        Execute the actions necessary to perform a `molecule syntax` and
        returns None.

        :return: None
        """
        msg = 'Scenario: [{}]'.format(self._config.scenario.name)
        LOG.info(msg)
        msg = 'Provisioner: [{}]'.format(self._config.provisioner.name)
        LOG.info(msg)
        msg = 'Syntax Verification of Playbook: [{}]'.format(
            os.path.basename(self._config.provisioner.playbooks.converge))
        LOG.info(msg)

        self._config.provisioner.syntax()


@click.command()
@click.pass_context
@click.option(
    '--scenario-name',
    default='default',
    help='Name of the scenario to target. (default)')
def syntax(ctx, scenario_name):  # pragma: no cover
    """ Use a provisioner to syntax check the role. """
    args = ctx.obj.get('args')
    command_args = {
        'subcommand': __name__,
        'scenario_name': scenario_name,
    }

    for c in base.get_configs(args, command_args):
        Syntax(c).execute()

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

import fcntl
import os
import signal
import struct
import sys
import termios

import click
import pexpect

from molecule import logger
from molecule import util
from molecule.command import base

LOG = logger.get_logger(__name__)


class Login(base.Base):
    def __init__(self, c):
        super(Login, self).__init__(c)
        self._pt = None

    def execute(self):
        """
        Execute the actions necessary to perform a `molecule login` and
        returns None.

        >>> molecule login --host hotname --scenario-name foo

        :return: None
        """
        if not self._config.state.created:
            msg = 'Instances not created.  Please create instances first.'
            util.sysexit_with_message(msg)

        hosts = [
            d['name']
            for d in self._config.platforms.instances_with_scenario_name
        ]
        hostname = self._get_hostname(hosts)
        self._get_login(hostname)

    def _get_hostname(self, hosts):
        hostname = self._config.command_args.get('host')
        match = [x for x in hosts if x.startswith(hostname)]
        if len(match) == 0:
            msg = ("There are no hosts that match '{}'.  You "
                   'can only login to valid hosts.').format(hostname)
            util.sysexit_with_message(msg)
        elif len(match) != 1:
            # If there are multiple matches, but one of them is an exact string
            # match, assume this is the one they're looking for and use it.
            if hostname in match:
                match = [hostname, ]
            else:
                msg = ("There are {} hosts that match '{}'. You "
                       'can only login to one at a time.\n\n'
                       'Available hosts:\n{}'.format(
                           len(match), hostname, '\n'.join(sorted(hosts))))
                util.sysexit_with_message(msg)

        return match[0]

    def _get_login(self, hostname):  # pragma: no cover
        login_cmd = self._config.driver.login_cmd_template
        login_args = self._config.driver.login_args(hostname)

        lines, columns = os.popen('stty size', 'r').read().split()
        dimensions = (int(lines), int(columns))
        self._pt = pexpect.spawn(
            '/usr/bin/env ' + login_cmd.format(*login_args),
            dimensions=dimensions)
        signal.signal(signal.SIGWINCH, self._sigwinch_passthrough)
        self._pt.interact()

    def _sigwinch_passthrough(self):  # pragma: no cover
        tiocgwinsz = 1074295912  # assume
        if 'TIOCGWINSZ' in dir(termios):
            tiocgwinsz = termios.TIOCGWINSZ
        s = struct.pack('HHHH', 0, 0, 0, 0)
        a = struct.unpack('HHHH',
                          fcntl.ioctl(sys.stdout.fileno(), tiocgwinsz, s))
        self._pt.setwinsize(a[0], a[1])


@click.command()
@click.pass_context
@click.option('--host', required=True, help='Host to access.')
@click.option(
    '--scenario-name', required=True, help='Name of the scenario to target.')
def login(ctx, host, scenario_name):  # pragma: no cover
    """ Log in to one instance. """
    args = ctx.obj.get('args')
    command_args = {
        'subcommand': __name__,
        'host': host,
        'scenario_name': scenario_name
    }

    for config in base.get_configs(args, command_args):
        l = Login(config)
        l.execute()

#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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
import pexpect
import signal
import struct
import subprocess
import sys
import termios

import click

from molecule import util
from molecule.command import base

LOG = util.get_logger(__name__)


class Login(base.Base):
    def execute(self, exit=True):
        """
        Execute the actions necessary to perform a `molecule login` and
        return a tuple.

        :param exit: (Unused) Provided to complete method signature.
        :return: Return a tuple of None, otherwise sys.exit on command failure.
        """
        # get list of running hosts from state
        if self.molecule.state.hosts:
            hosts = [k for k, v in self.molecule.state.hosts.iteritems()]
        else:
            hosts = []

        try:
            # Nowhere to login to if there is no running host.
            if len(hosts) == 0:
                raise base.InvalidHost('There are no running hosts.')

            # Check whether a host was specified.
            if self.command_args.get('host') is None:
                # One running host is perfect. Login to it.
                if len(hosts) == 1:
                    hostname = hosts[0]

                # But too many hosts is trouble as well.
                else:
                    message = ('There are {} running hosts. Please specify '
                               'which with --host.\n\n'
                               'Available hosts:\n{}'.format(
                                   len(hosts), '\n'.join(sorted(hosts))))
                    raise base.InvalidHost(message)

            else:
                # If the host was specified, try to use it.
                hostname = self.command_args.get('host')
                match = [x for x in hosts if x.startswith(hostname)]
                if len(match) == 0:
                    raise subprocess.CalledProcessError(1, None)
                elif len(match) != 1:
                    # If there are multiple matches, but one of them is an
                    # exact string match, assume this is the one they're
                    # looking for and use it
                    if hostname in match:
                        match = [hostname, ]
                    else:
                        message = ("There are {} hosts that match '{}'. You "
                                   'can only login to one at a time.\n\n'
                                   'Available hosts:\n{}'.format(
                                       len(match), hostname,
                                       '\n'.join(sorted(hosts))))
                        raise base.InvalidHost(message)
                hostname = match[0]

        except subprocess.CalledProcessError:
            msg = "Unknown host '{}'.\n\nAvailable hosts:\n{}"
            LOG.error(
                msg.format(self.command_args.get('host'), '\n'.join(hosts)))
            util.sysexit()
        except base.InvalidHost as e:
            LOG.error(e.message)
            util.sysexit()

        self._get_login(hostname)
        return None, None

    def _get_login(self, hostname):  # pragma: no cover
        login_cmd = self.molecule.driver.login_cmd(hostname)
        login_args = self.molecule.driver.login_args(hostname)

        lines, columns = os.popen('stty size', 'r').read().split()
        dimensions = (int(lines), int(columns))
        self._pt = pexpect.spawn(
            '/usr/bin/env ' + login_cmd.format(*login_args),
            dimensions=dimensions)
        signal.signal(signal.SIGWINCH, self._sigwinch_passthrough)
        self._pt.interact()

    def _sigwinch_passthrough(self, sig, data):  # pragma: no cover
        TIOCGWINSZ = 1074295912  # assume
        if 'TIOCGWINSZ' in dir(termios):
            TIOCGWINSZ = termios.TIOCGWINSZ
        s = struct.pack('HHHH', 0, 0, 0, 0)
        a = struct.unpack('HHHH',
                          fcntl.ioctl(sys.stdout.fileno(), TIOCGWINSZ, s))
        self._pt.setwinsize(a[0], a[1])


@click.command()
@click.option('--driver', default=None, help='Specificy a driver.')
@click.option('--host', default=None, help='Host to access.')
@click.pass_context
def login(ctx, driver, host):  # pragma: no cover
    """
    Initiates an interactive ssh session with the given host.

    \b
    If no `--host` flag provided, will login to the instance.  If more than
    once instance exists, the `--host` flag must be provided.
    """
    command_args = {'driver': driver, 'host': host}

    l = Login(ctx.obj.get('args'), command_args)
    l.execute
    util.sysexit(l.execute()[0])

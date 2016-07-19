#  Copyright (c) 2015-2016 Cisco Systems
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

import os
import pexpect
import signal
import subprocess

from molecule import utilities
from molecule.commands import base


class Login(base.BaseCommand):
    """
    Initiates an interactive ssh session with the given host.

    Usage:
        login [<host>]
    """

    def execute(self):
        if self.static:
            self.disabled('login')

        # Collect the list of running hosts.
        try:
            status = self.molecule._provisioner.status()
        except Exception as e:
            status = []

        # make sure vagrant knows about this host
        try:
            # Nowhere to log into if there is no running host.
            if len(status) == 0:
                raise base.InvalidHost("There is no running host.")

            # Check whether a host was specified.
            if self.molecule._args['<host>'] is None:

                # One running host is perfect. Log into it.
                if len(status) == 1:
                    hostname = status[0].name

                # But too many hosts is trouble as well.
                else:
                    raise base.InvalidHost(
                        "There are {} running hosts. You can only log into one at a time.".format(
                            len(status)))

            else:

                # If the host was specified, try to use it.
                hostname = self.molecule._args['<host>']
                match = [x.name for x in status if x.name.startswith(hostname)]
                if len(match) == 0:
                    raise subprocess.CalledProcessError(1, None)
                elif len(match) != 1:
                    # If there are multiple matches, but one of them is an
                    # exact string match, assume this is the one they're
                    # looking for and use it
                    if hostname in match:
                        match = [hostname, ]
                    else:
                        raise base.InvalidHost(
                            "There are {} hosts that match '{}'.  You can only log into one at a time.\n"
                            "Try molecule status to see available hosts.".format(
                                len(match), hostname))
                hostname = match[0]

            login_cmd = self.molecule._provisioner.login_cmd(hostname)
            login_args = self.molecule._provisioner.login_args(hostname)

        except subprocess.CalledProcessError:
            # gets appended to python-vagrant's error message
            conf_errmsg = '\nUnknown host {}. Try molecule status to see available hosts.'
            utilities.logger.error(conf_errmsg.format(self.molecule._args[
                '<host>']))
            utilities.sysexit()
        except base.InvalidHost as e:
            utilities.logger.error(e.message)
            utilities.sysexit()

        lines, columns = os.popen('stty size', 'r').read().split()
        dimensions = (int(lines), int(columns))
        self.molecule._pt = pexpect.spawn(
            '/usr/bin/env ' + login_cmd.format(*login_args),
            dimensions=dimensions)
        signal.signal(signal.SIGWINCH, self.molecule._sigwinch_passthrough)
        self.molecule._pt.interact()
        return None, None

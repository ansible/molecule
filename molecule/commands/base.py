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

import abc
import docopt

from molecule import core
from molecule import utilities


class InvalidHost(Exception):
    pass


class BaseCommand:
    __metaclass__ = abc.ABCMeta

    def __init__(self, command_args, global_args, molecule=False):
        """
        Initialize commands

        :param command_args: arguments of the command
        :param global_args: arguments from the CLI
        :param molecule: molecule instance
        """
        self.args = docopt.docopt(self.__doc__, argv=command_args)
        self.args['<command>'] = self.__class__.__name__.lower()
        self.command_args = command_args

        self.static = False

        # give us the option to reuse an existing molecule instance
        if not molecule:
            self.molecule = core.Molecule(self.args)
            self.molecule.main()
        else:
            self.molecule = molecule

        # init doesn't need to load molecule files
        if self.__class__.__name__ == 'Init':
            return

        # assume static inventory if no vagrant config block is defined
        if self.molecule._provisioner is None:
            self.static = True

        # assume static inventory if no instances are defined in vagrant config block
        if self.molecule._provisioner.instances is None:
            self.static = True

        # Add or update the group_vars if needed.
        self.molecule._add_or_update_vars('group_vars')

        # Add or update the host_vars if needed
        self.molecule._add_or_update_vars('host_vars')

        # Update symlinks
        self.molecule._symlink_vars()

    def disabled(self, cmd):
        """
        Prints 'command disabled' message and exits program.

        :param cmd: Name of the disabled command to print.
        :return: None
        """
        errmsg = "The `{}` command isn't supported with static inventory."
        utilities.logger.error(errmsg.format(cmd))
        utilities.sysexit()

    @abc.abstractproperty
    def execute(self):
        pass

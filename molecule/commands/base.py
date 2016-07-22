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

    def __init__(self, command_args, args, molecule=False):
        """
        Initialize commands

        :param command_args: arguments of the command
        :param args: arguments from the CLI
        :param molecule: molecule instance
        """
        self.args = docopt.docopt(self.__doc__, argv=command_args)
        self.args['<command>'] = self.__class__.__name__.lower()
        self.command_args = command_args

        self.molecule = core.Molecule(self.args)
        self.main()

    def main(self):
        c = self.molecule._config
        if not c.molecule_file_exists():
            error = '\nUnable to find {}. Exiting.'
            utilities.logger.error(error.format(c.molecule_file))
            utilities.sysexit()
        self.molecule.main()

    @abc.abstractproperty
    def execute(self):
        pass

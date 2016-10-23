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

import abc

from molecule import config
from molecule import core
from molecule import util

LOG = util.get_logger(__name__)


class InvalidHost(Exception):
    """
    Exception class raised when an error occurs in :class:`.Login`.
    """
    pass


class Base(object):
    """
    An abstract base class used to define the command interface.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, args, command_args, molecule=None):
        """
        Base initializer for all :ref:`Command` classes.

        :param args: A dict of options, arguments and commands from the CLI.
        :param command_args: A dict of options passed to the subcommand from
         the CLI.
        :param molecule: An optional instance of molecule.
        :returns: None
        """
        self.args = args
        self.command_args = command_args
        self._config = self._get_config()

        options = args.copy()
        options.update(command_args)

        if not molecule:
            self.molecule = self._get_core(options)
            self.main()
        else:
            self.molecule = molecule

    def main(self):
        """
        A mechanism to initialize molecule by calling its main method.  This
        can be redefined by classes which do not want this behavior
        (:class:`.Init`).

        :returns: None
        """
        if not self._config.molecule_file_exists():
            msg = 'Unable to find {}. Exiting.'
            LOG.error(msg.format(self._config.molecule_file))
            util.sysexit()
        self.molecule.main()

    @abc.abstractproperty
    def execute(self):  # pragma: no cover
        pass

    def _get_config(self):
        return config.ConfigV1()

    def _get_core(self, options):
        return core.Molecule(self._config, options)

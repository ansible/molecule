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

import abc
import collections
import glob
import os

from molecule import config
from molecule import util

MOLECULE_GLOB = 'molecule/*/molecule.yml'


class Base(object):
    """
    An abstract base class used to define the command interface.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, c):
        """
        Base initializer for all :ref:`Command` classes.

        :param c: An instance of a Molecule config.
        :returns: None
        """
        self._config = c
        self._setup()

    @abc.abstractmethod
    def execute(self):  # pragma: no cover
        pass

    def prune(self):
        """
        Prune the ephemeral directory with the exception of safe files and
        returns None.

        :return: None
        """
        safe_files = [
            self._config.provisioner.config_file,
            self._config.provisioner.inventory_file,
            self._config.state.state_file,
        ] + self._config.driver.safe_files

        files = util.os_walk(self._config.scenario.ephemeral_directory, '*')
        for f in files:
            if all(sf not in f for sf in safe_files):
                os.remove(f)

    def _setup(self):
        """
        Prepare Molecule's provisioner and returns None.

        :return: None
        """
        self._config.provisioner.write_config()
        self._config.provisioner.manage_inventory()


def _verify_configs(configs):
    """
    Verify a Molecule config was found and returns None.

    :param configs: A list containing absolute paths to Molecule config files.
    :return: None
    """
    if configs:
        scenario_names = [c.scenario.name for c in configs]
        for scenario_name, n in collections.Counter(scenario_names).items():
            if n > 1:
                msg = ("Duplicate scenario name '{}' found.  "
                       'Exiting.').format(scenario_name)
                util.sysexit_with_message(msg)

    else:
        msg = "'{}' glob failed.  Exiting.".format(MOLECULE_GLOB)
        util.sysexit_with_message(msg)


def get_configs(args, command_args):
    """
    Glob the current directory for Molecule config files, instantiate config
    objects, and returns a list.

    :param args: A dict of options, arguments and commands from the CLI.
    :param command_args: A dict of options passed to the subcommand from
     the CLI.
    :return: list
    """
    configs = [
        config.Config(
            molecule_file=util.abs_path(c),
            args=args,
            command_args=command_args) for c in glob.glob(MOLECULE_GLOB)
    ]
    _verify_configs(configs)

    return configs

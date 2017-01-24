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
from molecule import interpolation
from molecule import util


class Base(object):
    """
    An abstract base class used to define the command interface.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, config):
        """
        Base initializer for all :ref:`Command` classes.

        :param config: An instance of a Molecule config.
        :returns: None
        """
        self._config = config

    @abc.abstractmethod
    def execute(self):  # pragma: no cover
        pass


def _load_config(c):
    """
    Open, interpolate, and YAML parse the provided file and returns a dict.

    :param c: A string containing an absolute path to a Molecule config.
    :return: dict
    """
    i = interpolation.Interpolator(interpolation.TemplateWithDefaults,
                                   os.environ)
    with open(c, 'r') as stream:
        interpolated_config = i.interpolate(stream.read())

        return util.safe_load(interpolated_config)


def _verify_configs(configs):
    """
    Verify a Molecule config was found and returns None.

    :param configs: A list containing absolute paths to Molecule config files.
    :return: None
    """
    if configs:
        scenario_names = [config.scenario.name for config in configs]
        for scenario_name, n in collections.Counter(scenario_names).items():
            if n > 1:
                msg = ("Duplicate scenario name '{}' found.  "
                       'Exiting.').format(scenario_name)
                util.sysexit_with_message(msg)

    else:
        msg = 'Unable to find a molecule.yml.  Exiting.'
        util.sysexit_with_message(msg)


def _setup(configs):
    """
    Prepare the system for Molecule and returns None.

    The ephemeral directory is pruned with the exception of the state file.

    :return: None
    """
    for c in configs:
        for root, dirs, files in os.walk(c.ephemeral_directory, topdown=False):
            for name in files:
                state_file = os.path.basename(c.state.state_file)
                if name != state_file:
                    os.remove(os.path.join(root, name))
        if not os.path.isdir(c.ephemeral_directory):
            os.mkdir(c.ephemeral_directory)

        c.provisioner.write_inventory()
        c.provisioner.write_config()
        c.provisioner._add_or_update_vars('host_vars')
        c.provisioner._add_or_update_vars('group_vars')


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
            molecule_file=os.path.abspath(c),
            args=args,
            command_args=command_args,
            configs=[_load_config(c)])
        for c in glob.glob('molecule/*/molecule.yml')
    ]

    scenario_name = command_args.get('scenario_name')
    if scenario_name:
        configs = _filter_configs_for_scenario(scenario_name, configs)

    _verify_configs(configs)
    _setup(configs)

    return configs


def _filter_configs_for_scenario(scenario_name, configs):
    """
    Find the config matching the provided scenario name and returns a list.

    :param scenario_name: A string representing the name of the scenario's
     config to return
    :param configs: A list containing Molecule config instances.
    :return: list
    """

    return [
        config for config in configs if config.scenario.name == scenario_name
    ]

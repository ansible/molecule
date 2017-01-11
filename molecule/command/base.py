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
import os

import yaml

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


def _load_config(config):
    """
    Open, interpolate, and YAML parse the provided file and returns a dict.

    :param config: A string containing an absolute path to a Molecule config.
    :return: dict
    """
    i = interpolation.Interpolator(interpolation.TemplateWithDefaults,
                                   os.environ)
    with open(config, 'r') as stream:
        interpolated_config = i.interpolate(stream.read())

        return yaml.safe_load(interpolated_config) or {}


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
                util.print_error(msg)
                util.sysexit()

    else:
        msg = 'Unable to find a molecule.yml.  Exiting.'
        util.print_error(msg)
        util.sysexit()


def get_configs(args, command_args):
    """
    Walk the current directory for Molecule config files and returns a list.

    :param args: A dict of options, arguments and commands from the CLI.
    :param command_args: A dict of options passed to the subcommand from
     the CLI.
    :return: list
    """
    current_directory = os.path.join(os.getcwd(), 'molecule')
    configs = [
        config.Config(
            molecule_file=c,
            args=args,
            command_args=command_args,
            configs=[_load_config(c)])
        for c in util.os_walk(current_directory, 'molecule.yml')
    ]

    scenario_name = command_args.get('scenario_name')
    if scenario_name:
        configs = _filter_configs_for_scenario(scenario_name, configs)

    _verify_configs(configs)

    return configs


def _filter_configs_for_scenario(scenario_name, configs):
    """
    Find the config matching the provided scenario name and return a list.

    :param scenario_name: A string representing the name of the scenario's
     config to return
    :param configs: A list containing Molecule config instances.
    :return: list
    """

    return [
        config for config in configs if config.scenario.name == scenario_name
    ]

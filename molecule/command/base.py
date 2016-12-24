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
import os

import yaml

from molecule import config
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
        self._setup_provisioner()

    @abc.abstractmethod
    def execute(self):  # pragma: no cover
        pass

    # TODO(retr0h): Test it
    def _setup_provisioner(self):
        self._config.provisioner.write_inventory()
        self._config.provisioner.write_config()


def _get_local_config():
    expanded_path = os.path.expanduser(config.MOLECULE_LOCAL_CONFIG)
    try:
        return _load_config(expanded_path)
    except IOError:
        return {}


def _load_config(config):
    with open(config, 'r') as stream:
        return yaml.load(stream) or {}


def _verify_configs(configs):
    if not configs:
        msg = ('Unable to find a molecule.yml.  Exiting.')
        util.print_error(msg)
        util.sysexit()


def get_configs(args, command_args):
    current_directory = os.path.join(os.getcwd(), 'molecule')
    local_config = _get_local_config()
    configs = [
        config.Config(
            molecule_file=c,
            args=args,
            command_args=command_args,
            configs=[local_config, _load_config(c)])
        for c in util.os_walk(current_directory, 'molecule.yml')
    ]
    _verify_configs(configs)

    return configs

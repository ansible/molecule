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

import os

import anyconfig

from molecule import interpolation
from molecule import logger
from molecule import platforms
from molecule import scenario
from molecule import state
from molecule import util
from molecule.dependency import ansible_galaxy
from molecule.dependency import gilt
from molecule.driver import dockr
from molecule.driver import lxc
from molecule.driver import lxd
from molecule.driver import vagrant
from molecule.lint import ansible_lint
from molecule.provisioner import ansible
from molecule.verifier import goss
from molecule.verifier import testinfra

LOG = logger.get_logger(__name__)
MOLECULE_DIRECTORY = 'molecule'
MOLECULE_EPHEMERAL_DIRECTORY = '.molecule'
MOLECULE_FILE = 'molecule.yml'
MERGE_STRATEGY = anyconfig.MS_DICTS


class Config(object):
    """
    Molecule searches the current directory for `molecule.yml` files by
    globbing `molecule/*/molecule.yml`.  The files are instantiated into
    a list of Molecule :class:`.Config` objects, and each Molecule subcommand
    operates on this list.

    The directory in which the `molecule.yml` resides is the Scenario's
    directory.  Molecule performs most functions within this directory.

    The :class:`.Config` object has instantiated Dependency_, Driver_, Lint_,
    Platforms_, Provisioner_, Verifier_, :class:`.Scenario`, and State_
    references.
    """

    def __init__(self, molecule_file, args=None, command_args=None):
        """
        Initialize a new config version one class and returns None.

        :param molecule_file: A string containing the path to the Molecule file
         to be parsed.
        :param args: A dict of options, arguments and commands from the CLI.
        :param command_args: A dict of options passed to the subcommand from
         the CLI.
        :returns: None
        """
        # TODO(retr0h): This file should be merged.
        self.molecule_file = molecule_file
        self.args = args if args else {}
        self.command_args = command_args if command_args else {}
        self.config = self._combine()

    @property
    def ephemeral_directory(self):
        return molecule_ephemeral_directory(self.scenario.directory)

    @property
    def dependency(self):
        dependency_name = self.config['dependency']['name']
        if dependency_name == 'galaxy':
            return ansible_galaxy.AnsibleGalaxy(self)
        elif dependency_name == 'gilt':
            return gilt.Gilt(self)
        else:
            self._exit_with_invalid_section('dependency', dependency_name)

    @property
    def driver(self):
        driver_name = self.config['driver']['name']
        if driver_name == 'docker':
            return dockr.Dockr(self)
        elif driver_name == 'lxc':
            return lxc.Lxc(self)
        elif driver_name == 'lxd':
            return lxd.Lxd(self)
        elif driver_name == 'vagrant':
            return vagrant.Vagrant(self)
        else:
            self._exit_with_invalid_section('driver', driver_name)

    @property
    def drivers(self):
        return molecule_drivers()

    @property
    def lint(self):
        lint_name = self.config['lint']['name']
        if lint_name == 'ansible-lint':
            return ansible_lint.AnsibleLint(self)
        else:
            self._exit_with_invalid_section('lint', lint_name)

    @property
    def platforms(self):
        return platforms.Platforms(self)

    @property
    def provisioner(self):
        provisioner_name = self.config['provisioner']['name']
        if provisioner_name == 'ansible':
            return ansible.Ansible(self)
        else:
            self._exit_with_invalid_section('provisioner', provisioner_name)

    @property
    def scenario(self):
        return scenario.Scenario(self)

    @property
    def state(self):
        return state.State(self)

    @property
    def verifier(self):
        verifier_name = self.config['verifier']['name']
        if verifier_name == 'testinfra':
            return testinfra.Testinfra(self)
        elif verifier_name == 'goss':
            return goss.Goss(self)
        else:
            self._exit_with_invalid_section('verifier', verifier_name)

    @property
    def verifiers(self):
        return molecule_verifiers()

    def _combine(self):
        """
        Perform a prioritized recursive merge of the `molecule_file` with
        defaults and returns a new dict.

        :return: dict
        """
        i = interpolation.Interpolator(interpolation.TemplateWithDefaults,
                                       os.environ)

        base = self._get_defaults()
        with open(self.molecule_file, 'r') as stream:
            interpolated_config = i.interpolate(stream.read())
            base = self.merge_dicts(base, util.safe_load(interpolated_config))

        return base

    def _get_defaults(self):
        return {
            'dependency': {
                'name': 'galaxy',
                'options': {},
                'env': {},
                'enabled': True,
            },
            'driver': {
                'name': 'docker',
                'options': {},
            },
            'lint': {
                'name': 'ansible-lint',
                'enabled': True,
                'options': {},
                'env': {},
            },
            'platforms': [],
            'provisioner': {
                'name': 'ansible',
                'config_options': {},
                'options': {},
                'env': {},
                'host_vars': {},
                'group_vars': {},
                'children': {},
            },
            'scenario': {
                'name': 'default',
                'setup': 'create.yml',
                'converge': 'playbook.yml',
                'teardown': 'destroy.yml',
                'check_sequence': ['create', 'converge', 'check'],
                'converge_sequence': ['create', 'converge'],
                'test_sequence': [
                    'destroy', 'dependency', 'syntax', 'create', 'converge',
                    'idempotence', 'lint', 'verify', 'destroy'
                ],
            },
            'verifier': {
                'name': 'testinfra',
                'enabled': True,
                'directory': 'tests',
                'options': {},
                'env': {},
            },
        }

    def _exit_with_invalid_section(self, section, name):
        msg = "Invalid {} named '{}' configured.".format(section, name)
        util.sysexit_with_message(msg)

    def merge_dicts(self, a, b):
        return merge_dicts(a, b)


def merge_dicts(a, b):
    """
    Merges the values of B into A and returns a new dict.  Uses the same
    merge strategy as ``config._combine``.

    ::

        dict a

        b:
           - c: 0
           - c: 2
        d:
           e: "aaa"
           f: 3

        dict b

        a: 1
        b:
           - c: 3
        d:
           e: "bbb"

    Will give an object such as::

        {'a': 1, 'b': [{'c': 3}], 'd': {'e': "bbb", 'f': 3}}


    :param a: the target dictionary
    :param b: the dictionary to import
    :return: dict
    """
    conf = anyconfig.to_container(a, ac_merge=MERGE_STRATEGY)
    conf.update(b)

    return conf


def molecule_directory(path):
    return os.path.join(path, MOLECULE_DIRECTORY)


def molecule_ephemeral_directory(path):
    return os.path.join(path, '.molecule')


def molecule_file(path):
    return os.path.join(path, MOLECULE_FILE)


def molecule_drivers():
    return [
        dockr.Dockr(None).name,
        lxc.Lxc(None).name,
        lxd.Lxd(None).name,
        vagrant.Vagrant(None).name,
    ]


def molecule_verifiers():
    return [goss.Goss(None).name, testinfra.Testinfra(None).name]

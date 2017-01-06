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

from molecule import provisioner
from molecule import scenario
from molecule.dependency import ansible_galaxy
from molecule.driver import docker
from molecule.lint import ansible_lint
from molecule.verifier import testinfra

MOLECULE_DIRECTORY = 'molecule'
MOLECULE_EPHEMERAL_DIRECTORY = '.molecule'
MOLECULE_FILE = 'molecule.yml'


class Config(object):
    MERGE_STRATEGY = anyconfig.MS_DICTS

    def __init__(self, molecule_file, args={}, command_args={}, configs=[]):
        """
        Initialize a new config version one class and returns None.

        :param molecule_file: A string containing the path to the Molecule file
         parsed.
        :param args: A dict of options, arguments and commands from the CLI.
        :param command_args: A dict of options passed to the subcommand from
         the CLI.
        :param configs: A list of dicts to merge.
        :returns: None
        """
        self.molecule_file = molecule_file
        self.args = args
        self.command_args = command_args
        self.config = self._combine(configs)

    @property
    def ephemeral_directory(self):
        return molecule_ephemeral_directory(self.scenario.directory)

    @property
    def dependency(self):
        if self.config['dependency']['name'] == 'galaxy':
            return ansible_galaxy.AnsibleGalaxy(self)

    @property
    def driver(self):
        if self.config['driver']['name'] == 'docker':
            return docker.Docker(self)

    @property
    def lint(self):
        if self.config['lint']['name'] == 'ansible-lint':
            return ansible_lint.AnsibleLint(self)

    @property
    def platforms(self):
        return self.config['platforms']

    @property
    def provisioner(self):
        if self.config['provisioner']['name'] == 'ansible':
            return provisioner.Ansible(self)

    @property
    def scenario(self):
        return scenario.Scenario(self)

    @property
    def verifier(self):
        if self.config['verifier']['name'] == 'testinfra':
            return testinfra.Testinfra(self)

    def _combine(self, configs):
        """ Perform a prioritized recursive merge of serveral source dicts
        and returns a new dict.

        The merge order is based on the index of the list, meaning that
        elements at the end of the list will be merged last, and have greater
        precedence than elements at the beginning.  The result is then merged
        ontop of the defaults.

        :param configs: A list containing the dicts to load.
        :return: dict
        """

        base = self._get_defaults()
        for config in configs:
            base = self.merge_dicts(base, config)

        return base

    def _get_defaults(self):
        return {
            'dependency': {
                'name': 'galaxy',
                'options': {},
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
            },
            'platforms': [],
            'provisioner': {
                'name': 'ansible',
                'options': {
                    'ask_become_pass': False,
                    'ask_vault_pass': False,
                    'config_file': 'ansible.cfg',
                    'diff': True,
                    'host_key_checking': False,
                    'inventory_file': 'ansible_inventory.yml',
                    'limit': 'all',
                    'playbook': 'playbook.yml',
                    'raw_ssh_args': [
                        '-o UserKnownHostsFile=/dev/null',
                        '-o IdentitiesOnly=yes',
                        '-o ControlMaster=auto',
                        '-o ControlPersist=60s',
                    ],
                    'become': True,
                    'become_user': False,
                    'tags': False,
                    'timeout': 30,
                    'vault_password_file': False,
                    'verbose': False,
                },
            },
            'scenario': {
                'name': 'default',
                'setup': 'create.yml',
                'converge': 'playbook.yml',
                'teardown': 'destroy.yml',
                'converge_sequence': ['create', 'converge'],
                'test_sequence':
                ['destroy', 'create', 'converge', 'lint', 'verify', 'destroy'],
                'idempotence_sequence': ['create', 'converge', 'idempotence'],
            },
            'verifier': {
                'name': 'testinfra',
                'enabled': True,
                'directory': 'tests',
                'options': {},
            },
        }

    def merge_dicts(self, a, b):
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
        conf = anyconfig.to_container(a, ac_merge=self.MERGE_STRATEGY)
        conf.update(b)

        return conf


def molecule_directory(path):
    return os.path.join(path, MOLECULE_DIRECTORY)


def molecule_ephemeral_directory(path):
    return os.path.join(path, '.molecule')


def molecule_file(path):
    return os.path.join(path, MOLECULE_FILE)

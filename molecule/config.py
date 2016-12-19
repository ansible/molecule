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

import collections
import os

import anyconfig

from molecule.dependency import ansible_galaxy
from molecule.driver import docker
from molecule.lint import ansible_lint
from molecule.provisioner import ansible
from molecule.verifier import testinfra

LOCAL_CONFIG = '~/.config/molecule/config.yml'
MERGE_STRATEGY = anyconfig.MS_DICTS


class Config(object):
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
    def inventory(self):
        return self.driver.inventory

    @property
    def inventory_file(self):
        return os.path.join(self.scenario_directory, '.molecule',
                            'ansible_inventory')

    @property
    def dependency(self):
        if self.dependency_name == 'galaxy':
            return ansible_galaxy.AnsibleGalaxy(self)

    @property
    def dependency_name(self):
        return self.config['dependency']['name']

    @property
    def dependency_enabled(self):
        return self.config['dependency']['enabled']

    @property
    def dependency_options(self):
        return merge_dicts(self.dependency.options,
                           self.config['dependency']['options'])

    @property
    def driver(self):
        if self.driver_name == 'docker':
            return docker.Docker(self)

    @property
    def driver_name(self):
        return self.config['driver']['name']

    @property
    def driver_options(self):
        return self.config['driver']['options']

    @property
    def lint(self):
        if self.lint_name == 'ansible-lint':
            return ansible_lint.AnsibleLint(self)

    @property
    def lint_name(self):
        return self.config['lint']['name']

    @property
    def lint_enabled(self):
        return self.config['lint']['enabled']

    @property
    def lint_options(self):
        return merge_dicts(self.lint.options, self.config['lint']['options'])

    @property
    def platforms(self):
        return self.config['platforms']

    @property
    def platform_groups(self):
        #  [baz]
        #  instance-2
        #  [foo]
        #  instance-1
        #  instance-2
        #  [bar]
        #  instance-1
        dd = collections.defaultdict(list)
        for platform in self.config['platforms']:
            for group in platform.get('groups', []):
                dd[group].append(platform['name'])

        return dict(dd)

    @property
    def provisioner(self):
        if self.provisioner_name == 'ansible':
            return ansible.Ansible(self)

    @property
    def provisioner_name(self):
        return self.config['provisioner']['name']

    @property
    def provisioner_options(self):
        return self.config['provisioner']['options']

    @property
    def scenario_name(self):
        return self.config['scenario']['name']

    @property
    def scenario_directory(self):
        return os.path.dirname(self.molecule_file)

    @property
    def scenario_setup(self):
        return os.path.join(self.scenario_directory,
                            self.config['scenario']['setup'])

    @property
    def scenario_converge(self):
        return os.path.join(self.scenario_directory,
                            self.config['scenario']['converge'])

    @property
    def scenario_teardown(self):
        return os.path.join(self.scenario_directory,
                            self.config['scenario']['teardown'])

    @property
    def verifier(self):
        if self.verifier_name == 'testinfra':
            return testinfra.Testinfra(self)

    @property
    def verifier_name(self):
        return self.config['verifier']['name']

    @property
    def verifier_enabled(self):
        return self.config['verifier']['enabled']

    @property
    def verifier_directory(self):
        return os.path.join(self.scenario_directory,
                            self.config['verifier']['directory'])

    @property
    def verifier_options(self):
        return merge_dicts(self.verifier.options,
                           self.config['verifier']['options'])

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
            base = merge_dicts(base, config)

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
                    'ask_sudo_pass': False,
                    'ask_vault_pass': False,
                    'config_file': 'ansible.cfg',
                    'diff': True,
                    'host_key_checking': False,
                    'inventory_file': 'ansible_inventory',
                    'limit': 'all',
                    'playbook': 'playbook.yml',
                    'raw_ssh_args': [
                        '-o UserKnownHostsFile=/dev/null',
                        '-o IdentitiesOnly=yes',
                        '-o ControlMaster=auto',
                        '-o ControlPersist=60s',
                    ],
                    'sudo': True,
                    'sudo_user': False,
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
            },
            'verifier': {
                'name': 'testinfra',
                'enabled': True,
                'directory': 'tests',
                'options': {},
            },
        }


def merge_dicts(a, b):
    """
    Merges the values of B into A and returns a new dict.  Uses the same merge
    strategy as ``config._combine``.

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

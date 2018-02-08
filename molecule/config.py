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
from molecule.driver import azure
from molecule.driver import delegated
from molecule.driver import docker
from molecule.driver import ec2
from molecule.driver import gce
from molecule.driver import lxc
from molecule.driver import lxd
from molecule.driver import openstack
from molecule.driver import vagrant
from molecule.lint import yamllint
from molecule.model import schema
from molecule.provisioner import ansible
from molecule.verifier import goss
from molecule.verifier import testinfra

LOG = logger.get_logger(__name__)
MOLECULE_DIRECTORY = 'molecule'
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

    The :class:`.Config` object has instantiated Dependency_, Driver_,
    :ref:`root_lint`, Platforms_, Provisioner_, Verifier_,
    :ref:`root_scenario`, and State_ references.
    """

    def __init__(self,
                 molecule_file,
                 args={},
                 command_args={},
                 ansible_args=()):
        """
        Initialize a new config class and returns None.

        :param molecule_file: A string containing the path to the Molecule file
         to be parsed.
        :param args: An optional dict of options, arguments and commands from
         the CLI.
        :param command_args: An optional dict of options passed to the
         subcommand from the CLI.
        :param ansible_args: An optional tuple of arguments provided to the
         `ansible-playbook` command.
        :returns: None
        """
        self.molecule_file = molecule_file
        self.args = args
        self.command_args = command_args
        self.ansible_args = ansible_args
        self.config = self._combine()
        self._action = None

    @property
    def debug(self):
        return self.args.get('debug', False)

    @property
    def subcommand(self):
        return self.command_args['subcommand']

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        self._action = value

    @property
    def project_directory(self):
        return os.getcwd()

    @property
    def molecule_directory(self):
        return molecule_directory(self.project_directory)

    @property
    def dependency(self):
        dependency_name = self.config['dependency']['name']
        if dependency_name == 'galaxy':
            return ansible_galaxy.AnsibleGalaxy(self)
        elif dependency_name == 'gilt':
            return gilt.Gilt(self)
        else:
            util.exit_with_invalid_section('dependency', dependency_name)

    @property
    def driver(self):
        driver_name = self._get_driver_name()
        driver = None

        if driver_name == 'azure':
            driver = azure.Azure(self)
        elif driver_name == 'delegated':
            driver = delegated.Delegated(self)
        elif driver_name == 'docker':
            driver = docker.Docker(self)
        elif driver_name == 'ec2':
            driver = ec2.Ec2(self)
        elif driver_name == 'gce':
            driver = gce.Gce(self)
        elif driver_name == 'lxc':
            driver = lxc.Lxc(self)
        elif driver_name == 'lxd':
            driver = lxd.Lxd(self)
        elif driver_name == 'openstack':
            driver = openstack.Openstack(self)
        elif driver_name == 'vagrant':
            driver = vagrant.Vagrant(self)
        else:
            util.exit_with_invalid_section('driver', driver_name)

        driver.name = driver_name

        return driver

    @property
    def drivers(self):
        return molecule_drivers()

    @property
    def env(self):
        return {
            'MOLECULE_DEBUG': str(self.debug),
            'MOLECULE_FILE': self.molecule_file,
            'MOLECULE_INVENTORY_FILE': self.provisioner.inventory_file,
            'MOLECULE_EPHEMERAL_DIRECTORY': self.scenario.ephemeral_directory,
            'MOLECULE_SCENARIO_DIRECTORY': self.scenario.directory,
            'MOLECULE_INSTANCE_CONFIG': self.driver.instance_config,
            'MOLECULE_DEPENDENCY_NAME': self.dependency.name,
            'MOLECULE_DRIVER_NAME': self.driver.name,
            'MOLECULE_LINT_NAME': self.lint.name,
            'MOLECULE_PROVISIONER_NAME': self.provisioner.name,
            'MOLECULE_SCENARIO_NAME': self.scenario.name,
            'MOLECULE_VERIFIER_NAME': self.verifier.name,
        }

    @property
    def lint(self):
        lint_name = self.config['lint']['name']
        if lint_name == 'yamllint':
            return yamllint.Yamllint(self)
        else:
            util.exit_with_invalid_section('lint', lint_name)

    @property
    def platforms(self):
        return platforms.Platforms(self)

    @property
    def provisioner(self):
        provisioner_name = self.config['provisioner']['name']
        if provisioner_name == 'ansible':
            return ansible.Ansible(self)
        else:
            util.exit_with_invalid_section('provisioner', provisioner_name)

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
            util.exit_with_invalid_section('verifier', verifier_name)

    @property
    def verifiers(self):
        return molecule_verifiers()

    def merge_dicts(self, a, b):
        return merge_dicts(a, b)

    def _get_driver_name(self):
        driver_from_state_file = self.state.driver
        driver_from_cli = self.command_args.get('driver_name')

        if driver_from_state_file:
            driver_name = driver_from_state_file
        elif driver_from_cli:
            driver_name = driver_from_cli
        else:
            driver_name = self.config['driver']['name']

        if driver_from_cli and (driver_from_cli != driver_name):
            msg = ("Instance(s) were created with the '{}' driver, but the "
                   "subcommand is using '{}' driver.").format(
                       driver_name, driver_from_cli)
            util.sysexit_with_message(msg)

        return driver_name

    def _combine(self):
        """
        Perform a prioritized recursive merge of the `molecule_file` with
        defaults, interpolate the result with environment variables, and
        returns a new dict.

        :return: dict
        """
        i = interpolation.Interpolator(interpolation.TemplateWithDefaults,
                                       os.environ)

        base = self._get_defaults()
        with util.open_file(self.molecule_file) as stream:
            try:
                interpolated_config = i.interpolate(stream.read())
                base = self.merge_dicts(base,
                                        util.safe_load(interpolated_config))
            except interpolation.InvalidInterpolation as e:
                msg = ("parsing config file '{}'.\n\n"
                       '{}\n{}'.format(self.molecule_file, e.place, e.string))
                util.sysexit_with_message(msg)

        schema.validate(base)

        return base

    def _get_defaults(self):
        return {
            'dependency': {
                'name': 'galaxy',
                'enabled': True,
                'options': {},
                'env': {},
            },
            'driver': {
                'name': 'docker',
                'provider': {
                    'name': None
                },
                'options': {
                    'managed': True,
                },
                'ssh_connection_options': [],
                'safe_files': [],
            },
            'lint': {
                'name': 'yamllint',
                'enabled': True,
                'options': {},
                'env': {},
            },
            'platforms': [],
            'provisioner': {
                'name': 'ansible',
                'config_options': {},
                'connection_options': {},
                'options': {},
                'env': {},
                'inventory': {
                    'host_vars': {},
                    'group_vars': {},
                    'links': {},
                },
                'children': {},
                'playbooks': {
                    'create': 'create.yml',
                    'converge': 'playbook.yml',
                    'destroy': 'destroy.yml',
                    'prepare': 'prepare.yml',
                    'side_effect': None,
                },
                'lint': {
                    'name': 'ansible-lint',
                    'enabled': True,
                    'options': {},
                    'env': {},
                },
            },
            'scenario': {
                'name':
                'default',
                'check_sequence': [
                    'destroy',
                    'dependency',
                    'create',
                    'prepare',
                    'converge',
                    'check',
                    'destroy',
                ],
                'converge_sequence': [
                    'dependency',
                    'create',
                    'prepare',
                    'converge',
                ],
                'create_sequence': [
                    'create',
                    'prepare',
                ],
                'destroy_sequence': [
                    'destroy',
                ],
                'test_sequence': [
                    'lint',
                    'destroy',
                    'dependency',
                    'syntax',
                    'create',
                    'prepare',
                    'converge',
                    'idempotence',
                    'side_effect',
                    'verify',
                    'destroy',
                ],
            },
            'verifier': {
                'name': 'testinfra',
                'enabled': True,
                'directory': 'tests',
                'options': {},
                'env': {},
                'additional_files_or_dirs': [],
                'lint': {
                    'name': 'flake8',
                    'enabled': True,
                    'options': {},
                    'env': {},
                },
            },
        }


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
    conf = a
    anyconfig.merge(a, b, ac_merge=MERGE_STRATEGY)

    return conf


def molecule_directory(path):
    return os.path.join(path, MOLECULE_DIRECTORY)


def molecule_file(path):
    return os.path.join(path, MOLECULE_FILE)


def molecule_drivers():
    return [
        azure.Azure(None).name,
        delegated.Delegated(None).name,
        docker.Docker(None).name,
        ec2.Ec2(None).name,
        gce.Gce(None).name,
        lxc.Lxc(None).name,
        lxd.Lxd(None).name,
        openstack.Openstack(None).name,
        vagrant.Vagrant(None).name,
    ]


def molecule_verifiers():
    return [goss.Goss(None).name, testinfra.Testinfra(None).name]

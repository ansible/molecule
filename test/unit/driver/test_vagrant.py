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

import pytest

from molecule import config
from molecule.driver import vagrant


@pytest.fixture
def molecule_driver_section_data():
    return {
        'driver': {
            'name': 'vagrant',
            'options': {},
            'ssh_connection_options': ['-o foo=bar'],
            'safe_files': ['foo'],
        }
    }


@pytest.fixture
def vagrant_instance(molecule_driver_section_data, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_section_data)

    return vagrant.Vagrant(config_instance)


def test_config_private_member(vagrant_instance):
    assert isinstance(vagrant_instance._config, config.Config)


def test_testinfra_options_property(vagrant_instance):
    x = {
        'connection': 'ansible',
        'ansible-inventory':
        vagrant_instance._config.provisioner.inventory_file
    }

    assert x == vagrant_instance.testinfra_options


def test_name_property(vagrant_instance):
    assert 'vagrant' == vagrant_instance.name


def test_options_property(vagrant_instance):
    x = {'managed': True}

    assert x == vagrant_instance.options


def test_login_cmd_template_property(vagrant_instance):
    x = 'ssh {address} -l {user} -p {port} -i {identity_file} -o foo=bar'

    assert x == vagrant_instance.login_cmd_template


def test_safe_files_property(vagrant_instance):
    x = [
        os.path.join(vagrant_instance._config.scenario.ephemeral_directory,
                     'Vagrantfile'),
        os.path.join(vagrant_instance._config.scenario.ephemeral_directory,
                     'vagrant.yml'),
        os.path.join(vagrant_instance._config.scenario.ephemeral_directory,
                     'instance_config.yml'),
        os.path.join(vagrant_instance._config.scenario.ephemeral_directory,
                     '.vagrant'),
        'foo',
    ]

    assert x == vagrant_instance.safe_files


def test_default_safe_files_property(vagrant_instance):
    x = [
        os.path.join(vagrant_instance._config.scenario.ephemeral_directory,
                     'Vagrantfile'),
        os.path.join(vagrant_instance._config.scenario.ephemeral_directory,
                     'vagrant.yml'),
        os.path.join(vagrant_instance._config.scenario.ephemeral_directory,
                     'instance_config.yml'),
        os.path.join(vagrant_instance._config.scenario.ephemeral_directory,
                     '.vagrant'),
    ]

    assert x == vagrant_instance.default_safe_files


def test_delegated_property(vagrant_instance):
    assert not vagrant_instance.delegated


def test_managed_property(vagrant_instance):
    assert vagrant_instance.managed


def test_default_ssh_connection_options_property(vagrant_instance):
    x = [
        '-o UserKnownHostsFile=/dev/null',
        '-o ControlMaster=auto',
        '-o ControlPersist=60s',
        '-o IdentitiesOnly=yes',
        '-o StrictHostKeyChecking=no',
    ]

    assert x == vagrant_instance.default_ssh_connection_options


def test_login_options(mocker, vagrant_instance):
    m = mocker.patch('molecule.util.safe_load_file')
    m.return_value = [{
        'instance': 'foo',
        'address': '127.0.0.1',
        'user': 'vagrant',
        'port': 2222,
        'identity_file': '/foo/bar'
    }, {
        'instance': 'bar',
        'address': '127.0.0.1',
        'user': 'vagrant',
        'port': 2222,
        'identity_file': '/foo/bar'
    }]
    x = {
        'instance': 'foo',
        'address': '127.0.0.1',
        'user': 'vagrant',
        'port': 2222,
        'identity_file': '/foo/bar'
    }

    assert x == vagrant_instance.login_options('foo')


def test_ansible_connection_options(mocker, vagrant_instance):
    m = mocker.patch('molecule.util.safe_load_file')
    m.return_value = [{
        'instance': 'foo',
        'address': '127.0.0.1',
        'user': 'vagrant',
        'port': 2222,
        'identity_file': '/foo/bar'
    }, {
        'instance': 'bar',
        'address': '127.0.0.1',
        'user': 'vagrant',
        'port': 2222,
        'identity_file': '/foo/bar'
    }]
    x = {
        'ansible_host': '127.0.0.1',
        'ansible_port': 2222,
        'ansible_user': 'vagrant',
        'ansible_private_key_file': '/foo/bar',
        'connection': 'ssh',
        'ansible_ssh_common_args': '-o foo=bar',
    }

    assert x == vagrant_instance.ansible_connection_options('foo')


def test_ansible_connection_options_handles_missing_instance_config(
        mocker, vagrant_instance):
    m = mocker.patch('molecule.util.safe_load_file')
    m.side_effect = IOError

    assert {} == vagrant_instance.ansible_connection_options('foo')


def test_ansible_connection_options_handles_missing_results_key(
        mocker, vagrant_instance):
    m = mocker.patch('molecule.util.safe_load_file')
    m.side_effect = StopIteration

    assert {} == vagrant_instance.ansible_connection_options('foo')


def test_vagrantfile_property(vagrant_instance):
    x = os.path.join(vagrant_instance._config.scenario.ephemeral_directory,
                     'Vagrantfile')

    assert x == vagrant_instance.vagrantfile


def test_vagrantfile_config_property(vagrant_instance):
    x = os.path.join(vagrant_instance._config.scenario.ephemeral_directory,
                     'vagrant.yml')

    assert x == vagrant_instance.vagrantfile_config


def test_instance_config_property(vagrant_instance):
    x = os.path.join(vagrant_instance._config.scenario.ephemeral_directory,
                     'instance_config.yml')

    assert x == vagrant_instance.instance_config


def test_ssh_connection_options_property(vagrant_instance):
    x = ['-o foo=bar']

    assert x == vagrant_instance.ssh_connection_options


def test_status(mocker, vagrant_instance):
    result = vagrant_instance.status()

    assert 2 == len(result)

    assert result[0].instance_name == 'instance-1'
    assert result[0].driver_name == 'Vagrant'
    assert result[0].provisioner_name == 'Ansible'
    assert result[0].scenario_name == 'default'
    assert result[0].created == 'False'
    assert result[0].converged == 'False'

    assert result[1].instance_name == 'instance-2'
    assert result[1].driver_name == 'Vagrant'
    assert result[1].provisioner_name == 'Ansible'
    assert result[1].scenario_name == 'default'
    assert result[1].created == 'False'
    assert result[1].converged == 'False'

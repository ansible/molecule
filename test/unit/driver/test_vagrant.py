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
    return {'driver': {'name': 'vagrant', 'options': {}}}


@pytest.fixture
def vagrant_instance(molecule_driver_section_data, config_instance):
    config_instance.config.update(molecule_driver_section_data)

    return vagrant.Vagrant(config_instance)


def test_config_private_member(vagrant_instance):
    assert isinstance(vagrant_instance._config, config.Config)


def test_testinfra_options_property(vagrant_instance):
    vagrant_instance._config.provisioner.inventory_file
    x = {
        'connection': 'ansible',
        'ansible-inventory':
        vagrant_instance._config.provisioner.inventory_file
    }

    assert x == vagrant_instance.testinfra_options


def test_name_property(vagrant_instance):
    assert 'vagrant' == vagrant_instance.name


def test_options_property(vagrant_instance):
    assert {} == vagrant_instance.options


def test_login_cmd_template_property(vagrant_instance):
    x = 'ssh {} -l {} -p {} -i {}'

    assert x == vagrant_instance.login_cmd_template


def test_safe_files(vagrant_instance):
    x = [
        os.path.join(vagrant_instance._config.ephemeral_directory,
                     'Vagrantfile'),
        os.path.join(vagrant_instance._config.ephemeral_directory,
                     'vagrant.yml'),
        os.path.join(vagrant_instance._config.ephemeral_directory,
                     'instance_config.yml')
    ]

    assert x == vagrant_instance.safe_files


def test_login_args(mocker, vagrant_instance):
    m = mocker.patch('molecule.util.safe_load_file')
    m.return_value = {
        'results': [{
            'Host': 'foo',
            'HostName': '127.0.0.1',
            'User': 'vagrant',
            'Port': 2222,
            'IdentityFile': '/foo/bar'
        }, {
            'Host': 'bar',
            'HostName': '127.0.0.1',
            'User': 'vagrant',
            'Port': 2222,
            'IdentityFile': '/foo/bar'
        }]
    }
    x = ['127.0.0.1', 'vagrant', 2222, '/foo/bar']

    assert x == vagrant_instance.login_args('foo')


def test_connection_options(mocker, vagrant_instance):
    m = mocker.patch('molecule.util.safe_load_file')
    m.return_value = {
        'results': [{
            'Host': 'foo',
            'HostName': '127.0.0.1',
            'User': 'vagrant',
            'Port': 2222,
            'IdentityFile': '/foo/bar'
        }, {
            'Host': 'bar',
            'HostName': '127.0.0.1',
            'User': 'vagrant',
            'Port': 2222,
            'IdentityFile': '/foo/bar'
        }]
    }
    x = {
        'ansible_ssh_host': '127.0.0.1',
        'ansible_ssh_port': 2222,
        'ansible_ssh_user': 'vagrant',
        'ansible_ssh_private_key_file': '/foo/bar',
        'connection': 'ssh'
    }

    assert x == vagrant_instance.connection_options('foo')


def test_connection_options_handles_missing_instance_config(mocker,
                                                            vagrant_instance):
    m = mocker.patch('molecule.util.safe_load_file')
    m.side_effect = IOError

    assert {} == vagrant_instance.connection_options('foo')


def test_vagrantfile_property(vagrant_instance):
    x = os.path.join(vagrant_instance._config.ephemeral_directory,
                     'Vagrantfile')

    assert x == vagrant_instance.vagrantfile


def test_vagrantfile_config_property(vagrant_instance):
    x = os.path.join(vagrant_instance._config.ephemeral_directory,
                     'vagrant.yml')

    assert x == vagrant_instance.vagrantfile_config


def test_instance_config_property(vagrant_instance):
    x = os.path.join(vagrant_instance._config.ephemeral_directory,
                     'instance_config.yml')

    assert x == vagrant_instance.instance_config


def test_status(mocker, vagrant_instance):
    result = vagrant_instance.status()

    assert 2 == len(result)

    assert result[0].instance_name == 'instance-1-default'
    assert result[0].driver_name == 'Vagrant'
    assert result[0].provisioner_name == 'Ansible'
    assert result[0].scenario_name == 'default'
    assert result[0].state == 'Not Created'

    assert result[1].instance_name == 'instance-2-default'
    assert result[1].driver_name == 'Vagrant'
    assert result[0].provisioner_name == 'Ansible'
    assert result[0].scenario_name == 'default'
    assert result[1].state == 'Not Created'


def test_instances_state(vagrant_instance):
    assert 'Not Created' == vagrant_instance._instances_state()


def test_instances_state_created(vagrant_instance):
    vagrant_instance._config.state.change_state('created', True)

    assert 'Created' == vagrant_instance._instances_state()

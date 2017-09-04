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
from molecule.driver import openstack


@pytest.fixture
def molecule_driver_section_data():
    return {
        'driver': {
            'name': 'openstack',
            'options': {},
        }
    }


@pytest.fixture
def openstack_instance(molecule_driver_section_data, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_section_data)

    return openstack.Openstack(config_instance)


def test_config_private_member(openstack_instance):
    assert isinstance(openstack_instance._config, config.Config)


def test_testinfra_options_property(openstack_instance):
    assert {
        'connection': 'ansible',
        'ansible-inventory':
        openstack_instance._config.provisioner.inventory_file
    } == openstack_instance.testinfra_options


def test_name_property(openstack_instance):
    assert 'openstack' == openstack_instance.name


def test_options_property(openstack_instance):
    x = {'managed': True}

    assert x == openstack_instance.options


def test_login_cmd_template_property(openstack_instance):
    x = ('ssh {address} -l {user} -p {port} -i {identity_file} '
         '-o UserKnownHostsFile=/dev/null '
         '-o ControlMaster=auto '
         '-o ControlPersist=60s '
         '-o IdentitiesOnly=yes '
         '-o StrictHostKeyChecking=no')

    assert x == openstack_instance.login_cmd_template


def test_safe_files_property(openstack_instance):
    x = [
        os.path.join(openstack_instance._config.scenario.ephemeral_directory,
                     'instance_config.yml'),
    ]

    assert x == openstack_instance.safe_files


def test_default_safe_files_property(openstack_instance):
    x = [
        os.path.join(openstack_instance._config.scenario.ephemeral_directory,
                     'instance_config.yml'),
    ]

    assert x == openstack_instance.default_safe_files


def test_delegated_property(openstack_instance):
    assert not openstack_instance.delegated


def test_managed_property(openstack_instance):
    assert openstack_instance.managed


def test_default_ssh_connection_options_property(openstack_instance):
    x = [
        '-o UserKnownHostsFile=/dev/null',
        '-o ControlMaster=auto',
        '-o ControlPersist=60s',
        '-o IdentitiesOnly=yes',
        '-o StrictHostKeyChecking=no',
    ]

    assert x == openstack_instance.default_ssh_connection_options


def test_login_options(mocker, openstack_instance):
    m = mocker.patch('molecule.util.safe_load_file')
    m.return_value = [{
        'instance': 'foo',
        'address': '172.16.0.2',
        'user': 'cloud-user',
        'port': 22,
        'identity_file': '/foo/bar'
    }, {
        'instance': 'bar',
        'address': '172.16.0.3',
        'user': 'cloud-user',
        'port': 22,
        'identity_file': '/foo/bar'
    }]
    x = {
        'instance': 'foo',
        'address': '172.16.0.2',
        'user': 'cloud-user',
        'port': 22,
        'identity_file': '/foo/bar'
    }

    assert x == openstack_instance.login_options('foo')


def test_ansible_connection_options(mocker, openstack_instance):
    m = mocker.patch('molecule.util.safe_load_file')
    m.return_value = [{
        'instance': 'foo',
        'address': '172.16.0.2',
        'user': 'cloud-user',
        'port': 22,
        'identity_file': '/foo/bar'
    }, {
        'instance': 'bar',
        'address': '172.16.0.3',
        'user': 'cloud-user',
        'port': 22,
        'identity_file': '/foo/bar'
    }]
    x = {
        'ansible_host':
        '172.16.0.2',
        'ansible_port':
        22,
        'ansible_user':
        'cloud-user',
        'ansible_private_key_file':
        '/foo/bar',
        'connection':
        'ssh',
        'ansible_ssh_common_args': ('-o UserKnownHostsFile=/dev/null '
                                    '-o ControlMaster=auto '
                                    '-o ControlPersist=60s '
                                    '-o IdentitiesOnly=yes '
                                    '-o StrictHostKeyChecking=no'),
    }

    assert x == openstack_instance.ansible_connection_options('foo')


def test_ansible_connection_options_handles_missing_instance_config(
        mocker, openstack_instance):
    m = mocker.patch('molecule.util.safe_load_file')
    m.side_effect = IOError

    assert {} == openstack_instance.ansible_connection_options('foo')


def test_ansible_connection_options_handles_missing_results_key(
        mocker, openstack_instance):
    m = mocker.patch('molecule.util.safe_load_file')
    m.side_effect = StopIteration

    assert {} == openstack_instance.ansible_connection_options('foo')


def test_instance_config_property(openstack_instance):
    x = os.path.join(openstack_instance._config.scenario.ephemeral_directory,
                     'instance_config.yml')

    assert x == openstack_instance.instance_config


def test_ssh_connection_options_property(openstack_instance):
    x = [
        '-o UserKnownHostsFile=/dev/null',
        '-o ControlMaster=auto',
        '-o ControlPersist=60s',
        '-o IdentitiesOnly=yes',
        '-o StrictHostKeyChecking=no',
    ]

    assert x == openstack_instance.ssh_connection_options


def test_status(mocker, openstack_instance):
    result = openstack_instance.status()

    assert 2 == len(result)

    assert result[0].instance_name == 'instance-1'
    assert result[0].driver_name == 'Openstack'
    assert result[0].provisioner_name == 'Ansible'
    assert result[0].scenario_name == 'default'
    assert result[0].created == 'False'
    assert result[0].converged == 'False'

    assert result[1].instance_name == 'instance-2'
    assert result[1].driver_name == 'Openstack'
    assert result[1].provisioner_name == 'Ansible'
    assert result[1].scenario_name == 'default'
    assert result[1].created == 'False'
    assert result[1].converged == 'False'

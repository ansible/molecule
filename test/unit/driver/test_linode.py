#  Copyright (c) 2018-2019 Red Hat, Inc.
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
from molecule.driver import linode


@pytest.fixture
def linode_instance(patched_config_validate, config_instance):
    return linode.Linode(config_instance)


def test_linode_config_gives_config_object(linode_instance):
    assert isinstance(linode_instance._config, config.Config)


def test_linode_testinfra_options_property(linode_instance):
    assert {
        'connection': 'ansible',
        'ansible-inventory': linode_instance._config.provisioner.inventory_file
    } == linode_instance.testinfra_options


def test_linode_name_property(linode_instance):
    assert 'linode' == linode_instance.name


def test_linode_options_property(linode_instance):
    assert {'managed': True} == linode_instance.options


def test_linode_login_cmd_template_property(linode_instance):
    template = 'ssh {address} -l {user} -p {port} -i {identity_file}'
    assert template in linode_instance.login_cmd_template


def test_linode_safe_files_property(linode_instance):
    expected_safe_files = [
        os.path.join(linode_instance._config.scenario.ephemeral_directory,
                     'instance_config.yml')
    ]

    assert expected_safe_files == linode_instance.safe_files


def test_linode_default_safe_files_property(linode_instance):
    expected_default_safe_files = [
        os.path.join(linode_instance._config.scenario.ephemeral_directory,
                     'instance_config.yml')
    ]
    assert expected_default_safe_files == linode_instance.default_safe_files


def test_linode_delegated_property(linode_instance):
    assert not linode_instance.delegated


def test_linode_managed_property(linode_instance):
    assert linode_instance.managed


def test_linode_default_ssh_connection_options_property(linode_instance):
    expected_options = [
        '-o UserKnownHostsFile=/dev/null', '-o ControlMaster=auto',
        '-o ControlPersist=60s', '-o IdentitiesOnly=yes',
        '-o StrictHostKeyChecking=no'
    ]

    assert expected_options == linode_instance.default_ssh_connection_options


def test_linode_login_options(linode_instance, mocker):
    target = 'molecule.driver.linode.Linode._get_instance_config'
    get_instance_config_patch = mocker.patch(target)

    get_instance_config_patch.return_value = {
        'instance': 'linode',
        'address': '172.16.0.2',
        'user': 'linode-admin',
        'port': 22,
        'identity_file': '/foo/bar',
    }

    get_instance_config_patch = {
        'instance': 'linode',
        'address': '172.16.0.2',
        'user': 'linode-admin',
        'port': 22,
        'identity_file': '/foo/bar',
    }

    assert get_instance_config_patch == linode_instance.login_options('linode')


def test_linode_ansible_connection_options(linode_instance, mocker):
    target = 'molecule.driver.linode.Linode._get_instance_config'
    get_instance_config_patch = mocker.patch(target)

    get_instance_config_patch.return_value = {
        'instance': 'linode',
        'address': '172.16.0.2',
        'user': 'linode-admin',
        'port': 22,
        'ssh_pass': 'foobar',
        'identity_file': '/foo/bar',
    }

    get_instance_config_patch = {
        'ansible_host':
        '172.16.0.2',
        'ansible_port':
        22,
        'ansible_user':
        'linode-admin',
        'ansible_private_key_file':
        '/foo/bar',
        'connection':
        'ssh',
        'ansible_ssh_common_args': ('-o UserKnownHostsFile=/dev/null '
                                    '-o ControlMaster=auto '
                                    '-o ControlPersist=60s '
                                    '-o IdentitiesOnly=yes '
                                    '-o StrictHostKeyChecking=no'),
        'ansible_ssh_pass':
        'foobar',
    }

    connection_options = linode_instance.ansible_connection_options('linode')
    assert get_instance_config_patch == connection_options


def test_linode_instance_config_property(linode_instance):
    instance_config_path = os.path.join(
        linode_instance._config.scenario.ephemeral_directory,
        'instance_config.yml')

    assert instance_config_path == linode_instance.instance_config


def test_linode_ssh_connection_options_property(linode_instance):
    expected_options = [
        '-o UserKnownHostsFile=/dev/null', '-o ControlMaster=auto',
        '-o ControlPersist=60s', '-o IdentitiesOnly=yes',
        '-o StrictHostKeyChecking=no'
    ]

    assert expected_options == linode_instance.ssh_connection_options


def test_linode_status(mocker, linode_instance):
    linode_status = linode_instance.status()

    assert 2 == len(linode_status)

    assert linode_status[0].instance_name == 'instance-1'
    assert linode_status[0].driver_name == 'linode'
    assert linode_status[0].provisioner_name == 'ansible'
    assert linode_status[0].scenario_name == 'default'
    assert linode_status[0].created == 'false'
    assert linode_status[0].converged == 'false'

    assert linode_status[1].instance_name == 'instance-2'
    assert linode_status[1].driver_name == 'linode'
    assert linode_status[1].provisioner_name == 'ansible'
    assert linode_status[1].scenario_name == 'default'
    assert linode_status[1].created == 'false'
    assert linode_status[1].converged == 'false'


def test_created(linode_instance):
    assert 'false' == linode_instance._created()


def test_converged(linode_instance):
    assert 'false' == linode_instance._converged()

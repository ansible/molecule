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
import yaml

from molecule import provisioner
from molecule import config


@pytest.fixture
def provisioner_data():
    return {'provisioner': {'name': 'ansible', 'options': {'foo': 'bar'}}}


@pytest.fixture
def provisioner_instance(platforms_data, molecule_file, provisioner_data):
    c = config.Config(
        molecule_file, configs=[platforms_data, provisioner_data])

    return provisioner.Ansible(c)


def test_config_private_member(provisioner_instance):
    assert isinstance(provisioner_instance._config, config.Config)


def test_default_options_property(provisioner_instance):
    assert {} == provisioner_instance.default_options


def test_name_property(provisioner_instance):
    assert 'ansible' == provisioner_instance.name


def test_options_property(provisioner_instance):
    x = {
        'ask_become_pass': False,
        'ask_vault_pass': False,
        'config_file': 'ansible.cfg',
        'diff': True,
        'host_key_checking': False,
        'inventory_file': 'ansible_inventory.yml',
        'limit': 'all',
        'playbook': 'playbook.yml',
        'raw_ssh_args': [
            '-o UserKnownHostsFile=/dev/null', '-o IdentitiesOnly=yes',
            '-o ControlMaster=auto', '-o ControlPersist=60s'
        ],
        'become': True,
        'become_user': False,
        'tags': False,
        'timeout': 30,
        'vault_password_file': False,
        'verbose': False,
        'foo': 'bar'
    }

    assert x == provisioner_instance.options


def test_options_property_handles_cli_args(
        molecule_file, platforms_data, provisioner_data, provisioner_instance):
    c = config.Config(
        molecule_file,
        args={'debug': True},
        configs=[platforms_data, provisioner_data])
    p = provisioner.Ansible(c)

    assert p.options['debug']


def test_inventory_property(provisioner_instance):
    x = {
        'bar': {
            'hosts': {
                'instance-1-default': {
                    'ansible_connection': 'docker'
                }
            }
        },
        'foo': {
            'hosts': {
                'instance-1-default': {
                    'ansible_connection': 'docker'
                },
                'instance-2-default': {
                    'ansible_connection': 'docker'
                }
            }
        },
        'baz': {
            'hosts': {
                'instance-2-default': {
                    'ansible_connection': 'docker'
                }
            }
        }
    }

    assert x == provisioner_instance.inventory


def test_inventory_property_handles_missing_groups(temp_dir,
                                                   provisioner_instance):
    platforms = [{'name': 'instance-1'}, {'name': 'instance-2'}]
    provisioner_instance._config.config['platforms'] = platforms

    x = {
        'ungrouped': {
            'hosts': {
                'instance-1-default': {
                    'ansible_connection': 'docker'
                },
                'instance-2-default': {
                    'ansible_connection': 'docker'
                }
            }
        }
    }

    assert x == provisioner_instance.inventory


def test_inventory_file_property(provisioner_instance):
    x = os.path.join(provisioner_instance._config.ephemeral_directory,
                     'ansible_inventory.yml')

    assert x == provisioner_instance.inventory_file


def test_config_file_property(provisioner_instance):
    x = os.path.join(provisioner_instance._config.ephemeral_directory,
                     'ansible.cfg')

    assert x == provisioner_instance.config_file


def test_init_calls_setup(mocker, molecule_file, platforms_data,
                          provisioner_data):
    m = mocker.patch('molecule.provisioner.Ansible._setup')
    c = config.Config(
        molecule_file,
        args={'debug': True},
        configs=[platforms_data, provisioner_data])
    provisioner.Ansible(c)

    m.assert_called_once_with()


def test_converge(provisioner_instance, mocker, patched_ansible_playbook):
    result = provisioner_instance.converge('playbook')

    inventory_file = provisioner_instance._config.provisioner.inventory_file
    patched_ansible_playbook.assert_called_once_with(
        inventory_file, 'playbook', provisioner_instance._config)
    assert result == 'patched-ansible-playbook-stdout'

    patched_ansible_playbook.return_value.execute.assert_called_once_with()


def test_syntax(provisioner_instance, mocker, patched_ansible_playbook):
    provisioner_instance.syntax('playbook')

    inventory_file = provisioner_instance._config.provisioner.inventory_file
    patched_ansible_playbook.assert_called_once_with(
        inventory_file, 'playbook', provisioner_instance._config)
    patched_ansible_playbook.return_value.add_cli_arg.assert_called_once_with(
        'syntax-check', True)
    patched_ansible_playbook.return_value.execute.assert_called_once_with()


def test_check(provisioner_instance, mocker, patched_ansible_playbook):
    provisioner_instance.check('playbook')

    inventory_file = provisioner_instance._config.provisioner.inventory_file
    patched_ansible_playbook.assert_called_once_with(
        inventory_file, 'playbook', provisioner_instance._config)
    patched_ansible_playbook.return_value.add_cli_arg.assert_called_once_with(
        'check', True)
    patched_ansible_playbook.return_value.execute.assert_called_once_with()


def test_write_inventory(temp_dir, provisioner_instance):
    provisioner_instance.write_inventory()

    assert os.path.exists(provisioner_instance.inventory_file)

    with open(provisioner_instance.inventory_file, 'r') as stream:
        data = yaml.load(stream)
        x = {
            'bar': {
                'hosts': {
                    'instance-1-default': {
                        'ansible_connection': 'docker'
                    }
                }
            },
            'foo': {
                'hosts': {
                    'instance-1-default': {
                        'ansible_connection': 'docker'
                    },
                    'instance-2-default': {
                        'ansible_connection': 'docker'
                    }
                }
            },
            'baz': {
                'hosts': {
                    'instance-2-default': {
                        'ansible_connection': 'docker'
                    }
                }
            }
        }

        assert x == data


def test_write_config(temp_dir, provisioner_instance):
    provisioner_instance.write_config()

    assert os.path.exists(provisioner_instance.config_file)


def test_setup(mocker, temp_dir, provisioner_instance):
    patched_provisioner_write_inventory = mocker.patch(
        'molecule.provisioner.Ansible.write_inventory')
    patched_provisioner_write_config = mocker.patch(
        'molecule.provisioner.Ansible.write_config')
    provisioner_instance._setup()

    assert os.path.exists(os.path.dirname(provisioner_instance.inventory_file))

    patched_provisioner_write_inventory.assert_called_once_with()
    patched_provisioner_write_config.assert_called_once_with()


def test_verify_inventory(provisioner_instance):
    provisioner_instance._verify_inventory()


def test_verify_inventory_raises_when_missing_hosts(
        temp_dir, patched_print_error, provisioner_instance):
    provisioner_instance._config.config['platforms'] = []
    with pytest.raises(SystemExit) as e:
        provisioner_instance._verify_inventory()

    assert 1 == e.value.code

    msg = "Instances missing from the 'platform' section of molecule.yml."
    patched_print_error.assert_called_once_with(msg)


def test_vivify(provisioner_instance):
    d = provisioner_instance._vivify()
    d['bar']['baz'] = 'qux'

    assert 'qux' == str(d['bar']['baz'])

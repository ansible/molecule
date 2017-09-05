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
from molecule.driver import delegated


@pytest.fixture
def molecule_driver_section_data():
    return {
        'driver': {
            'name': 'delegated',
            'options': {
                'login_cmd_template': 'docker exec -ti {instance} bash',
                'ansible_connection_options': {
                    'ansible_connection': 'docker'
                }
            }
        }
    }


@pytest.fixture
def delegated_instance(molecule_driver_section_data, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_section_data)

    return delegated.Delegated(config_instance)


def test_config_private_member(delegated_instance):
    assert isinstance(delegated_instance._config, config.Config)


def test_testinfra_options_property(delegated_instance):
    assert {
        'connection': 'ansible',
        'ansible-inventory':
        delegated_instance._config.provisioner.inventory_file
    } == delegated_instance.testinfra_options


def test_name_property(delegated_instance):
    assert 'delegated' == delegated_instance.name


def test_options_property(delegated_instance):
    x = {
        'ansible_connection_options': {
            'ansible_connection': 'docker'
        },
        'login_cmd_template': 'docker exec -ti {instance} bash',
        'managed': True,
    }

    assert x == delegated_instance.options


def test_login_cmd_template_property(delegated_instance):
    x = 'docker exec -ti {instance} bash'

    assert x == delegated_instance.login_cmd_template


def test_safe_files_property(delegated_instance):
    assert [] == delegated_instance.safe_files


def test_default_safe_files_property(delegated_instance):
    assert [] == delegated_instance.default_safe_files


def test_delegated_property(delegated_instance):
    assert delegated_instance.delegated


def test_managed_property(delegated_instance):
    assert delegated_instance.managed


def test_default_ssh_connection_options_property(delegated_instance):
    assert [] == delegated_instance.default_ssh_connection_options


def test_login_options(delegated_instance):
    assert {'instance': 'foo'} == delegated_instance.login_options('foo')


def test_ansible_connection_options(delegated_instance):
    x = {'ansible_connection': 'docker'}

    assert x == delegated_instance.ansible_connection_options('foo')


def test_instance_config_property(delegated_instance):
    x = os.path.join(delegated_instance._config.scenario.ephemeral_directory,
                     'instance_config.yml')

    assert x == delegated_instance.instance_config


def test_ssh_connection_options_property(delegated_instance):
    assert [] == delegated_instance.ssh_connection_options


def test_status(mocker, delegated_instance):
    result = delegated_instance.status()

    assert 2 == len(result)

    assert result[0].instance_name == 'instance-1'
    assert result[0].driver_name == 'Delegated'
    assert result[0].provisioner_name == 'Ansible'
    assert result[0].scenario_name == 'default'
    assert result[0].created == 'False'
    assert result[0].converged == 'False'

    assert result[1].instance_name == 'instance-2'
    assert result[1].driver_name == 'Delegated'
    assert result[1].provisioner_name == 'Ansible'
    assert result[1].scenario_name == 'default'
    assert result[1].created == 'False'
    assert result[1].converged == 'False'

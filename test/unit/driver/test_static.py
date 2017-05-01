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
from molecule.driver import static


@pytest.fixture
def molecule_driver_section_data():
    return {
        'driver': {
            'name': 'static',
            'options': {
                'login_cmd_template': 'docker exec -ti {} bash',
                'ansible_connection_options': {
                    'ansible_connection': 'docker'
                }
            }
        }
    }


@pytest.fixture
def static_instance(molecule_driver_section_data, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_section_data)

    return static.Static(config_instance)


def test_config_private_member(static_instance):
    assert isinstance(static_instance._config, config.Config)


def test_testinfra_options_property(static_instance):
    assert {
        'connection': 'ansible',
        'ansible-inventory': static_instance._config.provisioner.inventory_file
    } == static_instance.testinfra_options


def test_name_property(static_instance):
    assert 'static' == static_instance.name


def test_options_property(static_instance):
    x = {
        'ansible_connection_options': {
            'ansible_connection': 'docker'
        },
        'login_cmd_template': 'docker exec -ti {} bash'
    }

    assert x == static_instance.options


def test_login_cmd_template_property(static_instance):
    assert 'docker exec -ti {} bash' == static_instance.login_cmd_template


def test_safe_files(static_instance):
    assert [] == static_instance.safe_files


def test_login_args(static_instance):
    assert ['foo'] == static_instance.login_args('foo')


def test_ansible_connection_options(static_instance):
    x = {'ansible_connection': 'docker'}

    assert x == static_instance.ansible_connection_options('foo')


def test_instance_config_property(static_instance):
    x = os.path.join(static_instance._config.ephemeral_directory,
                     'instance_config.yml')

    assert x == static_instance.instance_config


def test_status(mocker, static_instance):
    result = static_instance.status()

    assert 2 == len(result)

    assert result[0].instance_name == 'instance-1-default'
    assert result[0].driver_name == 'Static'
    assert result[0].provisioner_name == 'Ansible'
    assert result[0].scenario_name == 'default'
    assert result[0].created == 'False'
    assert result[0].converged == 'False'

    assert result[1].instance_name == 'instance-2-default'
    assert result[1].driver_name == 'Static'
    assert result[1].provisioner_name == 'Ansible'
    assert result[1].scenario_name == 'default'
    assert result[1].created == 'False'
    assert result[1].converged == 'False'

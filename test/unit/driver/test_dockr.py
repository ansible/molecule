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
from molecule.driver import dockr


@pytest.fixture
def molecule_driver_section_data():
    return {'driver': {'name': 'docker', 'options': {}}}


@pytest.fixture
def docker_instance(molecule_driver_section_data, config_instance):
    config_instance.config.update(molecule_driver_section_data)

    return dockr.Dockr(config_instance)


def test_config_private_member(docker_instance):
    assert isinstance(docker_instance._config, config.Config)


def test_testinfra_options_property(docker_instance):
    assert {
        'connection': 'ansible',
        'ansible-inventory': '.molecule/ansible_inventory.yml'
    } == docker_instance.testinfra_options


def test_name_property(docker_instance):
    assert 'docker' == docker_instance.name


def test_options_property(docker_instance):
    assert {} == docker_instance.options


def test_login_cmd_template_property(docker_instance):
    assert 'docker exec -ti {} bash' == docker_instance.login_cmd_template


def test_safe_files(docker_instance):
    assert [] == docker_instance.safe_files


def test_login_args(docker_instance):
    assert ['foo'] == docker_instance.login_args('foo')


def test_connection_options(docker_instance):
    x = {'ansible_connection': 'docker'}

    assert x == docker_instance.connection_options('foo')


def test_instance_config_property(docker_instance):
    x = os.path.join(docker_instance._config.ephemeral_directory,
                     'instance_config.yml')

    assert x == docker_instance.instance_config


def test_status(mocker, docker_instance):
    result = docker_instance.status()

    assert 2 == len(result)

    assert result[0].instance_name == 'instance-1-default'
    assert result[0].driver_name == 'Docker'
    assert result[0].provisioner_name == 'Ansible'
    assert result[0].scenario_name == 'default'
    assert result[0].state == 'Not Created'

    assert result[1].instance_name == 'instance-2-default'
    assert result[1].driver_name == 'Docker'
    assert result[0].provisioner_name == 'Ansible'
    assert result[0].scenario_name == 'default'
    assert result[1].state == 'Not Created'


def test_instances_state(docker_instance):
    assert 'Not Created' == docker_instance._instances_state()


def test_instances_state_created(docker_instance):
    docker_instance._config.state.change_state('created', True)

    assert 'Created' == docker_instance._instances_state()

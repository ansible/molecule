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
from molecule.driver import lxd


@pytest.fixture
def molecule_driver_section_data():
    return {
        'driver': {
            'name': 'lxd',
            'options': {},
        }
    }


@pytest.fixture
def lxd_instance(molecule_driver_section_data, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_section_data)

    return lxd.Lxd(config_instance)


def test_config_private_member(lxd_instance):
    assert isinstance(lxd_instance._config, config.Config)


def test_testinfra_options_property(lxd_instance):
    assert {
        'connection': 'ansible',
        'ansible-inventory': lxd_instance._config.provisioner.inventory_file
    } == lxd_instance.testinfra_options


def test_name_property(lxd_instance):
    assert 'lxd' == lxd_instance.name


def test_options_property(lxd_instance):
    x = {'managed': True}

    assert x == lxd_instance.options


def test_login_cmd_template_property(lxd_instance):
    assert 'lxc exec {instance} bash' == lxd_instance.login_cmd_template


def test_safe_files_property(lxd_instance):
    assert [] == lxd_instance.safe_files


def test_default_safe_files_property(lxd_instance):
    assert [] == lxd_instance.default_safe_files


def test_delegated_property(lxd_instance):
    assert not lxd_instance.delegated


def test_managed_property(lxd_instance):
    assert lxd_instance.managed


def test_default_ssh_connection_options_property(lxd_instance):
    assert [] == lxd_instance.default_ssh_connection_options


def test_login_options(lxd_instance):
    assert {'instance': 'foo'} == lxd_instance.login_options('foo')


def test_ansible_connection_options(lxd_instance):
    x = {'ansible_connection': 'lxd'}

    assert x == lxd_instance.ansible_connection_options('foo')


def test_instance_config_property(lxd_instance):
    x = os.path.join(lxd_instance._config.scenario.ephemeral_directory,
                     'instance_config.yml')

    assert x == lxd_instance.instance_config


def test_ssh_connection_options_property(lxd_instance):
    assert [] == lxd_instance.ssh_connection_options


def test_status(mocker, lxd_instance):
    result = lxd_instance.status()

    assert 2 == len(result)

    assert result[0].instance_name == 'instance-1'
    assert result[0].driver_name == 'Lxd'
    assert result[0].provisioner_name == 'Ansible'
    assert result[0].scenario_name == 'default'
    assert result[0].created == 'False'
    assert result[0].converged == 'False'

    assert result[1].instance_name == 'instance-2'
    assert result[1].driver_name == 'Lxd'
    assert result[1].provisioner_name == 'Ansible'
    assert result[1].scenario_name == 'default'
    assert result[1].created == 'False'
    assert result[1].converged == 'False'

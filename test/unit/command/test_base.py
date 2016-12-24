#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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
from molecule.command import base


@pytest.fixture()
def base_class(config_instance):
    class ExtendedBase(base.Base):
        def execute():
            pass

    return ExtendedBase


@pytest.fixture()
def base_instance(base_class, config_instance):
    return base_class(config_instance)


def test_config_private_member(base_instance):
    assert isinstance(base_instance._config, config.Config)


def test_init_calls_setup_provisioner(mocker, base_class, config_instance):
    patched_setup_provisioner = mocker.patch(
        'molecule.command.base.Base._setup_provisioner')

    base_class(config_instance)

    patched_setup_provisioner.assert_called_once


def test_setup_provisioner(mocker, base_instance):
    patched_provisioner_write_inventory = mocker.patch(
        'molecule.provisioner.Ansible.write_inventory')
    patched_provisioner_write_config = mocker.patch(
        'molecule.provisioner.Ansible.write_config')

    base_instance._setup_provisioner()

    patched_provisioner_write_inventory.assert_called_once
    patched_provisioner_write_config.assert_called_once


def test_get_local_config(mocker):
    m = mocker.patch('molecule.command.base._load_config')
    m.return_value = {'foo': 'bar'}

    assert {'foo': 'bar'} == base._get_local_config()


def test_get_local_config_returns_empty_dict_on_ioerror(monkeypatch):
    def mockreturn(path):
        return '/foo/bar/baz'

    monkeypatch.setattr('os.path.expanduser', mockreturn)

    assert {} == base._get_local_config()


def test_load_config(temp_dir):
    inventory_file = os.path.join(temp_dir.strpath, 'inventory_file')
    with open(inventory_file, 'w') as outfile:
        outfile.write('foo: bar')

    assert {'foo': 'bar'} == base._load_config(inventory_file)


def test_load_config_returns_empty_dict_on_empty_file(temp_dir):
    inventory_file = os.path.join(temp_dir.strpath, 'inventory_file')
    with open(inventory_file, 'w') as outfile:
        outfile.write('')

    assert {} == base._load_config(inventory_file)


def test_verify_configs():
    assert base._verify_configs([{}, {}]) is None


def test_verify_configs_raises(patched_print_error):
    with pytest.raises(SystemExit) as e:
        base._verify_configs([])

    assert 1 == e.value.code

    msg = 'Unable to find a molecule.yml.  Exiting.'
    patched_print_error.assert_called_with(msg)


def test_get_configs(temp_dir):
    molecule_directory = config.molecule_directory(temp_dir.strpath)
    scenario_directory = os.path.join(molecule_directory, 'scenario')
    molecule_file = config.molecule_file(scenario_directory)
    os.makedirs(scenario_directory)
    open(molecule_file, 'a').close()

    result = base.get_configs({}, {})
    assert 1 == len(result)
    assert isinstance(result, list)
    assert isinstance(result[0], config.Config)

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
from molecule import util
from molecule.command import base


class ExtendedBase(base.Base):
    def execute():
        pass


@pytest.fixture
def base_class(config_instance):
    return ExtendedBase


@pytest.fixture
def base_instance(base_class, config_instance):
    return base_class(config_instance)


def test_config_private_member(base_instance):
    assert isinstance(base_instance._config, config.Config)


def test_init_calls_setup(patched_base_setup, base_instance):
    patched_base_setup.assert_called_once_with()


def test_prune(base_instance):
    ephemeral_directory = base_instance._config.scenario.ephemeral_directory

    foo_file = os.path.join(ephemeral_directory, 'foo')
    bar_file = os.path.join(ephemeral_directory, 'bar')
    baz_directory = os.path.join(ephemeral_directory, 'baz')
    state_file = os.path.join(ephemeral_directory, 'state.yml')
    inventory_file = os.path.join(ephemeral_directory, 'ansible_inventory.yml')
    config_file = os.path.join(ephemeral_directory, 'ansible.cfg')

    os.mkdir(baz_directory)
    for f in [foo_file, bar_file, state_file]:
        util.write_file(f, '')

    base_instance.prune()

    assert not os.path.isfile(foo_file)
    assert not os.path.isfile(bar_file)
    assert os.path.isfile(state_file)
    assert os.path.isfile(config_file)
    assert os.path.isfile(inventory_file)
    assert not os.path.isdir(baz_directory)


def test_print_info(mocker, patched_logger_info, base_instance):
    base_instance.print_info()
    x = [
        mocker.call("Scenario: 'default'"),
        mocker.call("Action: 'extended_base'"),
    ]
    assert x == patched_logger_info.mock_calls


def test_setup(mocker, patched_add_or_update_vars, patched_write_config,
               patched_manage_inventory, base_instance):

    assert os.path.isdir(
        os.path.dirname(base_instance._config.provisioner.inventory_file))

    patched_manage_inventory.assert_called_once_with()
    patched_write_config.assert_called_once_with()


def test_execute_subcommand(config_instance):
    assert base.execute_subcommand(config_instance, 'list')


def test_get_configs(config_instance):
    molecule_file = config_instance.molecule_file
    data = config_instance.config
    util.write_file(molecule_file, util.safe_dump(data))

    result = base.get_configs({}, {})
    assert 1 == len(result)
    assert isinstance(result, list)
    assert isinstance(result[0], config.Config)


def test_get_configs_calls_verify_configs(patched_verify_configs):
    base.get_configs({}, {})

    patched_verify_configs.assert_called_once_with([])


def test_verify_configs(config_instance):
    configs = [config_instance]

    assert base._verify_configs(configs) is None


def test_verify_configs_raises_with_no_configs(patched_logger_critical):
    with pytest.raises(SystemExit) as e:
        base._verify_configs([])

    assert 1 == e.value.code

    msg = "'molecule/*/molecule.yml' glob failed.  Exiting."
    patched_logger_critical.assert_called_once_with(msg)


def test_verify_configs_raises_with_duplicate_configs(patched_logger_critical,
                                                      config_instance):
    with pytest.raises(SystemExit) as e:
        configs = [config_instance, config_instance]
        base._verify_configs(configs)

    assert 1 == e.value.code

    msg = "Duplicate scenario name 'default' found.  Exiting."
    patched_logger_critical.assert_called_once_with(msg)


def test_get_subcommand():
    assert 'test_base' == base._get_subcommand(__name__)

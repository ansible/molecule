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
import sh

from molecule import config
from molecule.dependency import gilt


@pytest.fixture
def molecule_dependency_section_data():
    return {
        'dependency': {
            'name': 'gilt',
            'options': {
                'foo': 'bar',
            },
            'env': {
                'foo': 'bar',
            }
        }
    }


@pytest.fixture
def gilt_instance(molecule_dependency_section_data, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_dependency_section_data)

    return gilt.Gilt(config_instance)


@pytest.fixture
def gilt_config(gilt_instance):
    return os.path.join(gilt_instance._config.scenario.directory, 'gilt.yml')


def test_config_private_member(gilt_instance):
    assert isinstance(gilt_instance._config, config.Config)


def test_default_options_property(gilt_config, gilt_instance):
    x = {'config': gilt_config}

    assert x == gilt_instance.default_options


def test_default_env_property(gilt_instance):
    assert 'MOLECULE_FILE' in gilt_instance.default_env
    assert 'MOLECULE_INVENTORY_FILE' in gilt_instance.default_env
    assert 'MOLECULE_SCENARIO_DIRECTORY' in gilt_instance.default_env
    assert 'MOLECULE_INSTANCE_CONFIG' in gilt_instance.default_env


def test_name_property(gilt_instance):
    assert 'gilt' == gilt_instance.name


def test_enabled_property(gilt_instance):
    assert gilt_instance.enabled


def test_options_property(gilt_config, gilt_instance):
    x = {'config': gilt_config, 'foo': 'bar'}

    assert x == gilt_instance.options


def test_options_property_handles_cli_args(gilt_config, gilt_instance):
    gilt_instance._config.args = {'debug': True}
    x = {'config': gilt_config, 'foo': 'bar', 'debug': True}

    assert x == gilt_instance.options


def test_env_property(gilt_instance):
    assert 'bar' == gilt_instance.env['foo']


def test_bake(gilt_config, gilt_instance):
    gilt_instance.bake()
    x = [
        str(sh.gilt), '--foo=bar', '--config={}'.format(gilt_config), 'overlay'
    ]
    result = str(gilt_instance._gilt_command).split()

    assert sorted(x) == sorted(result)


def test_execute(patched_run_command, patched_gilt_has_requirements_file,
                 patched_logger_success, gilt_instance):
    gilt_instance._gilt_command = 'patched-command'
    gilt_instance.execute()

    patched_run_command.assert_called_once_with('patched-command', debug=False)

    msg = 'Dependency completed successfully.'
    patched_logger_success.assert_called_once_with(msg)


def test_execute_does_not_execute_when_disabled(
        patched_run_command, patched_logger_warn, gilt_instance):
    gilt_instance._config.config['dependency']['enabled'] = False
    gilt_instance.execute()

    assert not patched_run_command.called

    msg = 'Skipping, dependency is disabled.'
    patched_logger_warn.assert_called_once_with(msg)


def test_execute_does_not_execute_when_no_requirements_file(
        patched_run_command, patched_gilt_has_requirements_file,
        patched_logger_warn, gilt_instance):
    patched_gilt_has_requirements_file.return_value = False
    gilt_instance.execute()

    assert not patched_run_command.called

    msg = 'Skipping, missing the requirements file.'
    patched_logger_warn.assert_called_once_with(msg)


def test_execute_bakes(patched_run_command, gilt_config,
                       patched_gilt_has_requirements_file, gilt_instance):
    gilt_instance.execute()
    assert gilt_instance._gilt_command is not None

    assert 1 == patched_run_command.call_count


def test_executes_catches_and_exits_return_code(
        patched_run_command, patched_gilt_has_requirements_file,
        gilt_instance):
    patched_run_command.side_effect = sh.ErrorReturnCode_1(
        sh.ansible_galaxy, b'', b'')
    with pytest.raises(SystemExit) as e:
        gilt_instance.execute()

    assert 1 == e.value.code


def test_has_requirements_file(gilt_instance):
    assert not gilt_instance._has_requirements_file()

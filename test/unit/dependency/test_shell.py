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

import pytest
import sh

from molecule import config
from molecule.dependency import shell


@pytest.fixture
def molecule_dependency_section_data():
    return {
        'dependency': {
            'name': 'shell',
            'command': 'ls -l -a /tmp',
            'options': {
                'foo': 'bar',
            },
            'env': {
                'foo': 'bar',
            }
        }
    }


@pytest.fixture
def shell_instance(molecule_dependency_section_data, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_dependency_section_data)

    return shell.Shell(config_instance)


def test_config_private_member(shell_instance):
    assert isinstance(shell_instance._config, config.Config)


def test_default_options_property(shell_instance):
    x = {}

    assert x == shell_instance.default_options


def test_default_env_property(shell_instance):
    assert 'MOLECULE_FILE' in shell_instance.default_env
    assert 'MOLECULE_INVENTORY_FILE' in shell_instance.default_env
    assert 'MOLECULE_SCENARIO_DIRECTORY' in shell_instance.default_env
    assert 'MOLECULE_INSTANCE_CONFIG' in shell_instance.default_env


def test_name_property(shell_instance):
    assert 'shell' == shell_instance.name


def test_enabled_property(shell_instance):
    assert shell_instance.enabled


def test_options_property(shell_instance):
    x = {'foo': 'bar'}

    assert x == shell_instance.options


def test_options_property_handles_cli_args(shell_instance):
    shell_instance._config.args = {}
    x = {'foo': 'bar'}

    assert x == shell_instance.options


def test_env_property(shell_instance):
    assert 'bar' == shell_instance.env['foo']


def test_bake(shell_instance):
    shell_instance.bake()

    x = [
        str(sh.ls),
        '-l',
        '-a',
        '/tmp',
    ]
    result = str(shell_instance._sh_command).split()

    assert sorted(x) == sorted(result)


def test_execute(patched_run_command, patched_logger_success, shell_instance):
    shell_instance._sh_command = 'patched-command'
    shell_instance.execute()

    patched_run_command.assert_called_once_with('patched-command', debug=False)

    msg = 'Dependency completed successfully.'
    patched_logger_success.assert_called_once_with(msg)


def test_execute_does_not_execute_when_disabled(
        patched_run_command, patched_logger_warn, shell_instance):
    shell_instance._config.config['dependency']['enabled'] = False
    shell_instance.execute()

    assert not patched_run_command.called

    msg = 'Skipping, dependency is disabled.'
    patched_logger_warn.assert_called_once_with(msg)


def test_execute_bakes(patched_run_command, shell_instance):
    shell_instance.execute()
    assert shell_instance._sh_command is not None

    assert 1 == patched_run_command.call_count


def test_executes_catches_and_exits_return_code(patched_run_command,
                                                shell_instance):
    patched_run_command.side_effect = sh.ErrorReturnCode_1(sh.ls, b'', b'')
    with pytest.raises(SystemExit) as e:
        shell_instance.execute()

    assert 1 == e.value.code


def test_has_command_configured(shell_instance):
    assert shell_instance._has_command_configured()

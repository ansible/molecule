#  Copyright (c) 2015-2018 Cisco Systems, Inc.
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
from molecule.lint import yamllint


@pytest.fixture
def _patched_get_files(mocker):
    m = mocker.patch('molecule.lint.yamllint.Yamllint._get_files')
    m.return_value = [
        'foo.yml',
        'bar.yaml',
    ]

    return m


@pytest.fixture
def _lint_section_data():
    return {
        'lint': {
            'name': 'yamllint',
            'options': {
                'foo': 'bar',
            },
            'env': {
                'FOO': 'bar',
            }
        }
    }


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.fixture
def _instance(_lint_section_data, patched_config_validate, config_instance):
    return yamllint.Yamllint(config_instance)


def test_config_private_member(_instance):
    assert isinstance(_instance._config, config.Config)


def test_files_private_member(_patched_get_files, _instance):
    x = [
        'foo.yml',
        'bar.yaml',
    ]

    assert x == _instance._files


def test_default_options_property(_instance):
    x = {
        's': True,
    }

    assert x == _instance.default_options


def test_default_env_property(_instance):
    assert 'MOLECULE_FILE' in _instance.default_env
    assert 'MOLECULE_INVENTORY_FILE' in _instance.default_env
    assert 'MOLECULE_SCENARIO_DIRECTORY' in _instance.default_env
    assert 'MOLECULE_INSTANCE_CONFIG' in _instance.default_env


def test_name_property(_instance):
    assert 'yamllint' == _instance.name


def test_enabled_property(_instance):
    assert _instance.enabled


@pytest.mark.parametrize(
    'config_instance', ['_lint_section_data'], indirect=True)
def test_options_property(_instance):
    x = {
        's': True,
        'foo': 'bar',
    }

    assert x == _instance.options


@pytest.mark.parametrize(
    'config_instance', ['_lint_section_data'], indirect=True)
def test_options_property_handles_cli_args(_instance):
    _instance._config.args = {'debug': True}
    x = {
        's': True,
        'foo': 'bar',
    }

    # Does nothing.  The `yamllint` command does not support
    # a `debug` flag.
    assert x == _instance.options


@pytest.mark.parametrize(
    'config_instance', ['_lint_section_data'], indirect=True)
def test_bake(_patched_get_files, _instance):
    _instance.bake()
    x = [
        str(sh.Command('yamllint')),
        '-s',
        '--foo=bar',
        'foo.yml',
        'bar.yaml',
    ]

    result = str(_instance._yamllint_command).split()
    assert sorted(x) == sorted(result)


def test_execute(_patched_get_files, patched_logger_info,
                 patched_logger_success, patched_run_command, _instance):
    _instance._yamllint_command = 'patched-yamllint-command'
    _instance.execute()

    patched_run_command.assert_called_once_with(
        'patched-yamllint-command', debug=False)

    msg = 'Executing Yamllint on files found in {}/...'.format(
        _instance._config.project_directory)
    patched_logger_info.assert_called_once_with(msg)

    msg = 'Lint completed successfully.'
    patched_logger_success.assert_called_once_with(msg)


def test_execute_does_not_execute(_patched_get_files, patched_logger_warn,
                                  patched_logger_success, patched_run_command,
                                  _instance):
    _instance._config.config['lint']['enabled'] = False
    _instance.execute()

    assert not patched_run_command.called

    msg = 'Skipping, lint is disabled.'
    patched_logger_warn.assert_called_once_with(msg)


@pytest.mark.parametrize(
    'config_instance', ['_lint_section_data'], indirect=True)
def test_execute_bakes(_patched_get_files, patched_run_command, _instance):
    _instance.execute()

    assert _instance._yamllint_command is not None

    x = [
        str(sh.Command('yamllint')),
        '-s',
        '--foo=bar',
        'foo.yml',
        'bar.yaml',
    ]
    result = str(patched_run_command.mock_calls[0][1][0]).split()

    assert sorted(x) == sorted(result)


def test_executes_catches_and_exits_return_code(patched_run_command,
                                                _instance):
    patched_run_command.side_effect = sh.ErrorReturnCode_1(
        sh.yamllint, b'', b'')
    with pytest.raises(SystemExit) as e:
        _instance.execute()

    assert 1 == e.value.code

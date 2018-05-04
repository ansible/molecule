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
from molecule.verifier.lint import yamllint


@pytest.fixture
def _patched_get_tests(mocker):
    m = mocker.patch('molecule.verifier.lint.yamllint.Yamllint._get_tests')
    m.return_value = ['test1', 'test2', 'test3']

    return m


@pytest.fixture
def _verifier_lint_section_data():
    return {
        'verifier': {
            'name': 'goss',
            'lint': {
                'name': 'yamllint',
                'options': {
                    'foo': 'bar',
                },
                'env': {
                    'FOO': 'bar',
                },
            }
        }
    }


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.fixture
def _instance(patched_config_validate, config_instance):
    return yamllint.Yamllint(config_instance)


def test_config_private_member(_instance):
    assert isinstance(_instance._config, config.Config)


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


@pytest.mark.parametrize(
    'config_instance', ['_verifier_lint_section_data'], indirect=True)
def test_env_property(_instance):
    assert 'bar' == _instance.env['FOO']


@pytest.mark.parametrize(
    'config_instance', ['_verifier_lint_section_data'], indirect=True)
def test_name_property(_instance):
    assert 'yamllint' == _instance.name


def test_enabled_property(_instance):
    assert _instance.enabled


@pytest.mark.parametrize(
    'config_instance', ['_verifier_lint_section_data'], indirect=True)
def test_options_property(_instance):
    x = {
        's': True,
        'foo': 'bar',
    }

    assert x == _instance.options


@pytest.mark.parametrize(
    'config_instance', ['_verifier_lint_section_data'], indirect=True)
def test_options_property_handles_cli_args(_instance):
    _instance._config.args = {'debug': True}
    x = {
        's': True,
        'foo': 'bar',
    }

    assert x == _instance.options


@pytest.mark.parametrize(
    'config_instance', ['_verifier_lint_section_data'], indirect=True)
def test_bake(_instance):
    _instance._tests = ['test1', 'test2', 'test3']
    _instance.bake()
    x = [
        str(sh.Command('yamllint')),
        '-s',
        '--foo=bar',
        'test1',
        'test2',
        'test3',
    ]

    result = str(_instance._yamllint_command).split()
    assert sorted(x) == sorted(result)


def test_execute(patched_logger_info, patched_logger_success,
                 patched_run_command, _instance):
    _instance._tests = ['test1', 'test2', 'test3']
    _instance._yamllint_command = 'patched-command'
    _instance.execute()

    patched_run_command.assert_called_once_with('patched-command', debug=False)

    msg = 'Executing Yamllint on files found in {}/...'.format(
        _instance._config.verifier.directory)
    patched_logger_info.assert_called_once_with(msg)

    msg = 'Lint completed successfully.'
    patched_logger_success.assert_called_once_with(msg)


def test_execute_does_not_execute(patched_run_command, patched_logger_warn,
                                  _instance):
    _instance._config.config['verifier']['lint']['enabled'] = False
    _instance.execute()

    assert not patched_run_command.called

    msg = 'Skipping, verifier_lint is disabled.'
    patched_logger_warn.assert_called_once_with(msg)


def test_does_not_execute_without_tests(patched_run_command,
                                        patched_logger_warn, _instance):
    _instance.execute()

    assert not patched_run_command.called

    msg = 'Skipping, no tests found.'
    patched_logger_warn.assert_called_once_with(msg)


@pytest.mark.parametrize(
    'config_instance', ['_verifier_lint_section_data'], indirect=True)
def test_execute_bakes(patched_run_command, _instance):
    _instance._tests = ['test1', 'test2', 'test3']
    _instance.execute()

    assert _instance._yamllint_command is not None

    x = [
        str(sh.Command('yamllint')),
        '-s',
        '--foo=bar',
        'test1',
        'test2',
        'test3',
    ]
    result = str(patched_run_command.mock_calls[0][1][0]).split()

    assert sorted(x) == sorted(result)


def test_executes_catches_and_exits_return_code(patched_run_command,
                                                _patched_get_tests, _instance):
    patched_run_command.side_effect = sh.ErrorReturnCode_1(
        sh.yamllint, b'', b'')
    with pytest.raises(SystemExit) as e:
        _instance.execute()

    assert 1 == e.value.code

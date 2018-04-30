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
from molecule.provisioner.lint import ansible_lint


@pytest.fixture
def _provisioner_lint_section_data():
    return {
        'provisioner': {
            'name': 'ansible',
            'lint': {
                'name': 'ansible-lint',
                'options': {
                    'foo': 'bar',
                    'v': True,
                    'exclude': [
                        'foo',
                        'bar',
                    ],
                    'x': [
                        'foo',
                        'bar',
                    ],
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
    return ansible_lint.AnsibleLint(config_instance)


def test_config_private_member(_instance):
    assert isinstance(_instance._config, config.Config)


def test_default_options_property(_instance):
    x = {
        'default_exclude': [_instance._config.scenario.ephemeral_directory],
        'exclude': [],
        'x': [],
    }

    assert x == _instance.default_options


def test_name_property(_instance):
    assert 'ansible-lint' == _instance.name


def test_enabled_property(_instance):
    assert _instance.enabled


@pytest.mark.parametrize(
    'config_instance', ['_provisioner_lint_section_data'], indirect=True)
def test_options_property(_instance):
    x = {
        'default_exclude': [_instance._config.scenario.ephemeral_directory],
        'exclude': [
            'foo',
            'bar',
        ],
        'x': [
            'foo',
            'bar',
        ],
        'foo': 'bar',
        'v': True,
    }

    assert x == _instance.options


@pytest.mark.parametrize(
    'config_instance', ['_provisioner_lint_section_data'], indirect=True)
def test_options_property_handles_cli_args(_instance):
    _instance._config.args = {'debug': True}
    x = {
        'default_exclude': [_instance._config.scenario.ephemeral_directory],
        'exclude': [
            'foo',
            'bar',
        ],
        'x': [
            'foo',
            'bar',
        ],
        'foo': 'bar',
        'v': True,
    }

    assert x == _instance.options


def test_default_env_property(_instance):
    assert 'MOLECULE_FILE' in _instance.default_env
    assert 'MOLECULE_INVENTORY_FILE' in _instance.default_env
    assert 'MOLECULE_SCENARIO_DIRECTORY' in _instance.default_env
    assert 'MOLECULE_INSTANCE_CONFIG' in _instance.default_env


@pytest.mark.parametrize(
    'config_instance', ['_provisioner_lint_section_data'], indirect=True)
def test_env_property(_instance):
    assert 'bar' == _instance.env['FOO']
    assert 'ANSIBLE_CONFIG' in _instance.env
    assert 'ANSIBLE_ROLES_PATH' in _instance.env
    assert 'ANSIBLE_LIBRARY' in _instance.env
    assert 'ANSIBLE_FILTER_PLUGINS' in _instance.env


@pytest.mark.parametrize(
    'config_instance', ['_provisioner_lint_section_data'], indirect=True)
def test_bake(_instance):
    _instance.bake()
    x = [
        str(sh.ansible_lint),
        '--foo=bar',
        '-v',
        '-x',
        '-x',
        '--exclude={}'.format(_instance._config.scenario.ephemeral_directory),
        '--exclude=foo',
        '--exclude=bar',
        _instance._config.provisioner.playbooks.converge,
        'bar',
        'foo',
    ]
    result = str(_instance._ansible_lint_command).split()

    assert sorted(x) == sorted(result)


def test_execute(mocker, patched_run_command, patched_logger_info,
                 patched_logger_success, _instance):
    _instance._ansible_lint_command = 'patched-ansiblelint-command'
    _instance.execute()

    patched_run_command.assert_called_once_with(
        'patched-ansiblelint-command', debug=False)

    msg = 'Executing Ansible Lint on {}...'.format(
        _instance._config.provisioner.playbooks.converge)
    patched_logger_info.assert_called_once_with(msg)

    msg = 'Lint completed successfully.'
    patched_logger_success.assert_called_once_with(msg)


def test_execute_does_not_execute(patched_run_command, patched_logger_warn,
                                  _instance):
    c = _instance._config.config
    c['provisioner']['lint']['enabled'] = False
    _instance.execute()

    assert not patched_run_command.called

    msg = 'Skipping, lint is disabled.'
    patched_logger_warn.assert_called_once_with(msg)


def test_execute_bakes(patched_run_command, _instance):
    _instance.execute()

    assert _instance._ansible_lint_command is not None

    assert 1 == patched_run_command.call_count


def test_executes_catches_and_exits_return_code(patched_run_command,
                                                patched_yamllint, _instance):
    patched_run_command.side_effect = sh.ErrorReturnCode_1(
        sh.ansible_lint, b'', b'')
    with pytest.raises(SystemExit) as e:
        _instance.execute()

    assert 1 == e.value.code

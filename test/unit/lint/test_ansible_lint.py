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
from molecule.lint import ansible_lint


@pytest.fixture
def molecule_lint_section_data():
    return {
        'lint': {
            'name': 'ansible-lint',
            'options': {
                'foo': 'bar',
                'v': True,
            },
            'env': {
                'foo': 'bar',
            }
        }
    }


@pytest.fixture
def ansible_lint_instance(molecule_lint_section_data, config_instance):
    config_instance.config.update(molecule_lint_section_data)

    return ansible_lint.AnsibleLint(config_instance)


def test_config_private_member(ansible_lint_instance):
    assert isinstance(ansible_lint_instance._config, config.Config)


def test_default_options_property(ansible_lint_instance):
    x = {'excludes': [ansible_lint_instance._config.ephemeral_directory]}

    assert x == ansible_lint_instance.default_options


def test_name_property(ansible_lint_instance):
    assert 'ansible-lint' == ansible_lint_instance.name


def test_enabled_property(ansible_lint_instance):
    assert ansible_lint_instance.enabled


def test_options_property(ansible_lint_instance):
    x = {
        'excludes': [ansible_lint_instance._config.ephemeral_directory],
        'foo': 'bar',
        'v': True,
    }

    assert x == ansible_lint_instance.options


def test_options_property_handles_cli_args(ansible_lint_instance):
    ansible_lint_instance._config.args = {'debug': True}
    x = {
        'excludes': [ansible_lint_instance._config.ephemeral_directory],
        'foo': 'bar',
        'v': True,
    }

    assert x == ansible_lint_instance.options


def test_default_env_property(ansible_lint_instance):
    assert isinstance(ansible_lint_instance.default_env, dict)


def test_env_property(ansible_lint_instance):
    assert 'bar' == ansible_lint_instance.env['foo']


def test_bake(ansible_lint_instance):
    ansible_lint_instance.bake()
    x = [
        str(sh.ansible_lint), '--foo=bar', '-v', '--exclude={}'.format(
            ansible_lint_instance._config.ephemeral_directory),
        ansible_lint_instance._config.scenario.converge
    ]
    result = str(ansible_lint_instance._ansible_lint_command).split()

    assert sorted(x) == sorted(result)


def test_execute(patched_run_command, patched_logger_success,
                 ansible_lint_instance):
    ansible_lint_instance._ansible_lint_command = 'patched-command'
    ansible_lint_instance.execute()

    patched_run_command.assert_called_once_with('patched-command', debug=None)

    msg = 'Lint completed successfully.'
    patched_logger_success.assert_called_once_with(msg)


def test_execute_does_not_execute(patched_run_command, patched_logger_warn,
                                  ansible_lint_instance):
    ansible_lint_instance._config.config['lint']['enabled'] = False
    ansible_lint_instance.execute()

    assert not patched_run_command.called

    msg = 'Skipping, lint is disabled.'
    patched_logger_warn.assert_called_once_with(msg)


def test_execute_bakes(patched_run_command, ansible_lint_instance):
    ansible_lint_instance.execute()

    assert ansible_lint_instance._ansible_lint_command is not None

    assert 1 == patched_run_command.call_count


def test_executes_catches_and_exits_return_code(patched_run_command,
                                                ansible_lint_instance):
    patched_run_command.side_effect = sh.ErrorReturnCode_1(sh.ansible_lint,
                                                           b'', b'')
    with pytest.raises(SystemExit) as e:
        ansible_lint_instance.execute()

    assert 1 == e.value.code

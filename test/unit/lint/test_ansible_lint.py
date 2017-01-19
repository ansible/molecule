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
def lint_data():
    return {'lint': {'name': 'ansible-lint', 'options': {'foo': 'bar'}}}


@pytest.fixture
def ansible_lint_instance(molecule_file, lint_data):
    c = config.Config(molecule_file, configs=[lint_data])

    return ansible_lint.AnsibleLint(c)


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
        'foo': 'bar'
    }

    assert x == ansible_lint_instance.options


def test_options_property_handles_cli_args(molecule_file,
                                           ansible_lint_instance, lint_data):
    c = config.Config(molecule_file, args={'debug': True}, configs=[lint_data])
    l = ansible_lint.AnsibleLint(c)
    x = {
        'excludes': [ansible_lint_instance._config.ephemeral_directory],
        'foo': 'bar'
    }

    # Does nothing.  The `ansible-lint` command does not support
    # a `debug` flag.
    assert x == l.options


def test_bake(ansible_lint_instance):
    ansible_lint_instance.bake()
    x = '{} --foo=bar --exclude={} {}'.format(
        str(sh.ansible_lint),
        ansible_lint_instance._config.ephemeral_directory,
        ansible_lint_instance._config.scenario.converge)

    assert x == ansible_lint_instance._ansible_lint_command


def test_execute(patched_run_command, ansible_lint_instance):
    ansible_lint_instance._ansible_lint_command = 'patched-command'
    ansible_lint_instance.execute()

    patched_run_command.assert_called_once_with('patched-command', debug=None)


def test_execute_does_not_execute(patched_run_command, ansible_lint_instance):
    ansible_lint_instance._config.config['lint']['enabled'] = False
    ansible_lint_instance.execute()

    assert not patched_run_command.called


def test_execute_bakes(patched_run_command, ansible_lint_instance):
    ansible_lint_instance.execute()

    assert ansible_lint_instance._ansible_lint_command is not None

    cmd = '{} --foo=bar --exclude={} {}'.format(
        str(sh.ansible_lint),
        ansible_lint_instance._config.ephemeral_directory,
        ansible_lint_instance._config.scenario.converge)
    patched_run_command.assert_called_once_with(cmd, debug=None)


def test_executes_catches_and_exits_return_code(patched_run_command,
                                                ansible_lint_instance):
    patched_run_command.side_effect = sh.ErrorReturnCode_1(sh.ansible_lint,
                                                           b'', b'')
    with pytest.raises(SystemExit) as e:
        ansible_lint_instance.execute()

    assert 1 == e.value.code

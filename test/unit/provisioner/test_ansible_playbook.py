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
from molecule.provisioner import ansible_playbook


@pytest.fixture
def ansible_playbook_instance(config_instance):
    return ansible_playbook.AnsiblePlaybook('playbook', config_instance)


@pytest.fixture
def inventory_file(ansible_playbook_instance):
    return ansible_playbook_instance._config.provisioner.inventory_file


def test_ansible_command_private_member(ansible_playbook_instance):
    assert ansible_playbook_instance._ansible_command is None


def test_ansible_playbook_private_member(ansible_playbook_instance):
    assert 'playbook' == ansible_playbook_instance._playbook


def test_config_private_member(ansible_playbook_instance):
    assert isinstance(ansible_playbook_instance._config, config.Config)


def test_bake(inventory_file, ansible_playbook_instance):
    pb = ansible_playbook_instance._config.provisioner.playbooks.converge
    ansible_playbook_instance._playbook = pb
    ansible_playbook_instance.bake()

    x = [
        str(sh.ansible_playbook),
        '--become',
        '--inventory={}'.format(inventory_file),
        pb,
    ]
    result = str(ansible_playbook_instance._ansible_command).split()

    assert sorted(x) == sorted(result)


def test_bake_removes_non_interactive_options_from_non_converge_playbooks(
        inventory_file, ansible_playbook_instance):
    ansible_playbook_instance.bake()

    x = '{} --inventory={} playbook'.format(
        str(sh.ansible_playbook), inventory_file)

    assert x == ansible_playbook_instance._ansible_command


def test_bake_has_ansible_args(inventory_file, ansible_playbook_instance):
    ansible_playbook_instance._config.ansible_args = ('foo', 'bar')
    ansible_playbook_instance.bake()

    x = '{} --inventory={} playbook foo bar'.format(
        str(sh.ansible_playbook), inventory_file)

    assert x == ansible_playbook_instance._ansible_command


def test_bake_does_not_have_ansible_args(inventory_file,
                                         ansible_playbook_instance):
    for action in ['create', 'destroy']:
        ansible_playbook_instance._config.ansible_args = ('foo', 'bar')
        ansible_playbook_instance._config.action = action
        ansible_playbook_instance.bake()

        x = '{} --inventory={} playbook'.format(
            str(sh.ansible_playbook), inventory_file)

        assert x == ansible_playbook_instance._ansible_command


def test_execute(patched_run_command, ansible_playbook_instance):
    ansible_playbook_instance._ansible_command = 'patched-command'
    result = ansible_playbook_instance.execute()

    patched_run_command.assert_called_once_with('patched-command', debug=False)
    assert 'patched-run-command-stdout' == result


def test_execute_bakes(inventory_file, patched_run_command,
                       ansible_playbook_instance):
    ansible_playbook_instance.execute()

    assert ansible_playbook_instance._ansible_command is not None

    cmd = '{} --inventory={} playbook'.format(
        str(sh.ansible_playbook), inventory_file)
    patched_run_command.assert_called_once_with(cmd, debug=False)


def test_execute_bakes_with_ansible_args(inventory_file, patched_run_command,
                                         ansible_playbook_instance):
    ansible_playbook_instance._config.ansible_args = ('--foo', '--bar')
    ansible_playbook_instance.execute()

    assert ansible_playbook_instance._ansible_command is not None

    cmd = '{} --inventory={} playbook --foo --bar'.format(
        str(sh.ansible_playbook), inventory_file)
    patched_run_command.assert_called_once_with(cmd, debug=False)


def test_executes_catches_and_exits_return_code_with_stdout(
        patched_run_command, patched_logger_critical,
        ansible_playbook_instance):
    patched_run_command.side_effect = sh.ErrorReturnCode_1(
        sh.ansible_playbook, b'out', b'err')
    with pytest.raises(SystemExit) as e:
        ansible_playbook_instance.execute()

    assert 1 == e.value.code

    msg = 'out'
    patched_logger_critical.assert_called_once_with(msg)


def test_add_cli_arg(ansible_playbook_instance):
    assert {} == ansible_playbook_instance._cli

    ansible_playbook_instance.add_cli_arg('foo', 'bar')
    assert {'foo': 'bar'} == ansible_playbook_instance._cli


def test_add_env_arg(ansible_playbook_instance):
    assert 'foo' not in ansible_playbook_instance._env

    ansible_playbook_instance.add_env_arg('foo', 'bar')
    assert 'bar' == ansible_playbook_instance._env['foo']

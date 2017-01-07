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

from molecule import ansible_playbook
from molecule import config


@pytest.fixture
def ansible_playbook_data():
    return {}


@pytest.fixture
def ansible_playbook_instance(molecule_file, platforms_data,
                              ansible_playbook_data):
    configs = [ansible_playbook_data, platforms_data]
    c = config.Config(molecule_file, configs=configs)

    return ansible_playbook.AnsiblePlaybook('inventory', 'playbook', c)


def test_ansible_playbook_command_private_member(ansible_playbook_instance):
    assert ansible_playbook_instance._ansible_playbook_command is None


def test_ansible_playbook_private_member(ansible_playbook_instance):
    assert 'playbook' == ansible_playbook_instance._playbook


def test_playbook_private_member(ansible_playbook_instance):
    assert 'inventory' == ansible_playbook_instance._inventory


def test_config_private_member(ansible_playbook_instance):
    assert isinstance(ansible_playbook_instance._config, config.Config)


def test_bake(ansible_playbook_instance):
    ansible_playbook_instance.bake()
    x = '{} --inventory=inventory playbook'.format(str(sh.ansible_playbook))

    assert x == ansible_playbook_instance._ansible_playbook_command


def test_execute(patched_run_command, ansible_playbook_instance):
    ansible_playbook_instance._ansible_playbook_command = 'patched-command'
    result = ansible_playbook_instance.execute()

    patched_run_command.assert_called_once_with('patched-command', debug=None)
    assert 'patched-run-command-stdout' == result


def test_execute_bakes(patched_run_command, ansible_playbook_instance):
    ansible_playbook_instance.execute()

    assert ansible_playbook_instance._ansible_playbook_command is not None

    cmd = '{} --inventory=inventory playbook'.format(str(sh.ansible_playbook))
    patched_run_command.assert_called_once_with(cmd, debug=None)


def test_executes_catches_and_exits_return_code(patched_run_command,
                                                ansible_playbook_instance):
    patched_run_command.side_effect = sh.ErrorReturnCode_1(sh.ansible_playbook,
                                                           None, None)
    with pytest.raises(SystemExit) as e:
        ansible_playbook_instance.execute()

    assert 1 == e.value.code


def test_add_cli_arg(ansible_playbook_instance):
    assert {} == ansible_playbook_instance._cli

    ansible_playbook_instance.add_cli_arg('foo', 'bar')
    assert {'foo': 'bar'} == ansible_playbook_instance._cli


def test_add_env_arg(ansible_playbook_instance):
    assert 'foo' not in ansible_playbook_instance._env

    ansible_playbook_instance.add_env_arg('foo', 'bar')
    assert 'bar' == ansible_playbook_instance._env['foo']

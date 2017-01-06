#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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

from molecule import config
from molecule.command import idempotence


@pytest.fixture
def idempotence_instance(molecule_file, platforms_data):
    configs = [platforms_data]
    c = config.Config(molecule_file, configs=configs)

    return idempotence.Idempotence(c)


def test_execute(mocker, patched_print_info, patched_ansible_converge,
                 patched_command_idempotence_is_idempotent,
                 patched_print_success, idempotence_instance):
    idempotence_instance.execute()
    x = [
        mocker.call('Scenario: [default]'),
        mocker.call('Provisioner: [ansible]'),
        mocker.call('Idempotence Verification of Playbook: [playbook.yml]')
    ]
    assert x == patched_print_info.mock_calls

    patched_ansible_converge.assert_called_once_with(
        idempotence_instance._config.provisioner.inventory_file,
        idempotence_instance._config.scenario.converge,
        out=None,
        err=None)

    patched_command_idempotence_is_idempotent.assert_called_once_with(
        'patched-ansible-converge-stdout')

    msg = 'Idempotence test passed.'
    patched_print_success.assert_called_once_with(msg)


def test_execute_fails_idempotence(
        mocker, patched_print_error, patched_ansible_converge,
        patched_command_idempotence_is_idempotent, idempotence_instance):
    patched_command_idempotence_is_idempotent.return_value = False
    with pytest.raises(SystemExit) as e:
        idempotence_instance.execute()

    assert 1 == e.value.code

    x = [
        mocker.call('Idempotence test failed because of the following tasks:'),
        mocker.call('')
    ]

    assert x == patched_print_error.mock_calls


def test_is_idempotent(idempotence_instance):
    output = """
PLAY RECAP ***********************************************************
check-command-01: ok=3    changed=0    unreachable=0    failed=0
    """

    assert idempotence_instance._is_idempotent(output)


def test_is_idempotent_not_idempotent(idempotence_instance):
    output = """
PLAY RECAP ***********************************************************
check-command-01: ok=2    changed=1    unreachable=0    failed=0
check-command-02: ok=2    changed=1    unreachable=0    failed=0
    """

    assert not idempotence_instance._is_idempotent(output)


def test_non_idempotent_tasks_idempotent(idempotence_instance):
    output = """
PLAY [all] ***********************************************************

GATHERING FACTS ******************************************************
ok: [check-command-01]

TASK: [Idempotence test] *********************************************
ok: [check-command-01]

PLAY RECAP ***********************************************************
check-command-01: ok=3    changed=0    unreachable=0    failed=0
"""
    result = idempotence_instance._non_idempotent_tasks(output)

    assert result == []


def test_non_idempotent_tasks_not_idempotent(idempotence_instance):
    output = """
PLAY [all] ***********************************************************

GATHERING FACTS ******************************************************
ok: [check-command-01]
ok: [check-command-02]

TASK: [Idempotence test] *********************************************
changed: [check-command-01]
changed: [check-command-02]

PLAY RECAP ***********************************************************
check-command-01: ok=2    changed=1    unreachable=0    failed=0
check-command-02: ok=2    changed=1    unreachable=0    failed=0
"""
    result = idempotence_instance._non_idempotent_tasks(output)

    assert result == [
        '* [check-command-01] => Idempotence test',
        '* [check-command-02] => Idempotence test'
    ]

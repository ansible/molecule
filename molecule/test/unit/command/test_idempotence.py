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

from molecule.command import idempotence


@pytest.fixture
def _patched_is_idempotent(mocker):
    return mocker.patch("molecule.command.idempotence.Idempotence._is_idempotent")


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.fixture
def _instance(patched_config_validate, config_instance):
    config_instance.state.change_state("converged", True)

    return idempotence.Idempotence(config_instance)


def test_execute(
    mocker,
    patched_logger_info,
    patched_ansible_converge,
    _patched_is_idempotent,
    patched_logger_success,
    _instance,
):
    _instance.execute()

    x = [mocker.call("Scenario: 'default'"), mocker.call("Action: 'idempotence'")]
    assert x == patched_logger_info.mock_calls

    patched_ansible_converge.assert_called_once_with(out=None, err=None)

    _patched_is_idempotent.assert_called_once_with("patched-ansible-converge-stdout")

    msg = "Idempotence completed successfully."
    patched_logger_success.assert_called_once_with(msg)


def test_execute_raises_when_not_converged(
    patched_logger_critical, patched_ansible_converge, _instance
):
    _instance._config.state.change_state("converged", False)
    with pytest.raises(SystemExit) as e:
        _instance.execute()

    assert 1 == e.value.code

    msg = "Instances not converged.  Please converge instances first."
    patched_logger_critical.assert_called_once_with(msg)


def test_execute_raises_when_fails_idempotence(
    mocker,
    patched_logger_critical,
    patched_ansible_converge,
    _patched_is_idempotent,
    _instance,
):
    _patched_is_idempotent.return_value = False
    with pytest.raises(SystemExit) as e:
        _instance.execute()

    assert 1 == e.value.code

    msg = "Idempotence test failed because of the following tasks:\n"
    patched_logger_critical.assert_called_once_with(msg)


def test_is_idempotent(_instance):
    output = """
PLAY RECAP ***********************************************************
check-command-01: ok=3    changed=0    unreachable=0    failed=0
    """

    assert _instance._is_idempotent(output)


def test_is_idempotent_not_idempotent(_instance):
    output = """
PLAY RECAP ***********************************************************
check-command-01: ok=2    changed=1    unreachable=0    failed=0
check-command-02: ok=2    changed=1    unreachable=0    failed=0
    """

    assert not _instance._is_idempotent(output)


def test_non_idempotent_tasks_idempotent(_instance):
    output = """
PLAY [all] ***********************************************************

GATHERING FACTS ******************************************************
ok: [check-command-01]

TASK: [Idempotence test] *********************************************
ok: [check-command-01]

PLAY RECAP ***********************************************************
check-command-01: ok=3    changed=0    unreachable=0    failed=0
"""
    result = _instance._non_idempotent_tasks(output)

    assert result == []


def test_non_idempotent_tasks_not_idempotent(_instance):
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
    result = _instance._non_idempotent_tasks(output)

    assert result == [
        "* [check-command-01] => Idempotence test",
        "* [check-command-02] => Idempotence test",
    ]

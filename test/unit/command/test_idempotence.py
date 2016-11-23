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

from molecule.command import idempotence


def test_execute_with_successful_idempotence(
        patched_converge, patched_print_info, molecule_instance):
    i = idempotence.Idempotence({}, {}, molecule_instance)
    result = i.execute()

    msg = 'Idempotence test in progress (can take a few minutes) ...'
    patched_print_info.assert_called_once_with(msg)

    patched_converge.assert_called_with(
        idempotent=True, exit=False, hide_errors=True)
    assert (None, None) == result


def test_execute_does_not_raise_on_converge_error(
        patched_converge, patched_print_info, molecule_instance):
    patched_converge.return_value = (1, None)

    i = idempotence.Idempotence({}, {}, molecule_instance)
    result = i.execute()

    msg = 'Skipping due to errors during converge.'
    patched_print_info.assert_called_with(msg)
    assert (1, None) == result


def test_execute_does_not_raise_on_idempotence_failure(
        mocker, patched_converge, patched_logger_error, molecule_instance):
    output = 'check-command-01: ok=2    changed=1    unreachable=0    failed=0'
    patched_converge.return_value = None, output

    i = idempotence.Idempotence({}, {}, molecule_instance)
    result = i.execute(exit=False)

    expected_calls = [
        mocker.call('Idempotence test failed because of the following tasks:'),
        mocker.call('')
    ]
    assert patched_logger_error.mock_calls == expected_calls
    assert (1, None) == result


def test_execute_raises_on_idempotence_failure(
        mocker, patched_converge, patched_logger_error, molecule_instance):
    output = 'check-command-01: ok=2    changed=1    unreachable=0    failed=0'
    patched_converge.return_value = None, output

    i = idempotence.Idempotence({}, {}, molecule_instance)
    with pytest.raises(SystemExit):
        i.execute()

    expected_calls = [
        mocker.call('Idempotence test failed because of the following tasks:'),
        mocker.call('')
    ]
    assert patched_logger_error.mock_calls == expected_calls


def test_non_idempotent_tasks_idempotent(molecule_instance):
    output = """
PLAY [all] ***********************************************************
GATHERING FACTS ******************************************************
ok: [check-command-01]
TASK: [Idempotence test] *********************************************
ok: [check-command-01]
PLAY RECAP ***********************************************************
check-command-01: ok=3    changed=0    unreachable=0    failed=0
"""
    i = idempotence.Idempotence({}, {}, molecule_instance)
    ret = i._non_idempotent_tasks(output)

    assert ret == []


def test_non_idempotent_tasks_not_idempotent(molecule_instance):
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
    i = idempotence.Idempotence({}, {}, molecule_instance)
    ret = i._non_idempotent_tasks(output)

    assert ret == [
        '* [check-command-01] => Idempotence test',
        '* [check-command-02] => Idempotence test'
    ]

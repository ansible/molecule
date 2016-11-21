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

from molecule.command import test


def test_execute(mocker, patched_destroy_main, patched_destroy,
                 patched_dependency, patched_syntax, patched_create,
                 patched_converge, patched_idempotence, patched_check,
                 patched_verify, molecule_instance):
    t = test.Test({}, {}, molecule_instance)
    result = t.execute()

    patched_syntax.assert_called_once_with(exit=False)
    patched_dependency.assert_called_once_with(exit=False)
    patched_create.assert_called_once_with(exit=False)
    patched_converge.assert_called_once_with(exit=False)
    patched_idempotence.assert_called_once_with(exit=False)
    patched_check.assert_called_once_with(exit=False)
    patched_verify.assert_called_once_with(exit=False)

    expected = [mocker.call(exit=False), mocker.call()]
    assert patched_destroy.mock_calls == expected

    assert (None, None) == result


def test_execute_fail_fast(patched_destroy, patched_logger_error,
                           molecule_instance):
    patched_destroy.return_value = 1, 'output'

    t = test.Test({}, {}, molecule_instance)
    with pytest.raises(SystemExit):
        t.execute()

    patched_logger_error.assert_called_once_with('output')


def test_execute_always_destroy(
        mocker, patched_destroy_main, patched_destroy, patched_syntax,
        patched_create, patched_converge, patched_idempotence, patched_check,
        patched_verify, molecule_instance):
    command_args = {'destroy': 'always'}
    t = test.Test({}, command_args, molecule_instance)
    result = t.execute()

    expected = [mocker.call(exit=False), mocker.call()]
    assert patched_destroy.mock_calls == expected

    assert (None, None) == result


def test_execute_never_destroy(
        patched_destroy_main, patched_destroy, patched_syntax, patched_create,
        patched_converge, patched_idempotence, patched_check, patched_verify,
        molecule_instance):
    command_args = {'destroy': 'never'}
    t = test.Test({}, command_args, molecule_instance)
    result = t.execute()

    patched_destroy.assert_called_once_with(exit=False)

    assert (None, None) == result

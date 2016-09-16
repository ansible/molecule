#  Copyright (c) 2015-2016 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

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
        patched_converge, patched_logger_error, molecule_instance):
    patched_converge.return_value = None, 'changed=2'

    i = idempotence.Idempotence({}, {}, molecule_instance)
    result = i.execute(exit=False)

    msg = 'Idempotence test failed.'
    patched_logger_error.assert_called_with(msg)
    assert (1, None) == result


def test_execute_raises_on_idempotence_failure(
        patched_converge, patched_logger_error, molecule_instance):
    patched_converge.return_value = None, 'changed=2'

    i = idempotence.Idempotence({}, {}, molecule_instance)
    with pytest.raises(SystemExit):
        i.execute()

    msg = 'Idempotence test failed.'
    patched_logger_error.assert_called_with(msg)

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

from molecule.command import check


def test_raises_when_instance_not_created(patched_main, patched_logger_error,
                                          molecule_instance):
    c = check.Check([], dict(), molecule_instance)

    with pytest.raises(SystemExit):
        c.execute()

    msg = ('ERROR: Instance(s) not created, `check` should be run against '
           'created instance(s)')
    patched_logger_error.assert_called_once_with(msg)


def test_execute(mocker, patched_main, patched_ansible_playbook,
                 patched_print_info, molecule_instance):
    molecule_instance.state.change_state('created', True)
    molecule_instance.state.change_state('converged', True)
    molecule_instance._driver = mocker.Mock(
        ansible_connection_params={'debug': True})
    patched_ansible_playbook.return_value = 'returned'

    c = check.Check([], dict(), molecule_instance)
    result = c.execute()

    msg = 'Performing a "Dry Run" of playbook ...'
    patched_print_info.assert_called_once_with(msg)
    patched_ansible_playbook.assert_called_once_with(hide_errors=True)
    assert 'returned' == result

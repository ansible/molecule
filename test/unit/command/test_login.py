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

from molecule.command import login


def test_execute_raises_when_no_running_hosts(patched_print_error,
                                              molecule_instance):
    l = login.Login({}, {}, molecule_instance)
    with pytest.raises(SystemExit):
        l.execute()

    msg = 'There are no running hosts.'
    patched_print_error.assert_called_once_with(msg)


def test_execute_raises_when_no_host_privided_but_multiple_instances_exist(
        patched_print_error, molecule_instance):
    molecule_instance.state.change_state('hosts', {'foo': None, 'baz': None})
    l = login.Login({}, {}, molecule_instance)
    with pytest.raises(SystemExit):
        l.execute()

    msg = ('There are 2 running hosts. Please specify which with --host.\n'
           '\nAvailable hosts:\nbaz\nfoo')
    patched_print_error.assert_called_once_with(msg)


def test_execute_raises_when_host_unknown(patched_print_error,
                                          molecule_instance):
    molecule_instance.state.change_state('hosts', {'foo': None})
    command_args = {'host': 'unknown'}
    l = login.Login({}, command_args, molecule_instance)
    with pytest.raises(SystemExit):
        l.execute()

    msg = "Unknown host 'unknown'.\n\nAvailable hosts:\nfoo"
    patched_print_error.assert_called_once_with(msg)


def test_execute_single_instance(mocker, molecule_instance):
    molecule_instance.state.change_state('hosts', {'foo': None})
    patched_get_login = mocker.patch('molecule.command.login.Login._get_login')

    l = login.Login({}, {}, molecule_instance)
    l.execute()

    patched_get_login.assert_called_once_with('foo')


def test_execute_multiple_instances(mocker, molecule_instance):
    molecule_instance.state.change_state('hosts', {'foo': None, 'bar': None})
    command_args = {'host': 'foo'}
    patched_get_login = mocker.patch('molecule.command.login.Login._get_login')

    l = login.Login({}, command_args, molecule_instance)
    l.execute()

    patched_get_login.assert_called_once_with('foo')


def test_execute_partial_hostname_match(mocker, molecule_instance):
    molecule_instance.state.change_state('hosts', {'foo-host': None})
    command_args = {'host': 'fo'}
    patched_get_login = mocker.patch('molecule.command.login.Login._get_login')

    l = login.Login({}, command_args, molecule_instance)
    l.execute()

    patched_get_login.assert_called_once_with('foo-host')


def test_execute_more_specific_hostname_match(mocker, molecule_instance):
    molecule_instance.state.change_state('hosts', {'foo': None, 'fooo': None})
    command_args = {'host': 'foo'}
    patched_get_login = mocker.patch('molecule.command.login.Login._get_login')

    l = login.Login({}, command_args, molecule_instance)
    l.execute()

    patched_get_login.assert_called_once_with('foo')


def test_execute_partial_hostname_raises_when_many_match(
        mocker, patched_print_error, molecule_instance):
    molecule_instance.state.change_state('hosts', {'foo': None, 'fooo': None})
    command_args = {'host': 'fo'}

    l = login.Login({}, command_args, molecule_instance)
    with pytest.raises(SystemExit):
        l.execute()

    msg = ("There are 2 hosts that match 'fo'. You can only login to one at a "
           "time.\n\nAvailable hosts:\nfoo\nfooo")
    patched_print_error.assert_called_once_with(msg)

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

from molecule import config
from molecule.command import login


@pytest.fixture
def login_instance(molecule_file, platforms_data):
    configs = [platforms_data]
    c = config.Config(
        molecule_file,
        args={},
        command_args={'host': 'instance-1'},
        configs=configs)
    c.state.change_state('created', True)

    return login.Login(c)


def test_execute(mocker, login_instance):
    m = mocker.patch('molecule.command.login.Login._get_login')
    login_instance.execute()

    m.assert_called_once_with('instance-1-default')


def test_execute_raises_when_not_converged(patched_print_error,
                                           login_instance):
    login_instance._config.state.change_state('created', False)
    with pytest.raises(SystemExit) as e:
        login_instance.execute()

    assert 1 == e.value.code

    msg = 'Instances not created.  Please create instances first.'
    patched_print_error.assert_called_once_with(msg)


def test_get_hostname_does_not_match(molecule_file, patched_print_error):
    c = config.Config(molecule_file, command_args={'host': 'invalid'})
    l = login.Login(c)
    hosts = ['instance-1']

    with pytest.raises(SystemExit) as e:
        l._get_hostname(hosts)

    assert 1 == e.value.code

    msg = ("There are no hosts that match 'invalid'.  You "
           'can only login to valid hosts.')
    patched_print_error.assert_called_once_with(msg)


def test_get_hostname_exact_match_with_one_host(molecule_file):
    c = config.Config(molecule_file, command_args={'host': 'instance-1'})
    l = login.Login(c)
    hosts = ['instance-1']

    assert 'instance-1' == l._get_hostname(hosts)


def test_get_hostname_partial_match_with_one_host(molecule_file):
    c = config.Config(molecule_file, command_args={'host': 'inst'})
    l = login.Login(c)
    hosts = ['instance-1']

    assert 'instance-1' == l._get_hostname(hosts)


def test_get_hostname_exact_match_with_multiple_hosts(molecule_file):
    c = config.Config(molecule_file, command_args={'host': 'instance-1'})
    l = login.Login(c)
    hosts = ['instance-1', 'instance-2']

    assert 'instance-1' == l._get_hostname(hosts)


def test_get_hostname_partial_match_with_multiple_hosts(molecule_file):
    c = config.Config(molecule_file, command_args={'host': 'foo'})
    l = login.Login(c)
    hosts = ['foo', 'fooo']

    assert 'foo' == l._get_hostname(hosts)


def test_get_hostname_partial_match_with_multiple_hosts_raises(
        molecule_file, patched_print_error):
    c = config.Config(molecule_file, command_args={'host': 'inst'})
    l = login.Login(c)
    hosts = ['instance-1', 'instance-2']

    with pytest.raises(SystemExit) as e:
        l._get_hostname(hosts)

    assert 1 == e.value.code

    msg = ("There are 2 hosts that match 'inst'. "
           'You can only login to one at a time.\n\n'
           'Available hosts:\n'
           'instance-1\n'
           'instance-2')
    patched_print_error.assert_called_once_with(msg)

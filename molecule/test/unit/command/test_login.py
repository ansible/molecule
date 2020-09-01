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

from molecule.command import login


@pytest.fixture
def _instance(config_instance):
    config_instance.state.change_state("created", True)

    return login.Login(config_instance)


def test_execute(mocker, _instance):
    _instance._config.command_args = {"host": "instance-1"}
    m = mocker.patch("molecule.command.login.Login._get_login")
    _instance.execute()

    m.assert_called_once_with("instance-1")


@pytest.mark.skip(reason="needs rewrite after switch to delegated")
@pytest.mark.parametrize(
    "config_instance", ["command_driver_delegated_managed_section_data"], indirect=True
)
def test_execute_raises_when_not_created(patched_logger_critical, _instance):
    _instance._config.state.change_state("created", False)

    with pytest.raises(SystemExit) as e:
        _instance.execute()

    assert 1 == e.value.code

    msg = "Instances not created.  Please create instances first."
    patched_logger_critical.assert_called_once_with(msg)


def test_get_hostname_does_not_match(patched_logger_critical, _instance):
    _instance._config.command_args = {"host": "invalid"}
    hosts = ["instance-1"]
    with pytest.raises(SystemExit) as e:
        _instance._get_hostname(hosts)

    assert 1 == e.value.code

    msg = (
        "There are no hosts that match 'invalid'.  You "
        "can only login to valid hosts."
    )
    patched_logger_critical.assert_called_once_with(msg)


def test_get_hostname_exact_match_with_one_host(_instance):
    _instance._config.command_args = {"host": "instance-1"}
    hosts = ["instance-1"]

    assert "instance-1" == _instance._get_hostname(hosts)


def test_get_hostname_partial_match_with_one_host(_instance):
    _instance._config.command_args = {"host": "inst"}
    hosts = ["instance-1"]

    assert "instance-1" == _instance._get_hostname(hosts)


def test_get_hostname_exact_match_with_multiple_hosts(_instance):
    _instance._config.command_args = {"host": "instance-1"}
    hosts = ["instance-1", "instance-2"]

    assert "instance-1" == _instance._get_hostname(hosts)


def test_get_hostname_partial_match_with_multiple_hosts(_instance):
    _instance._config.command_args = {"host": "foo"}
    hosts = ["foo", "fooo"]

    assert "foo" == _instance._get_hostname(hosts)


def test_get_hostname_partial_match_with_multiple_hosts_raises(
    patched_logger_critical, _instance
):
    _instance._config.command_args = {"host": "inst"}
    hosts = ["instance-1", "instance-2"]
    with pytest.raises(SystemExit) as e:
        _instance._get_hostname(hosts)

    assert 1 == e.value.code

    msg = (
        "There are 2 hosts that match 'inst'. "
        "You can only login to one at a time.\n\n"
        "Available hosts:\n"
        "instance-1\n"
        "instance-2"
    )
    patched_logger_critical.assert_called_once_with(msg)


def test_get_hostname_no_host_flag_specified_on_cli(_instance):
    _instance._config.command_args = {}
    hosts = ["instance-1"]
    _instance._get_hostname(hosts)

    assert "instance-1" == _instance._get_hostname(hosts)


def test_get_hostname_no_host_flag_specified_on_cli_with_multiple_hosts_raises(
    patched_logger_critical, _instance
):
    _instance._config.command_args = {}
    hosts = ["instance-1", "instance-2"]
    with pytest.raises(SystemExit) as e:
        _instance._get_hostname(hosts)

    assert 1 == e.value.code

    msg = (
        "There are 2 running hosts. Please specify "
        "which with --host.\n\n"
        "Available hosts:\n"
        "instance-1\n"
        "instance-2"
    )
    patched_logger_critical.assert_called_once_with(msg)

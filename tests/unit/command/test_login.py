#  Copyright (c) 2015-2018 Cisco Systems, Inc.  # noqa: D100
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
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from molecule.command import login


if TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from molecule import config


@pytest.fixture()
def _instance(config_instance: config.Config):  # type: ignore[no-untyped-def]  # noqa: ANN202
    config_instance.state.change_state("created", True)  # noqa: FBT003

    return login.Login(config_instance)


def test_login_execute(mocker: MockerFixture, _instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    _instance._config.command_args = {"host": "instance-1"}
    m = mocker.patch("molecule.command.login.Login._get_login")
    _instance.execute()

    m.assert_called_once_with("instance-1")


@pytest.mark.parametrize(
    "config_instance",
    ["command_driver_delegated_managed_section_data"],  # noqa: PT007
    indirect=True,
)
def test_login_execute_instance_creation(mocker: MockerFixture, _instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    _instance._config.command_args = {"host": "instance-1"}
    _instance._config.state.change_state("created", False)  # noqa: FBT003

    mocker.patch("molecule.command.login.Login._get_login")
    patched_execute_subcommand = mocker.patch("molecule.command.base.execute_subcommand")
    patched_execute_subcommand.side_effect = lambda _config, _: _config.state.change_state(
        key="created",
        value=True,
    )
    _instance.execute()

    patched_execute_subcommand.assert_called_once_with(_instance._config, "create")
    assert _instance._config.state.created


def test_get_hostname_does_not_match(caplog, _instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    _instance._config.command_args = {"host": "invalid"}
    hosts = ["instance-1"]
    with pytest.raises(SystemExit) as e:
        _instance._get_hostname(hosts)

    assert e.value.code == 1

    msg = "There are no hosts that match 'invalid'.  You can only login to valid hosts."
    assert msg in caplog.text


def test_get_hostname_exact_match_with_one_host(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    _instance._config.command_args = {"host": "instance-1"}
    hosts = ["instance-1"]

    assert _instance._get_hostname(hosts) == "instance-1"


def test_get_hostname_partial_match_with_one_host(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    _instance._config.command_args = {"host": "inst"}
    hosts = ["instance-1"]

    assert _instance._get_hostname(hosts) == "instance-1"


def test_get_hostname_exact_match_with_multiple_hosts(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    _instance._config.command_args = {"host": "instance-1"}
    hosts = ["instance-1", "instance-2"]

    assert _instance._get_hostname(hosts) == "instance-1"


def test_get_hostname_partial_match_with_multiple_hosts(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    _instance._config.command_args = {"host": "foo"}
    hosts = ["foo", "fooo"]

    assert _instance._get_hostname(hosts) == "foo"


def test_get_hostname_partial_match_with_multiple_hosts_raises(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    caplog,  # noqa: ANN001
    _instance,  # noqa: ANN001, PT019
):
    _instance._config.command_args = {"host": "inst"}
    hosts = ["instance-1", "instance-2"]
    with pytest.raises(SystemExit) as e:
        _instance._get_hostname(hosts)

    assert e.value.code == 1

    msg = (
        "There are 2 hosts that match 'inst'. "
        "You can only login to one at a time.\n\n"
        "Available hosts:\n"
        "instance-1\n"
        "instance-2"
    )
    assert msg in caplog.text


def test_get_hostname_no_host_flag_specified_on_cli(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    _instance._config.command_args = {}
    hosts = ["instance-1"]
    _instance._get_hostname(hosts)

    assert _instance._get_hostname(hosts) == "instance-1"


def test_get_hostname_no_host_flag_specified_on_cli_with_multiple_hosts_raises(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    caplog,  # noqa: ANN001
    _instance,  # noqa: ANN001, PT019
):
    _instance._config.command_args = {}
    hosts = ["instance-1", "instance-2"]
    with pytest.raises(SystemExit) as e:
        _instance._get_hostname(hosts)

    assert e.value.code == 1

    msg = (
        "There are 2 running hosts. Please specify "
        "which with --host.\n\n"
        "Available hosts:\n"
        "instance-1\n"
        "instance-2"
    )
    assert msg in caplog.text

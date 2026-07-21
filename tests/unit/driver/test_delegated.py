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

import json
import os
import subprocess

from typing import TYPE_CHECKING

import pytest

from molecule import config
from molecule.driver import delegated
from tests.conftest import is_subset  # pylint:disable=C0411


if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture
def _driver_managed_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {
        "driver": {
            "name": "default",
            "options": {
                "managed": True,
            },
        },
    }


@pytest.fixture
def _driver_unmanaged_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {
        "driver": {
            "name": "default",
            "options": {
                "managed": False,
            },
        },
    }


@pytest.fixture
def _instance(config_instance: config.Config):  # type: ignore[no-untyped-def]  # noqa: ANN202
    return delegated.Delegated(config_instance)


def test_delegated_config_private_member(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert isinstance(_instance._config, config.Config)


def test_delegated_options_property2(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.testinfra_options == {
        "connection": "ansible",
        "ansible-inventory": _instance._config.provisioner.inventory_directory,
    }


def test_delegated_name_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.name == "default"


@pytest.mark.parametrize(
    "config_instance",
    ["_driver_unmanaged_section_data"],  # noqa: PT007
    indirect=True,
)
def test_delegated_options_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    x = {
        "managed": False,
    }

    assert x == _instance.options


@pytest.mark.parametrize(
    "config_instance",
    ["_driver_managed_section_data"],  # noqa: PT007
    indirect=True,
)
def test_delegated_options_property_when_managed(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    x = {"managed": True}

    assert x == _instance.options


@pytest.mark.parametrize(
    "config_instance",
    ["_driver_managed_section_data"],  # noqa: PT007
    indirect=True,
)
def test_login_cmd_template_property_when_managed(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    x = (
        "ssh {address} -l {user} -p {port} -i {identity_file} "
        "-o UserKnownHostsFile=/dev/null "
        "-o ControlMaster=auto "
        "-o ControlPersist=60s "
        "-o ForwardX11=no "
        "-o LogLevel=ERROR "
        "-o IdentitiesOnly=yes "
        "-o StrictHostKeyChecking=no"
    )

    assert x == _instance.login_cmd_template


def test_safe_files_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.safe_files == []


def test_default_safe_files_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.default_safe_files == []


def test_delegated_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.delegated


def test_managed_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.managed


@pytest.mark.parametrize(
    "config_instance",
    ["_driver_unmanaged_section_data"],  # noqa: PT007
    indirect=True,
)
def test_default_ssh_connection_options_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.default_ssh_connection_options == []


@pytest.mark.parametrize(
    "config_instance",
    ["_driver_managed_section_data"],  # noqa: PT007
    indirect=True,
)
def test_default_ssh_connection_options_property_when_managed(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    x = [
        "-o UserKnownHostsFile=/dev/null",
        "-o ControlMaster=auto",
        "-o ControlPersist=60s",
        "-o ForwardX11=no",
        "-o LogLevel=ERROR",
        "-o IdentitiesOnly=yes",
        "-o StrictHostKeyChecking=no",
    ]

    assert x == _instance.default_ssh_connection_options


@pytest.mark.parametrize(
    "config_instance",
    ["_driver_unmanaged_section_data"],  # noqa: PT007
    indirect=True,
)
def test_login_options(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.login_options("foo") == {"instance": "foo"}


@pytest.mark.parametrize(
    "config_instance",
    ["_driver_managed_section_data"],  # noqa: PT007
    indirect=True,
)
def test_login_options_when_managed(mocker: MockerFixture, _instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    m = mocker.patch("molecule.driver.delegated.Delegated._get_instance_config")
    m.return_value = {
        "instance": "foo",
        "address": "172.16.0.2",
        "user": "cloud-user",
        "port": 22,
        "become_method": "su",
        "become_pass": "password",
        "identity_file": "/foo/bar",
    }

    x = {
        "instance": "foo",
        "address": "172.16.0.2",
        "user": "cloud-user",
        "port": 22,
        "become_method": "su",
        "become_pass": "password",
        "identity_file": "/foo/bar",
    }
    assert x == _instance.login_options("foo")


@pytest.mark.parametrize(
    "config_instance",
    ["_driver_unmanaged_section_data"],  # noqa: PT007
    indirect=True,
)
def test_ansible_connection_options(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    x = {}  # type: ignore[var-annotated]

    assert is_subset(x, _instance.ansible_connection_options("foo"))  # type: ignore[no-untyped-call]


@pytest.mark.parametrize(
    "config_instance",
    ["_driver_managed_section_data"],  # noqa: PT007
    indirect=True,
)
def test_ansible_connection_options_when_managed(mocker: MockerFixture, _instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.managed is True

    ssh_case_data = mocker.patch(
        "molecule.driver.delegated.Delegated._get_instance_config",
    )
    ssh_case_data.return_value = {
        "instance": "foo",
        "address": "172.16.0.2",
        "user": "cloud-user",
        "port": 22,
        "become_method": "su",
        "become_pass": "password",
        "identity_file": "/foo/bar",
    }

    ssh_expected_data = {
        "ansible_host": "172.16.0.2",
        "ansible_port": 22,
        "ansible_user": "cloud-user",
        "ansible_become_method": "su",
        "ansible_become_pass": "password",
        "ansible_private_key_file": "/foo/bar",
        "ansible_connection": "smart",
        "ansible_ssh_common_args": (
            "-o UserKnownHostsFile=/dev/null "
            "-o ControlMaster=auto "
            "-o ControlPersist=60s "
            "-o ForwardX11=no "
            "-o LogLevel=ERROR "
            "-o IdentitiesOnly=yes "
            "-o StrictHostKeyChecking=no"
        ),
    }

    assert ssh_expected_data.items() <= _instance.ansible_connection_options("foo").items()

    winrm_case_data = mocker.patch(
        "molecule.driver.delegated.Delegated._get_instance_config",
    )
    winrm_case_data.return_value = {
        "instance": "foo",
        "address": "172.16.0.2",
        "user": "cloud-user",
        "port": 5896,
        "connection": "winrm",
    }

    winrm_expected_data = {
        "ansible_host": "172.16.0.2",
        "ansible_port": 5896,
        "ansible_user": "cloud-user",
        "ansible_connection": "winrm",
    }

    assert winrm_expected_data.items() <= _instance.ansible_connection_options("foo").items()


def test_ansible_connection_options_handles_missing_instance_config_managed(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    m = mocker.patch("molecule.util.safe_load_file")
    m.side_effect = IOError

    assert _instance.ansible_connection_options("foo") == {}


def test_ansible_connection_options_handles_missing_results_key_when_managed(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    m = mocker.patch("molecule.util.safe_load_file")
    m.side_effect = StopIteration

    assert _instance.ansible_connection_options("foo") == {}


def test_instance_config_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    x = os.path.join(  # noqa: PTH118
        _instance._config.scenario.ephemeral_directory,
        "instance_config.yml",
    )

    assert x == _instance.instance_config


@pytest.mark.parametrize(
    "config_instance",
    ["_driver_unmanaged_section_data"],  # noqa: PT007
    indirect=True,
)
def test_ssh_connection_options_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.ssh_connection_options == []


def test_status(mocker: MockerFixture, _instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    result = _instance.status()

    assert len(result) == 2  # noqa: PLR2004

    assert result[0].instance_name == "instance-1"
    assert result[0].driver_name == "default"
    assert result[0].provisioner_name == "ansible"
    assert result[0].scenario_name == "default"
    assert result[0].created == "false"
    assert result[0].converged == "false"

    assert result[1].instance_name == "instance-2"
    assert result[1].driver_name == "default"
    assert result[1].provisioner_name == "ansible"
    assert result[1].scenario_name == "default"
    assert result[1].created == "false"
    assert result[1].converged == "false"


def test_delegated_created(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance._created() == "false"


@pytest.fixture
def _driver_options_managed_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {"driver": {"options": {"managed": False}}}


@pytest.fixture
def _molecule_data_native():  # type: ignore[no-untyped-def]  # noqa: ANN202
    """Provide a molecule data dictionary for an ansible-native scenario (no `platforms`)."""
    return {
        "ansible": {"executor": {"backend": "ansible-playbook"}},
        "driver": {},
        "platforms": [],
        "provisioner": {},
    }


@pytest.mark.parametrize(
    "config_instance",
    ["_driver_options_managed_section_data"],  # noqa: PT007
    indirect=True,
)
def test_created_unknown_when_managed_false(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    _driver_options_managed_section_data,  # noqa: PT019
    _instance,  # noqa: PT019
):
    assert _instance._created() == "unknown"


def test_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance._converged() == "false"


def test_get_instance_config(mocker: MockerFixture, _instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    m = mocker.patch("molecule.util.safe_load_file")
    m.return_value = [{"instance": "foo"}, {"instance": "bar"}]

    x = {"instance": "foo"}
    assert x == _instance._get_instance_config("foo")


def test_ansible_inventory_args(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    args = _instance._ansible_inventory_args()

    assert args[0] == "--inventory"
    assert args[1] == _instance._config.provisioner.inventory_directory


def test_ansible_inventory_args_includes_extra_inventory_args(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    mocker.patch.object(
        type(_instance._config.provisioner),
        "ansible_args",
        new_callable=mocker.PropertyMock,
        return_value=["--inventory=/extra/inventory", "--diff"],
    )

    args = _instance._ansible_inventory_args()

    assert args == [
        "--inventory",
        _instance._config.provisioner.inventory_directory,
        "--inventory=/extra/inventory",
    ]


def test_ansible_inventory_args_includes_split_inventory_flag_and_value(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    mocker.patch.object(
        type(_instance._config.provisioner),
        "ansible_args",
        new_callable=mocker.PropertyMock,
        return_value=["--inventory", "/extra/inventory", "--diff"],
    )

    args = _instance._ansible_inventory_args()

    assert args == [
        "--inventory",
        _instance._config.provisioner.inventory_directory,
        "--inventory",
        "/extra/inventory",
    ]


def test_ansible_inventory_args_includes_split_short_flag_and_value(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    mocker.patch.object(
        type(_instance._config.provisioner),
        "ansible_args",
        new_callable=mocker.PropertyMock,
        return_value=["-i", "/extra/inventory"],
    )

    args = _instance._ansible_inventory_args()

    assert args == [
        "--inventory",
        _instance._config.provisioner.inventory_directory,
        "-i",
        "/extra/inventory",
    ]


def test_ansible_inventory_args_keeps_trailing_inventory_flag_with_no_value(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    mocker.patch.object(
        type(_instance._config.provisioner),
        "ansible_args",
        new_callable=mocker.PropertyMock,
        return_value=["--diff", "--inventory"],
    )

    args = _instance._ansible_inventory_args()

    assert args == [
        "--inventory",
        _instance._config.provisioner.inventory_directory,
        "--inventory",
    ]


def test_run_ansible_inventory_returns_parsed_json(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    m = mocker.patch("subprocess.run")
    m.return_value = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=json.dumps({"_meta": {"hostvars": {"instance-1": {}}}}),
    )

    result = _instance._run_ansible_inventory(["--list"])

    assert result == {"_meta": {"hostvars": {"instance-1": {}}}}


def test_run_ansible_inventory_returns_none_on_called_process_error(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    caplog: pytest.LogCaptureFixture,
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    m = mocker.patch("subprocess.run")
    m.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=["ansible-inventory"],
        stderr="boom",
    )

    with caplog.at_level("DEBUG"):
        result = _instance._run_ansible_inventory(["--list"])

    assert result is None
    assert "boom" in caplog.text


def test_run_ansible_inventory_returns_none_on_bad_json(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    caplog: pytest.LogCaptureFixture,
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    m = mocker.patch("subprocess.run")
    m.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout="not json")

    with caplog.at_level("DEBUG"):
        result = _instance._run_ansible_inventory(["--list"])

    assert result is None
    assert "ansible-inventory" in caplog.text


def test_run_ansible_inventory_returns_none_when_binary_missing(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    caplog: pytest.LogCaptureFixture,
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    m = mocker.patch("subprocess.run")
    m.side_effect = FileNotFoundError("ansible-inventory not found")

    with caplog.at_level("DEBUG"):
        result = _instance._run_ansible_inventory(["--list"])

    assert result is None
    assert "ansible-inventory" in caplog.text


def test_run_ansible_inventory_returns_none_on_timeout(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    caplog: pytest.LogCaptureFixture,
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    m = mocker.patch("subprocess.run")
    m.side_effect = subprocess.TimeoutExpired(cmd=["ansible-inventory"], timeout=30)

    with caplog.at_level("DEBUG"):
        result = _instance._run_ansible_inventory(["--list"])

    assert result is None
    assert "timed out" in caplog.text


def test_run_ansible_inventory_passes_timeout_to_subprocess_run(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    m = mocker.patch("subprocess.run")
    m.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout="{}")

    _instance._run_ansible_inventory(["--list"])

    assert m.call_args.kwargs["timeout"] == 30  # noqa: PLR2004


def test_get_inventory_login_options_maps_ansible_vars(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    m = mocker.patch("molecule.driver.delegated.Delegated._run_ansible_inventory")
    m.return_value = {
        "ansible_host": "172.16.0.2",
        "ansible_user": "cloud-user",
        "ansible_port": 22,
        "ansible_ssh_private_key_file": "/foo/bar",
    }

    x = {
        "address": "172.16.0.2",
        "user": "cloud-user",
        "port": 22,
        "identity_file": "/foo/bar",
    }
    assert x == _instance._get_inventory_login_options("foo")


def test_get_inventory_login_options_partial_vars(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    m = mocker.patch("molecule.driver.delegated.Delegated._run_ansible_inventory")
    m.return_value = {"ansible_host": "172.16.0.2"}

    assert _instance._get_inventory_login_options("foo") == {"address": "172.16.0.2"}


def test_get_inventory_login_options_returns_empty_dict_when_lookup_fails(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    m = mocker.patch("molecule.driver.delegated.Delegated._run_ansible_inventory")
    m.return_value = None

    assert _instance._get_inventory_login_options("foo") == {}


def test_get_ansible_native_hosts_returns_sorted_hostvars_keys(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    m = mocker.patch("molecule.driver.delegated.Delegated._run_ansible_inventory")
    m.return_value = {
        "_meta": {
            "hostvars": {
                "instance-2": {},
                "instance-1": {},
            },
        },
    }

    assert _instance.get_ansible_native_hosts() == ["instance-1", "instance-2"]


def test_get_ansible_native_hosts_returns_empty_list_when_lookup_fails(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    m = mocker.patch("molecule.driver.delegated.Delegated._run_ansible_inventory")
    m.return_value = None

    assert _instance.get_ansible_native_hosts() == []


@pytest.mark.parametrize(
    "config_instance",
    ["_driver_managed_section_data"],  # noqa: PT007
    indirect=True,
)
def test_login_options_falls_back_to_inventory_on_stop_iteration(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    mocker.patch(
        "molecule.driver.delegated.Delegated._get_instance_config",
        side_effect=StopIteration,
    )
    m = mocker.patch("molecule.driver.delegated.Delegated._get_inventory_login_options")
    m.return_value = {"address": "172.16.0.2", "user": "cloud-user"}

    x = {"instance": "foo", "address": "172.16.0.2", "user": "cloud-user"}
    assert x == _instance.login_options("foo")
    m.assert_called_once_with("foo")


@pytest.mark.parametrize(
    "config_instance",
    ["_driver_managed_section_data"],  # noqa: PT007
    indirect=True,
)
def test_login_options_falls_back_to_inventory_on_os_error(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    mocker.patch(
        "molecule.driver.delegated.Delegated._get_instance_config",
        side_effect=OSError,
    )
    m = mocker.patch("molecule.driver.delegated.Delegated._get_inventory_login_options")
    m.return_value = {}

    assert _instance.login_options("foo") == {"instance": "foo"}
    m.assert_called_once_with("foo")


@pytest.mark.parametrize(
    "config_instance",
    ["_molecule_data_native"],  # noqa: PT007
    indirect=True,
)
def test_status_falls_back_to_ansible_native_hosts_when_no_platforms(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    assert _instance._config.platforms.instances == []

    mocker.patch(
        "molecule.driver.delegated.Delegated.get_ansible_native_hosts",
        return_value=["instance-2", "instance-1"],
    )

    result = _instance.status()

    assert [s.instance_name for s in result] == ["instance-2", "instance-1"]


@pytest.mark.parametrize(
    "config_instance",
    ["_molecule_data_native"],  # noqa: PT007
    indirect=True,
)
def test_status_falls_back_to_blank_placeholder_when_inventory_empty(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,
    _instance,  # noqa: PT019
):
    mocker.patch(
        "molecule.driver.delegated.Delegated.get_ansible_native_hosts",
        return_value=[],
    )

    result = _instance.status()

    assert [s.instance_name for s in result] == [""]

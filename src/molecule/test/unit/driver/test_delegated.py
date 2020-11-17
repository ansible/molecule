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

import os

import pytest

from molecule import config
from molecule.driver import delegated
from molecule.test.conftest import is_subset


@pytest.fixture
def _driver_managed_section_data():
    return {
        "driver": {
            "name": "delegated",
            "options": {
                "managed": True,
            },
        }
    }


@pytest.fixture
def _driver_unmanaged_section_data():
    return {
        "driver": {
            "name": "delegated",
            "options": {
                "managed": False,
            },
        }
    }


@pytest.fixture
def _instance(config_instance):
    return delegated.Delegated(config_instance)


def test_config_private_member(_instance):
    assert isinstance(_instance._config, config.Config)


def test_testinfra_options_property(_instance):
    assert {
        "connection": "ansible",
        "ansible-inventory": _instance._config.provisioner.inventory_directory,
    } == _instance.testinfra_options


def test_name_property(_instance):
    assert "delegated" == _instance.name


@pytest.mark.parametrize(
    "config_instance", ["_driver_unmanaged_section_data"], indirect=True
)
def test_options_property(_instance):
    x = {
        "managed": False,
    }

    assert x == _instance.options


@pytest.mark.parametrize(
    "config_instance", ["_driver_managed_section_data"], indirect=True
)
def test_options_property_when_managed(_instance):
    x = {"managed": True}

    assert x == _instance.options


@pytest.mark.parametrize(
    "config_instance", ["_driver_managed_section_data"], indirect=True
)
def test_login_cmd_template_property_when_managed(_instance):
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


def test_safe_files_property(_instance):
    assert [] == _instance.safe_files


def test_default_safe_files_property(_instance):
    assert [] == _instance.default_safe_files


def test_delegated_property(_instance):
    assert _instance.delegated


def test_managed_property(_instance):
    assert _instance.managed


@pytest.mark.parametrize(
    "config_instance", ["_driver_unmanaged_section_data"], indirect=True
)
def test_default_ssh_connection_options_property(_instance):
    assert [] == _instance.default_ssh_connection_options


@pytest.mark.parametrize(
    "config_instance", ["_driver_managed_section_data"], indirect=True
)
def test_default_ssh_connection_options_property_when_managed(_instance):
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
    "config_instance", ["_driver_unmanaged_section_data"], indirect=True
)
def test_login_options(_instance):
    assert {"instance": "foo"} == _instance.login_options("foo")


@pytest.mark.parametrize(
    "config_instance", ["_driver_managed_section_data"], indirect=True
)
def test_login_options_when_managed(mocker, _instance):
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
    "config_instance", ["_driver_unmanaged_section_data"], indirect=True
)
def test_ansible_connection_options(_instance):
    x = {}

    assert is_subset(x, _instance.ansible_connection_options("foo"))


@pytest.mark.xfail(reason="Needs rewrite since switch to delegated")
@pytest.mark.parametrize(
    "config_instance", ["_driver_managed_section_data"], indirect=True
)
def test_ansible_connection_options_when_managed(mocker, _instance):

    assert _instance.managed is True

    ssh_case_data = mocker.patch(
        "molecule.driver.delegated.Delegated._get_instance_config"
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

    assert ssh_expected_data == _instance.ansible_connection_options("foo")

    winrm_case_data = mocker.patch(
        "molecule.driver.delegated.Delegated._get_instance_config"
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

    assert winrm_expected_data == _instance.ansible_connection_options("foo")


def test_ansible_connection_options_handles_missing_instance_config_managed(
    mocker, _instance
):
    m = mocker.patch("molecule.util.safe_load_file")
    m.side_effect = IOError

    assert {} == _instance.ansible_connection_options("foo")


def test_ansible_connection_options_handles_missing_results_key_when_managed(
    mocker, _instance
):
    m = mocker.patch("molecule.util.safe_load_file")
    m.side_effect = StopIteration

    assert {} == _instance.ansible_connection_options("foo")


def test_instance_config_property(_instance):
    x = os.path.join(
        _instance._config.scenario.ephemeral_directory, "instance_config.yml"
    )

    assert x == _instance.instance_config


@pytest.mark.parametrize(
    "config_instance", ["_driver_unmanaged_section_data"], indirect=True
)
def test_ssh_connection_options_property(_instance):
    assert [] == _instance.ssh_connection_options


def test_status(mocker, _instance):
    result = _instance.status()

    assert 2 == len(result)

    assert result[0].instance_name == "instance-1"
    assert result[0].driver_name == "delegated"
    assert result[0].provisioner_name == "ansible"
    assert result[0].scenario_name == "default"
    assert result[0].created == "false"
    assert result[0].converged == "false"

    assert result[1].instance_name == "instance-2"
    assert result[1].driver_name == "delegated"
    assert result[1].provisioner_name == "ansible"
    assert result[1].scenario_name == "default"
    assert result[1].created == "false"
    assert result[1].converged == "false"


def test_created(_instance):
    assert "false" == _instance._created()


@pytest.fixture
def _driver_options_managed_section_data():
    return {"driver": {"options": {"managed": False}}}


@pytest.mark.parametrize(
    "config_instance", ["_driver_options_managed_section_data"], indirect=True
)
def test_created_unknown_when_managed_false(
    _driver_options_managed_section_data, _instance
):
    assert "unknown" == _instance._created()


def test_property(_instance):
    assert "false" == _instance._converged()


def test_get_instance_config(mocker, _instance):
    m = mocker.patch("molecule.util.safe_load_file")
    m.return_value = [{"instance": "foo"}, {"instance": "bar"}]

    x = {"instance": "foo"}
    assert x == _instance._get_instance_config("foo")

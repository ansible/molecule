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
from molecule.driver import docker
from molecule.test.conftest import is_subset


@pytest.fixture
def _instance(config_instance):
    return docker.Docker(config_instance)


def test_config_private_member(_instance):
    assert isinstance(_instance._config, config.Config)


def test_testinfra_options_property(_instance):
    assert {
        "connection": "ansible",
        "ansible-inventory": _instance._config.provisioner.inventory_file,
    } == _instance.testinfra_options


def test_name_property(_instance):
    assert "docker" == _instance.name


def test_options_property(_instance):
    x = {"managed": True}

    assert x == _instance.options


def test_login_cmd_template_property(_instance):
    x = (
        "docker exec "
        "-e COLUMNS={columns} "
        "-e LINES={lines} "
        "-e TERM=bash "
        "-e TERM=xterm "
        "-ti {instance} bash"
    )

    assert x == _instance.login_cmd_template


def test_safe_files_property(_instance):
    x = [os.path.join(_instance._config.scenario.ephemeral_directory, "Dockerfile")]

    assert x == _instance.safe_files


def test_default_safe_files_property(_instance):
    x = [os.path.join(_instance._config.scenario.ephemeral_directory, "Dockerfile")]

    assert x == _instance.default_safe_files


def test_delegated_property(_instance):
    assert not _instance.delegated


def test_managed_property(_instance):
    assert _instance.managed


def test_default_ssh_connection_options_property(_instance):
    assert [] == _instance.default_ssh_connection_options


def test_login_options(_instance):
    assert {"instance": "foo"} == _instance.login_options("foo")


def test_ansible_connection_options(_instance):
    x = {"ansible_connection": "docker"}

    assert is_subset(x, _instance.ansible_connection_options("foo"))


def test_instance_config_property(_instance):
    x = os.path.join(
        _instance._config.scenario.ephemeral_directory, "instance_config.yml"
    )

    assert x == _instance.instance_config


def test_ssh_connection_options_property(_instance):
    assert [] == _instance.ssh_connection_options


def test_status(_instance):
    result = _instance.status()

    assert 2 == len(result)

    assert result[0].instance_name == "instance-1"
    assert result[0].driver_name == "docker"
    assert result[0].provisioner_name == "ansible"
    assert result[0].scenario_name == "default"
    assert result[0].created == "false"
    assert result[0].converged == "false"

    assert result[1].instance_name == "instance-2"
    assert result[1].driver_name == "docker"
    assert result[1].provisioner_name == "ansible"
    assert result[1].scenario_name == "default"
    assert result[1].created == "false"
    assert result[1].converged == "false"


def test_created(_instance):
    assert "false" == _instance._created()


def test_converged(_instance):
    assert "false" == _instance._converged()

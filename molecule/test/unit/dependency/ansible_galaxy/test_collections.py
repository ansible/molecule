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
import sh

from molecule import config
from molecule.dependency.ansible_galaxy import collections


@pytest.fixture
def _patched_ansible_galaxy_has_requirements_file(mocker):
    m = mocker.patch(
        (
            "molecule.dependency.ansible_galaxy.collections."
            "Collections._has_requirements_file"
        )
    )
    m.return_value = True

    return m


@pytest.fixture
def _dependency_section_data():
    return {
        "dependency": {
            "name": "galaxy",
            "options": {"foo": "bar", "v": True, "role-file": "bar.yml"},
            "env": {"FOO": "bar"},
        }
    }


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.fixture
def _instance(_dependency_section_data, patched_config_validate, config_instance):
    return collections.Collections(config_instance)


@pytest.fixture
def role_file(_instance):
    return os.path.join(_instance._config.scenario.directory, "collections.yml")


@pytest.fixture
def roles_path(_instance):
    return os.path.join(_instance._config.scenario.ephemeral_directory, "collections")


def test_config_private_member(_instance):
    assert isinstance(_instance._config, config.Config)


def test_default_options_property(_instance, role_file, roles_path):
    x = {"requirements-file": role_file, "collections-path": roles_path, "force": True}

    assert x == _instance.default_options


def test_default_env_property(_instance):
    env = _instance.default_env

    assert "MOLECULE_FILE" in env
    assert "MOLECULE_INVENTORY_FILE" in env
    assert "MOLECULE_SCENARIO_DIRECTORY" in env
    assert "MOLECULE_INSTANCE_CONFIG" in env


def test_name_property(_instance):
    assert "galaxy" == _instance.name


def test_enabled_property(_instance):
    assert _instance.enabled


@pytest.mark.parametrize("config_instance", ["_dependency_section_data"], indirect=True)
def test_options_property(_instance, role_file, roles_path):
    x = {
        "force": True,
        "requirements-file": role_file,
        "collections-path": roles_path,
        "foo": "bar",
        "v": True,
    }

    assert x == _instance.options


@pytest.mark.parametrize("config_instance", ["_dependency_section_data"], indirect=True)
def test_options_property_handles_cli_args(role_file, roles_path, _instance):
    _instance._config.args = {"debug": True}
    x = {
        "force": True,
        "requirements-file": role_file,
        "collections-path": roles_path,
        "foo": "bar",
        "vvv": True,
    }

    assert x == _instance.options


@pytest.mark.parametrize("config_instance", ["_dependency_section_data"], indirect=True)
def test_env_property(_instance):
    assert "bar" == _instance.env["FOO"]


@pytest.mark.parametrize("config_instance", ["_dependency_section_data"], indirect=True)
def test_bake(_instance, role_file, roles_path):
    _instance.bake()
    x = [
        str(sh.ansible_galaxy),
        "collection",
        "install",
        "--requirements-file={}".format(role_file),
        "--collections-path={}".format(roles_path),
        "--force",
        "--foo=bar",
        "-v",
    ]
    result = str(_instance._sh_command).split()

    assert sorted(x) == sorted(result)


def test_execute(
    patched_run_command,
    _patched_ansible_galaxy_has_requirements_file,
    patched_logger_success,
    _instance,
):
    _instance._sh_command = "patched-command"
    _instance.execute()

    role_directory = os.path.join(
        _instance._config.scenario.directory, _instance.options["collections-path"]
    )
    assert os.path.isdir(role_directory)

    patched_run_command.assert_called_once_with("patched-command", debug=False)

    msg = "Dependency completed successfully."
    patched_logger_success.assert_called_once_with(msg)


def test_execute_does_not_execute_when_disabled(
    patched_run_command, patched_logger_warning, _instance
):
    _instance._config.config["dependency"]["enabled"] = False
    _instance.execute()

    assert not patched_run_command.called

    msg = "Skipping, dependency is disabled."
    patched_logger_warning.assert_called_once_with(msg)


def test_execute_does_not_execute_when_no_requirements_file(
    patched_run_command,
    _patched_ansible_galaxy_has_requirements_file,
    patched_logger_warning,
    _instance,
):
    _patched_ansible_galaxy_has_requirements_file.return_value = False
    _instance.execute()

    assert not patched_run_command.called

    msg = "Skipped missing requirements file %s"
    assert patched_logger_warning.call_count == 1
    assert patched_logger_warning.call_args[0][0] == msg


def test_execute_bakes(
    patched_run_command,
    _instance,
    role_file,
    _patched_ansible_galaxy_has_requirements_file,
    roles_path,
):
    _instance.execute()
    assert _instance._sh_command is not None

    assert 1 == patched_run_command.call_count


def test_executes_catches_and_exits_return_code(
    patched_run_command, _patched_ansible_galaxy_has_requirements_file, _instance
):
    patched_run_command.side_effect = sh.ErrorReturnCode_1(sh.ansible_galaxy, b"", b"")
    with pytest.raises(SystemExit) as e:
        _instance.execute()

    assert 1 == e.value.code


def test_setup(_instance):
    role_directory = os.path.join(
        _instance._config.scenario.directory, _instance.options["collections-path"]
    )
    assert not os.path.isdir(role_directory)

    _instance._setup()

    assert os.path.isdir(role_directory)


def test_role_file(role_file, _instance):
    assert role_file == _instance.requirements_file


def test_has_requirements_file(_instance):
    assert not _instance._has_requirements_file()

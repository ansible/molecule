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

import os

import pytest

from molecule import config
from molecule.dependency.ansible_galaxy import roles


@pytest.fixture
def _patched_ansible_galaxy_has_requirements_file(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN202
    m = mocker.patch(
        "molecule.dependency.ansible_galaxy.roles.Roles._has_requirements_file",
    )
    m.return_value = True

    return m


@pytest.fixture
def _dependency_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {
        "dependency": {
            "name": "galaxy",
            "options": {"foo": "bar", "v": True, "requirements-file": "foo.yml"},
            "env": {"FOO": "bar"},
        },
    }


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.fixture
def _instance(  # type: ignore[no-untyped-def]  # noqa: ANN202
    _dependency_section_data,
    patched_config_validate,
    config_instance: config.Config,
):
    return roles.Roles(config_instance)


@pytest.fixture(name="role_file")
def fixture_role_file(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    return os.path.join(_instance._config.scenario.directory, "requirements.yml")  # noqa: PTH118


def test_roles_config_private_member(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert isinstance(_instance._config, config.Config)


def test_roles_default_options_property(_instance, role_file):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    x = {"role-file": role_file, "force": False}

    assert x == _instance.default_options


def test_roles_default_env_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    env = _instance.default_env

    assert "MOLECULE_FILE" in env
    assert "MOLECULE_INVENTORY_FILE" in env
    assert "MOLECULE_SCENARIO_DIRECTORY" in env
    assert "MOLECULE_INSTANCE_CONFIG" in env


def test_roles_name_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.name == "galaxy"


def test_roles_enabled_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.enabled


@pytest.mark.parametrize(
    "config_instance",
    ["_dependency_section_data"],  # noqa: PT007
    indirect=True,
)
def test_roles_options_property(_instance, role_file):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    x = {
        "force": False,
        "role-file": role_file,
        "foo": "bar",
        "v": True,
    }

    assert x == _instance.options


@pytest.mark.parametrize(
    "config_instance",
    ["_dependency_section_data"],  # noqa: PT007
    indirect=True,
)
def test_roles_options_property_handles_cli_args(role_file, _instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    _instance._config.args = {"debug": True}
    x = {
        "force": False,
        "role-file": role_file,
        "foo": "bar",
        "vvv": True,
    }

    assert x == _instance.options


@pytest.mark.parametrize(
    "config_instance",
    ["_dependency_section_data"],  # noqa: PT007
    indirect=True,
)
def test_roles_env_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.env["FOO"] == "bar"


@pytest.mark.parametrize(
    "config_instance",
    ["_dependency_section_data"],  # noqa: PT007
    indirect=True,
)
def test_galaxy_bake(_instance, role_file):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    _instance.bake()
    args = [
        "ansible-galaxy",
        "install",
        "--foo",
        "bar",
        "--role-file",
        role_file,
        "-v",
    ]
    assert _instance._sh_command == args


def test_execute(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    patched_run_command,
    _patched_ansible_galaxy_has_requirements_file,  # noqa: PT019
    caplog,
    _instance,  # noqa: PT019
):
    _instance._sh_command = "patched-command"
    _instance.execute()

    patched_run_command.assert_called_once_with(
        "patched-command",
        debug=False,
        check=True,
    )

    msg = "Dependency completed successfully."
    assert msg in caplog.text


def test_roles_execute_does_not_execute_when_disabled(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    patched_run_command,
    caplog,
    _instance,  # noqa: PT019
):
    _instance._config.config["dependency"]["enabled"] = False
    _instance.execute()

    assert not patched_run_command.called

    msg = "Skipping, dependency is disabled."
    assert msg in caplog.text


def test_roles_execute_does_not_execute_when_no_requirements_file(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    patched_run_command,
    _patched_ansible_galaxy_has_requirements_file,  # noqa: PT019
    caplog,
    _instance,  # noqa: PT019
):
    _patched_ansible_galaxy_has_requirements_file.return_value = False
    _instance.execute()

    assert not patched_run_command.called

    msg = "Skipping, missing the requirements file."
    assert msg in caplog.text


def test_roles_execute_bakes(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    patched_run_command,
    _instance,  # noqa: PT019
    role_file,
    _patched_ansible_galaxy_has_requirements_file,  # noqa: PT019
):
    _instance.execute()
    assert _instance._sh_command is not None

    assert patched_run_command.call_count == 1


def test_galaxy_executes_catches_and_exits_return_code(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    patched_run_command,
    _patched_ansible_galaxy_has_requirements_file,  # noqa: PT019
    _instance,  # noqa: PT019
):
    patched_run_command.side_effect = SystemExit(1)
    with pytest.raises(SystemExit) as e:
        _instance.execute()

    assert e.value.code == 1


def test_role_file(role_file, _instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert role_file == _instance.requirements_file


def test_roles_has_requirements_file(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert not _instance._has_requirements_file()

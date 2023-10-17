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

from molecule import config
from molecule.dependency import shell


@pytest.fixture()
def _dependency_section_data():
    return {
        "dependency": {
            "name": "shell",
            "command": "ls -l -a /tmp",
            "options": {"foo": "bar"},
            "env": {"FOO": "bar"},
        },
    }


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.fixture()
def _instance(
    _dependency_section_data,
    patched_config_validate,
    config_instance: config.Config,
):
    return shell.Shell(config_instance)


def test_shell_config_private_member(_instance):
    assert isinstance(_instance._config, config.Config)


def test_shell_default_options_property(_instance):
    x = {}

    assert x == _instance.default_options


def test_shell_default_env_property(_instance):
    assert "MOLECULE_FILE" in _instance.default_env
    assert "MOLECULE_INVENTORY_FILE" in _instance.default_env
    assert "MOLECULE_SCENARIO_DIRECTORY" in _instance.default_env
    assert "MOLECULE_INSTANCE_CONFIG" in _instance.default_env


@pytest.mark.parametrize("config_instance", ["_dependency_section_data"], indirect=True)
def test_shell_name_property(_instance):
    assert _instance.name == "shell"


def test_shell_enabled_property(_instance):
    assert _instance.enabled


@pytest.mark.parametrize("config_instance", ["_dependency_section_data"], indirect=True)
def test_shell_options_property(_instance):
    x = {"foo": "bar"}

    assert x == _instance.options


@pytest.mark.parametrize("config_instance", ["_dependency_section_data"], indirect=True)
def test_shell_options_property_handles_cli_args(_instance):
    _instance._config.args = {}
    x = {"foo": "bar"}

    assert x == _instance.options


@pytest.mark.parametrize("config_instance", ["_dependency_section_data"], indirect=True)
def test_shell_env_property(_instance):
    assert _instance.env["FOO"] == "bar"


def test_shell_execute(
    patched_run_command,
    caplog: pytest.LogCaptureFixture,
    _instance,
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


def test_shell_execute_does_not_execute_when_disabled(
    patched_run_command,
    caplog: pytest.LogCaptureFixture,
    _instance,
):
    _instance._config.config["dependency"]["enabled"] = False
    _instance.execute()

    assert not patched_run_command.called

    msg = "Skipping, dependency is disabled."
    assert msg in caplog.text


@pytest.mark.parametrize("config_instance", ["_dependency_section_data"], indirect=True)
def test_dependency_execute_bakes(patched_run_command, _instance):
    _instance.execute()
    assert patched_run_command.call_count == 1


@pytest.mark.parametrize("config_instance", ["_dependency_section_data"], indirect=True)
def test_dep_executes_catches_and_exits_return_code(patched_run_command, _instance):
    patched_run_command.side_effect = SystemExit(1)
    with pytest.raises(SystemExit) as e:
        _instance.execute()
    assert e.value.code == 1


def test_has_command_configured(_instance):
    assert _instance._has_command_configured()

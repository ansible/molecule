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

from molecule.config import Config
from molecule.util import write_file
from molecule.verifier import testinfra


@pytest.fixture
def _patched_testinfra_get_tests(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN202
    m = mocker.patch("molecule.verifier.testinfra.Testinfra._get_tests")
    m.return_value = ["foo.py", "bar.py"]

    return m


@pytest.fixture
def _verifier_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {
        "verifier": {
            "name": "testinfra",
            "options": {"foo": "bar", "v": True, "verbose": True},
            "additional_files_or_dirs": ["file1.py", "file2.py", "match*.py", "dir/*"],
            "env": {"FOO": "bar"},
        },
    }


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.fixture
def _instance(patched_config_validate, config_instance: Config):  # type: ignore[no-untyped-def]  # noqa: ANN202
    return testinfra.Testinfra(config_instance)


@pytest.fixture
def inventory_file(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    return _instance._config.provisioner.inventory_file


@pytest.fixture(name="inventory_directory")
def fixture_inventory_directory(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    return _instance._config.provisioner.inventory_directory


def test_testinfra_config_private_member(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert isinstance(_instance._config, Config)


def test_testinfra_default_options_property(inventory_directory, _instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    x = {
        "connection": "ansible",
        "ansible-inventory": inventory_directory,
        "p": "no:cacheprovider",
    }

    assert x == _instance.default_options


def test_default_options_property_updates_debug(inventory_directory, _instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    _instance._config.args = {"debug": True}
    x = {
        "connection": "ansible",
        "ansible-inventory": inventory_directory,
        "debug": True,
        "vvv": True,
        "p": "no:cacheprovider",
    }

    assert x == _instance.default_options


def test_default_options_property_updates_sudo(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    inventory_directory,
    _instance,  # noqa: PT019
    _patched_testinfra_get_tests,  # noqa: PT019
):
    _instance._config.args = {"sudo": True}
    x = {
        "connection": "ansible",
        "ansible-inventory": inventory_directory,
        "sudo": True,
        "p": "no:cacheprovider",
    }

    assert x == _instance.default_options


def test_testinfra_default_env_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert "MOLECULE_FILE" in _instance.default_env
    assert "MOLECULE_INVENTORY_FILE" in _instance.default_env
    assert "MOLECULE_SCENARIO_DIRECTORY" in _instance.default_env
    assert "MOLECULE_INSTANCE_CONFIG" in _instance.default_env


@pytest.mark.parametrize(
    "config_instance",
    ["_verifier_section_data"],  # noqa: PT007
    indirect=True,
)
def test_additional_files_or_dirs_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    tests_directory = _instance._config.verifier.directory
    file1_file = os.path.join(tests_directory, "file1.py")  # noqa: PTH118
    file2_file = os.path.join(tests_directory, "file2.py")  # noqa: PTH118
    match1_file = os.path.join(tests_directory, "match1.py")  # noqa: PTH118
    match2_file = os.path.join(tests_directory, "match2.py")  # noqa: PTH118
    test_subdir = os.path.join(tests_directory, "dir")  # noqa: PTH118
    test_subdir_file = os.path.join(test_subdir, "test_subdir_file.py")  # noqa: PTH118

    os.mkdir(tests_directory)  # noqa: PTH102
    os.mkdir(test_subdir)  # noqa: PTH102
    for f in [file1_file, file2_file, match1_file, match2_file, test_subdir_file]:
        write_file(f, "")

    x = [file1_file, file2_file, match1_file, match2_file, test_subdir_file]
    assert sorted(x) == sorted(_instance.additional_files_or_dirs)


@pytest.mark.parametrize(
    "config_instance",
    ["_verifier_section_data"],  # noqa: PT007
    indirect=True,
)
def test_testinfra_env_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.env["FOO"] == "bar"
    assert "ANSIBLE_CONFIG" in _instance.env


def test_testinfra_name_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.name == "testinfra"


def test_testinfra_enabled_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.enabled


def test_testinfra_directory_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    parts = _instance.directory.split(os.path.sep)

    assert parts[-3:] == ["molecule", "default", "tests"]


@pytest.fixture
def _verifier_testinfra_directory_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {"verifier": {"name": "testinfra", "directory": "/tmp/foo/bar"}}  # noqa: S108


@pytest.mark.parametrize(
    "config_instance",
    ["_verifier_testinfra_directory_section_data"],  # noqa: PT007
    indirect=True,
)
def test_directory_property_overridden(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.directory == "/tmp/foo/bar"  # noqa: S108


@pytest.mark.parametrize(
    "config_instance",
    ["_verifier_section_data"],  # noqa: PT007
    indirect=True,
)
def test_testinfra_options_property(inventory_directory, _instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    x = {
        "connection": "ansible",
        "ansible-inventory": inventory_directory,
        "foo": "bar",
        "v": True,
        "verbose": True,
        "p": "no:cacheprovider",
    }

    assert x == _instance.options


@pytest.mark.parametrize(
    "config_instance",
    ["_verifier_section_data"],  # noqa: PT007
    indirect=True,
)
def test_testinfra_options_property_handles_cli_args(inventory_directory, _instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    _instance._config.args = {"debug": True}
    x = {
        "connection": "ansible",
        "ansible-inventory": inventory_directory,
        "foo": "bar",
        "debug": True,
        "vvv": True,
        "verbose": True,
        "p": "no:cacheprovider",
    }

    assert x == _instance.options


@pytest.mark.parametrize(
    "config_instance",
    ["_verifier_section_data"],  # noqa: PT007
    indirect=True,
)
def test_testinfra_bake(_patched_testinfra_get_tests, inventory_directory, _instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    _instance._tests = ["foo.py", "bar.py"]
    _instance.bake()
    args = [
        "pytest",
        "--ansible-inventory",
        inventory_directory,
        "--connection",
        "ansible",
        "--foo",
        "bar",
        "-p",
        "no:cacheprovider",
        "foo.py",
        "bar.py",
        "-v",
    ]

    assert _instance._testinfra_command == args


def test_testinfra_execute(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    caplog,
    patched_run_command,
    _patched_testinfra_get_tests,  # noqa: PT019
    _instance,  # noqa: PT019
):
    _instance.execute()

    patched_run_command.assert_called_once()

    msg = f"Executing Testinfra tests found in {_instance.directory}/..."
    msg2 = "Verifier completed successfully."
    assert msg in caplog.text
    assert msg2 in caplog.text
    assert patched_run_command.call_args[0][0][0] == "pytest"


def test_testinfra_execute_does_not_execute(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    patched_run_command,
    caplog,
    _instance,  # noqa: PT019
):
    _instance._config.config["verifier"]["enabled"] = False
    _instance.execute()

    assert not patched_run_command.called

    msg = "Skipping, verifier is disabled."
    assert msg in caplog.text


def test_does_not_execute_without_tests(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    patched_run_command,
    caplog,
    _instance,  # noqa: PT019
):
    _instance.execute()

    assert not patched_run_command.called

    msg = "Skipping, no tests found."
    assert msg in caplog.text


def test_testinfra_execute_bakes(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    patched_run_command,
    _patched_testinfra_get_tests,  # noqa: PT019
    _instance,  # noqa: PT019
):
    _instance.execute()

    assert _instance._testinfra_command is not None

    assert patched_run_command.call_count == 1


@pytest.mark.parametrize(
    "config_instance",
    ["_verifier_section_data"],  # noqa: PT007
    indirect=True,
)
def test_execute_bakes_env(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    patched_run_command,
    _patched_testinfra_get_tests,  # noqa: PT019
    inventory_directory,
    _instance,  # noqa: PT019
):
    _instance.execute()

    assert patched_run_command.call_args[1]["env"]["FOO"] == "bar"


def test_testinfra_executes_catches_and_exits_return_code(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    patched_run_command,
    _patched_testinfra_get_tests,  # noqa: PT019
    _instance,  # noqa: PT019
):
    patched_run_command.side_effect = SystemExit(1)
    with pytest.raises(SystemExit) as e:
        _instance.execute()

    assert e.value.code == 1

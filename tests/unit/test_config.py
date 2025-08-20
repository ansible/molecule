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

import logging
import os

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import pytest

from molecule import config, platforms, scenario, state, util
from molecule.dependency import ansible_galaxy, shell
from molecule.provisioner import ansible
from molecule.verifier.ansible import Ansible as AnsibleVerifier


if TYPE_CHECKING:
    from typing import Literal
    from unittest.mock import Mock

    from pytest_mock import MockerFixture

    from molecule.types import DependencyData, DriverData


def test_args_member(config_instance: config.Config) -> None:  # noqa: D103
    assert config_instance.args == {}


def test_command_args_member(config_instance: config.Config) -> None:  # noqa: D103
    x = {"subcommand": "test"}

    assert x == config_instance.command_args


def test_debug_property(config_instance: config.Config) -> None:  # noqa: D103
    assert not config_instance.debug


def test_env_file_property(config_instance: config.Config) -> None:  # noqa: D103
    config_instance.args = {"env_file": ".env"}
    result = config_instance.env_file

    x = config_instance.args.get("env_file")
    assert isinstance(x, str)
    assert util.abs_path(x) == result


def test_subcommand_property(config_instance: config.Config) -> None:  # noqa: D103
    assert config_instance.subcommand == "test"


def test_action_property(config_instance: config.Config) -> None:  # noqa: D103
    assert config_instance.action is None


def test_action_setter(config_instance: config.Config) -> None:  # noqa: D103
    config_instance.action = "foo"

    assert config_instance.action == "foo"


def test_init_calls_validate(  # noqa: D103
    patched_config_validate: Mock,
    config_instance: config.Config,
) -> None:
    patched_config_validate.assert_called_once_with()


def test_collection_directory_property(
    monkeypatch: pytest.MonkeyPatch,
    config_instance: config.Config,
    resources_folder_path: Path,
) -> None:
    """Test collection_directory property.

    Args:
        monkeypatch: Pytest fixture.
        config_instance: Instance of Config.
        resources_folder_path: Path to resources directory holding a valid collection.
    """
    # default path is not in a collection
    assert config_instance.collection_directory is None

    # Change directory to collection root to test collection detection
    collection_path = resources_folder_path / "sample-collection"
    monkeypatch.chdir(collection_path)

    # Clear the cache so detection runs again with new cwd
    util.get_collection_metadata.cache_clear()

    # Clear cached property so it will be re-evaluated in new directory
    if "collection_directory" in config_instance.__dict__:
        delattr(config_instance, "collection_directory")

    assert config_instance.collection_directory == collection_path


def test_project_directory_property(config_instance: config.Config) -> None:  # noqa: D103
    assert str(Path.cwd()) == config_instance.project_directory


def test_molecule_directory_property(config_instance: config.Config) -> None:  # noqa: D103
    x = str(Path.cwd() / "molecule")

    assert x == config_instance.molecule_directory


def test_collection_property(
    monkeypatch: pytest.MonkeyPatch,
    config_instance: config.Config,
    resources_folder_path: Path,
) -> None:
    """Test collection property.

    Args:
        monkeypatch: Pytest fixture.
        config_instance: Instance of Config.
        resources_folder_path: Path to resources directory holding a valid collection.
    """
    # Clear any cached collection detection from previous tests
    util.get_collection_metadata.cache_clear()

    # Clear cached property on config instance if it exists
    if "collection" in config_instance.__dict__:
        delattr(config_instance, "collection")

    # default path is not in a collection
    assert config_instance.collection is None

    # Change directory to collection root to test collection detection
    collection_path = resources_folder_path / "sample-collection"
    monkeypatch.chdir(collection_path)

    # Clear the cache so detection runs again with new cwd
    util.get_collection_metadata.cache_clear()

    # Clear cached property so it will be re-evaluated in new directory
    if "collection" in config_instance.__dict__:
        delattr(config_instance, "collection")

    assert config_instance.collection is not None
    assert config_instance.collection["name"] == "goodies"
    assert config_instance.collection["namespace"] == "acme"


def test_collection_property_broken_collection(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    config_instance: config.Config,
    resources_folder_path: Path,
) -> None:
    """Test collection property with a malformed galaxy.yml.

    Args:
        monkeypatch: Pytest fixture.
        caplog: pytest log capture fixture.
        config_instance: Instance of Config.
        resources_folder_path: Path to resources directory holding a valid collection.
    """
    # Change directory to broken collection root to test collection detection
    collection_path = resources_folder_path / "broken-collection"
    monkeypatch.chdir(collection_path)

    # Clear the cache so detection runs again with new cwd
    util.get_collection_metadata.cache_clear()

    # Clear cached property so it will be re-evaluated in new directory
    if "collection" in config_instance.__dict__:
        delattr(config_instance, "collection")

    assert config_instance.collection is None

    msg = "is missing required fields: 'namespace'"
    assert msg in caplog.text


def test_dependency_property(config_instance: config.Config) -> None:  # noqa: D103
    assert isinstance(config_instance.dependency, ansible_galaxy.AnsibleGalaxy)


@pytest.fixture
def _config_dependency_shell_section_data() -> dict[Literal["dependency"], DependencyData]:
    return {"dependency": {"name": "shell", "command": "bin/command"}}


@pytest.mark.parametrize(
    "config_instance",
    ["_config_dependency_shell_section_data"],  # noqa: PT007
    indirect=True,
)
def test_dependency_property_is_shell(config_instance: config.Config) -> None:  # noqa: D103
    assert isinstance(config_instance.dependency, shell.Shell)


@pytest.fixture
def _config_driver_delegated_section_data() -> dict[Literal["driver"], DriverData]:
    return {"driver": {"name": "default", "options": {"managed": False}}}


def test_env(config_instance: config.Config) -> None:  # noqa: D103
    config_instance.args = {"env_file": ".env"}
    env_file = config_instance.args.get("env_file")
    assert isinstance(env_file, str)
    x = {
        "MOLECULE_DEBUG": "False",
        "MOLECULE_FILE": config_instance.config_file,
        "MOLECULE_ENV_FILE": util.abs_path(env_file),
        "MOLECULE_INVENTORY_FILE": config_instance.provisioner.inventory_file,  # type: ignore[union-attr]
        "MOLECULE_EPHEMERAL_DIRECTORY": config_instance.scenario.ephemeral_directory,
        "MOLECULE_SCENARIO_DIRECTORY": config_instance.scenario.directory,
        "MOLECULE_PROJECT_DIRECTORY": config_instance.project_directory,
        "MOLECULE_INSTANCE_CONFIG": config_instance.driver.instance_config,
        "MOLECULE_DEPENDENCY_NAME": "galaxy",
        "MOLECULE_DRIVER_NAME": "default",
        "MOLECULE_PROVISIONER_NAME": "ansible",
        "MOLECULE_SCENARIO_NAME": "default",
        "MOLECULE_STATE_FILE": config_instance.state.state_file,
        "MOLECULE_VERIFIER_NAME": "ansible",
        "MOLECULE_VERIFIER_TEST_DIRECTORY": config_instance.verifier.directory,
    }

    assert x == config_instance.env


def test_platforms_property(config_instance: config.Config) -> None:  # noqa: D103
    assert isinstance(config_instance.platforms, platforms.Platforms)


def test_provisioner_property(config_instance: config.Config) -> None:  # noqa: D103
    assert isinstance(config_instance.provisioner, ansible.Ansible)


def test_scenario_property(config_instance: config.Config) -> None:  # noqa: D103
    assert isinstance(config_instance.scenario, scenario.Scenario)


def test_state_property(config_instance: config.Config) -> None:  # noqa: D103
    assert isinstance(config_instance.state, state.State)


def test_verifier_property_is_ansible(config_instance: config.Config) -> None:  # noqa: D103
    assert isinstance(config_instance.verifier, AnsibleVerifier)


def test_verifier_property_invalid(config_instance: config.Config) -> None:  # noqa: D103
    config_instance.config["verifier"]["name"] = "missing"
    del config_instance.verifier

    with pytest.raises(RuntimeError, match="Unable to find 'missing' verifier driver."):
        config_instance.verifier  # noqa: B018


def test_get_driver_name_from_state_file(  # noqa: D103
    config_instance: config.Config,
    mocker: MockerFixture,
) -> None:
    config_instance.state.change_state("driver", "state-driver")

    with pytest.raises(SystemExit):
        config_instance._get_driver_name()

    mocker.patch("molecule.api.drivers", return_value=["state-driver"])
    assert config_instance._get_driver_name() == "state-driver"


def test_get_driver_name_from_cli(config_instance: config.Config) -> None:  # noqa: D103
    config_instance.command_args = {"driver_name": "cli-driver"}

    assert config_instance._get_driver_name() == "cli-driver"


def test_get_driver_name(config_instance: config.Config) -> None:  # noqa: D103
    assert config_instance._get_driver_name() == "default"


def test_get_driver_name_raises_when_different_driver_used(  # noqa: D103
    caplog: pytest.LogCaptureFixture,
    config_instance: config.Config,
) -> None:
    config_instance.state.change_state("driver", "foo")
    config_instance.command_args = {"driver_name": "bar"}
    with pytest.raises(SystemExit) as e:
        config_instance._get_driver_name()

    assert e.value.code == 1

    msg = (
        "Instance(s) were created with the 'foo' driver, but the subcommand is using 'bar' driver."
    )

    assert msg in caplog.text


def test_get_config(config_instance: config.Config) -> None:  # noqa: D103
    assert isinstance(config_instance._get_config(), dict)


def test_get_config_with_base_config(config_instance: config.Config) -> None:  # noqa: D103
    config_instance.args = {"base_config": ["./foo.yml"]}
    contents = {"foo": "bar"}
    util.write_file(config_instance.args["base_config"][0], util.safe_dump(contents))
    result = config_instance._get_config()

    assert result["foo"] == "bar"  # type: ignore[typeddict-item]


def test_get_config_with_multiple_base_configs(  # noqa: D103
    config_instance: config.Config,
) -> None:
    config_instance.args = {"base_config": ["./foo.yml", "./foo2.yml"]}
    contents = {"foo": "bar", "foo2": "bar"}
    util.write_file(config_instance.args["base_config"][0], util.safe_dump(contents))
    contents = {"foo2": "bar2"}
    util.write_file(config_instance.args["base_config"][1], util.safe_dump(contents))
    result = config_instance._get_config()

    assert result["foo"] == "bar"  # type: ignore[typeddict-item]
    assert result["foo2"] == "bar2"  # type: ignore[typeddict-item]


def test_reget_config(config_instance: config.Config) -> None:  # noqa: D103
    assert isinstance(config_instance._reget_config(), dict)


def test_interpolate(config_instance: config.Config) -> None:  # noqa: D103
    string = "foo: $HOME"
    x = f"foo: {os.environ['HOME']}"

    assert x == config_instance._interpolate(string, os.environ, "")


def test_interpolate_curly(config_instance: config.Config) -> None:  # noqa: D103
    string = "foo: ${HOME}"
    x = f"foo: {os.environ['HOME']}"

    assert x == config_instance._interpolate(string, os.environ, "")


def test_interpolate_default(config_instance: config.Config) -> None:  # noqa: D103
    string = "foo: ${NONE-default}"
    x = "foo: default"

    assert x == config_instance._interpolate(string, os.environ, "")


def test_interpolate_default_colon(config_instance: config.Config) -> None:  # noqa: D103
    string = "foo: ${NONE:-default}"
    x = "foo: default"

    assert x == config_instance._interpolate(string, os.environ, "")


def test_interpolate_default_variable(config_instance: config.Config) -> None:  # noqa: D103
    string = "foo: ${NONE:-$HOME}"
    x = f"foo: {os.environ['HOME']}"

    assert x == config_instance._interpolate(string, os.environ, "")


def test_interpolate_curly_default_variable(  # noqa: D103
    config_instance: config.Config,
) -> None:
    string = "foo: ${NONE-$HOME}"
    x = f"foo: {os.environ['HOME']}"

    assert x == config_instance._interpolate(string, os.environ, "")


def test_interpolate_raises_on_failed_interpolation(  # noqa: D103
    caplog: pytest.LogCaptureFixture,
    config_instance: config.Config,
) -> None:
    string = "$6$8I5Cfmpr$kGZB"

    with pytest.raises(SystemExit) as e:
        config_instance._interpolate(string, os.environ, "")

    assert e.value.code == 1

    msg = (
        f"parsing config file '{config_instance.molecule_file}'.\n\n"
        "Invalid placeholder in string: line 1, col 1\n"
        "$6$8I5Cfmpr$kGZB"
    )
    assert msg in caplog.text


def test_get_defaults(  # noqa: D103
    config_instance: config.Config,
    mocker: MockerFixture,
) -> None:
    mocker.patch.object(
        config_instance,
        "molecule_file",
        "/path/to/test_scenario_name/molecule.yml",
    )
    defaults = config_instance._get_defaults()
    assert defaults["scenario"]["name"] == "test_scenario_name"


def test_validate(  # noqa: D103
    monkeypatch: pytest.MonkeyPatch,
    config_instance: config.Config,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Mock the schema validation function using monkeypatch
    mock_calls = []

    def mock_validate(config_data: dict[str, object]) -> None:
        mock_calls.append(config_data)

    monkeypatch.setattr("molecule.model.schema_v3.validate", mock_validate)

    with caplog.at_level(logging.DEBUG):
        config_instance._validate()

    # Check that debug message was logged
    assert len(caplog.records) >= 1, (
        f"Expected at least 1 log record but got {len(caplog.records)}. "
        f"Scenario: {config_instance.scenario.name}"
    )

    # Find the validation record (there might be multiple records)
    validation_record = None
    for record in caplog.records:
        if "Validating schema" in record.getMessage():
            validation_record = record
            break

    assert validation_record is not None, "Should find validation message in log records"
    assert validation_record.levelname == "DEBUG"  # cspell:ignore levelname

    # Verify mock was called once
    assert len(mock_calls) == 1
    assert mock_calls[0] == config_instance.config


def test_validate_exists_when_validation_fails(  # noqa: D103
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
    config_instance: config.Config,
) -> None:
    m = mocker.patch("molecule.model.schema_v3.validate")
    m.return_value = "validation errors"

    with pytest.raises(SystemExit) as e:
        config_instance._validate()

    assert e.value.code == 1

    msg = f"Failed to validate {config_instance.molecule_file}\n\nvalidation errors"
    assert msg in caplog.text


def test_molecule_directory() -> None:  # noqa: D103
    assert config.molecule_directory("/foo/bar") == "/foo/bar/molecule"


def test_molecule_file() -> None:  # noqa: D103
    assert config.molecule_file("/foo/bar") == "/foo/bar/molecule.yml"


def test_set_env_from_file(config_instance: config.Config) -> None:  # noqa: D103
    config_instance.args = {"env_file": ".env"}
    contents = {"foo": "bar", "BAZ": "zzyzx"}
    env_file = config_instance.args.get("env_file")
    assert isinstance(env_file, str)
    util.write_file(env_file, util.safe_dump(contents))
    env = config.set_env_from_file({}, env_file)

    assert contents == env


def test_set_env_from_file_returns_original_env_when_env_file_not_found(  # noqa: D103
    config_instance: config.Config,
) -> None:
    env = config.set_env_from_file({}, "file-not-found")

    assert env == {}


def test_write_config(config_instance: config.Config) -> None:  # noqa: D103
    config_instance.write()

    assert os.path.isfile(config_instance.config_file)  # noqa: PTH113


# Test ansible section functionality


def test_ansible_section_defaults() -> None:
    """Test that ansible section gets proper defaults."""
    config_instance = config.Config(molecule_file="")
    defaults = config_instance._get_defaults()

    assert "ansible" in defaults
    assert not defaults["ansible"]["cfg"]
    assert defaults["ansible"]["executor"]["backend"] == "ansible-playbook"
    assert not defaults["ansible"]["executor"]["args"]["ansible_navigator"]
    assert not defaults["ansible"]["executor"]["args"]["ansible_playbook"]
    assert not defaults["ansible"]["env"]
    # Playbooks now have default filenames
    expected_playbooks = {
        "cleanup": "cleanup.yml",
        "create": "create.yml",
        "converge": "converge.yml",
        "destroy": "destroy.yml",
        "prepare": "prepare.yml",
        "side_effect": "side_effect.yml",
        "verify": "verify.yml",
    }
    assert defaults["ansible"]["playbooks"] == expected_playbooks


def test_executor_property_uses_ansible_section() -> None:
    """Test that the executor property uses ansible.executor.backend when present."""
    config_data: dict[str, Any] = {
        "ansible": {"executor": {"backend": "ansible-navigator"}},
    }
    config_instance = config.Config(molecule_file="")
    config_instance.config = config_data  # type: ignore[assignment]

    assert config_instance.executor == "ansible-navigator"


def test_ansible_section_no_default_platforms() -> None:
    """Test that no default platforms are provided - empty list."""
    config_instance = config.Config(molecule_file="")
    defaults = config_instance._get_defaults()

    assert not defaults["platforms"]

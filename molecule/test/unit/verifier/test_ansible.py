import os

import pytest

from molecule import config
from molecule.verifier import ansible


@pytest.fixture
def _patched_ansible_verify(mocker):
    m = mocker.patch("molecule.provisioner.ansible.Ansible.verify")
    m.return_value = "patched-ansible-verify-stdout"

    return m


@pytest.fixture
def _verifier_section_data():
    return {"verifier": {"name": "ansible", "env": {"FOO": "bar"}}}


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.fixture
def _instance(_verifier_section_data, patched_config_validate, config_instance):
    return ansible.Ansible(config_instance)


def test_config_private_member(_instance):
    assert isinstance(_instance._config, config.Config)


def test_default_options_property(_instance):
    assert {} == _instance.default_options


def test_default_env_property(_instance):
    assert "MOLECULE_FILE" in _instance.default_env
    assert "MOLECULE_INVENTORY_FILE" in _instance.default_env
    assert "MOLECULE_SCENARIO_DIRECTORY" in _instance.default_env
    assert "MOLECULE_INSTANCE_CONFIG" in _instance.default_env


@pytest.mark.parametrize("config_instance", ["_verifier_section_data"], indirect=True)
def test_env_property(_instance):
    assert "bar" == _instance.env["FOO"]


def test_name_property(_instance):
    assert "ansible" == _instance.name


def test_enabled_property(_instance):
    assert _instance.enabled


def test_directory_property(_instance):
    parts = _instance.directory.split(os.path.sep)
    # Unused by Ansible verifier
    assert ["molecule", "default", "tests"] == parts[-3:]


@pytest.mark.parametrize("config_instance", ["_verifier_section_data"], indirect=True)
def test_options_property(_instance):
    x = {}

    assert x == _instance.options


@pytest.mark.parametrize("config_instance", ["_verifier_section_data"], indirect=True)
def test_options_property_handles_cli_args(_instance):
    _instance._config.args = {"debug": True}
    x = {}

    assert x == _instance.options


def test_execute(
    patched_logger_info, _patched_ansible_verify, patched_logger_success, _instance
):
    _instance.execute()

    _patched_ansible_verify.assert_called_once_with()

    msg = "Running Ansible Verifier"
    patched_logger_info.assert_called_once_with(msg)

    msg = "Verifier completed successfully."
    patched_logger_success.assert_called_once_with(msg)


def test_execute_does_not_execute(
    patched_ansible_converge, patched_logger_warning, _instance
):
    _instance._config.config["verifier"]["enabled"] = False
    _instance.execute()

    assert not patched_ansible_converge.called

    msg = "Skipping, verifier is disabled."
    patched_logger_warning.assert_called_once_with(msg)

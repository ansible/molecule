"""Unit tests for the ansible verifier module."""

from __future__ import annotations

import os

import pytest

from molecule import config
from molecule.verifier import ansible


@pytest.fixture
def _patched_ansible_verify(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN202
    m = mocker.patch("molecule.provisioner.ansible.Ansible.verify")
    m.return_value = "patched-ansible-verify-stdout"

    return m


@pytest.fixture
def _verifier_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {"verifier": {"name": "ansible", "env": {"FOO": "bar"}}}


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.fixture
def _instance(  # type: ignore[no-untyped-def]  # noqa: ANN202
    _verifier_section_data,
    patched_config_validate,
    config_instance: config.Config,
):
    return ansible.Ansible(config_instance)


def test_verifier_config_private_member(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert isinstance(_instance._config, config.Config)


def test_verifier_default_options_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.default_options == {}


def test_verifier_ansible_default_env_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert "MOLECULE_FILE" in _instance.default_env
    assert "MOLECULE_INVENTORY_FILE" in _instance.default_env
    assert "MOLECULE_SCENARIO_DIRECTORY" in _instance.default_env
    assert "MOLECULE_INSTANCE_CONFIG" in _instance.default_env


@pytest.mark.parametrize(
    "config_instance",
    ["_verifier_section_data"],  # noqa: PT007
    indirect=True,
)
def test_verifier_env_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.env["FOO"] == "bar"


def test_verifier_name_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.name == "ansible"


def test_ansible_enabled_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance.enabled


def test_verifier_directory_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    parts = _instance.directory.split(os.path.sep)
    # Unused by Ansible verifier
    assert parts[-3:] == ["molecule", "default", "tests"]


@pytest.mark.parametrize(
    "config_instance",
    ["_verifier_section_data"],  # noqa: PT007
    indirect=True,
)
def test_verifier_ansible_options_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    x = {}  # type: ignore[var-annotated]

    assert x == _instance.options


@pytest.mark.parametrize(
    "config_instance",
    ["_verifier_section_data"],  # noqa: PT007
    indirect=True,
)
def test_verifier_ansible_options_property_handles_cli_args(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    _instance._config.args = {"debug": True}
    x = {}  # type: ignore[var-annotated]

    assert x == _instance.options


def test_ansible_execute(caplog, _patched_ansible_verify, _instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    _instance.execute()

    _patched_ansible_verify.assert_called_once_with(None)

    msg = "Running Ansible Verifier"
    assert msg in caplog.text

    msg = "Verifier completed successfully."
    assert msg in caplog.text


def test_execute_does_not_execute(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    patched_ansible_converge,
    caplog: pytest.LogCaptureFixture,
    _instance,  # noqa: PT019
):
    _instance._config.config["verifier"]["enabled"] = False
    _instance.execute()

    assert not patched_ansible_converge.called

    msg = "Skipping, verifier is disabled."
    assert msg in caplog.text

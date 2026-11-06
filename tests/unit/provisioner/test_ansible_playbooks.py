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

from typing import TYPE_CHECKING

import pytest

from molecule import util
from molecule.provisioner import ansible_playbooks
from tests.unit.conftest import os_split  # pylint:disable=C0411


if TYPE_CHECKING:
    from pathlib import Path

    from molecule import config


@pytest.fixture
def _provisioner_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {"provisioner": {"name": "ansible", "options": {}, "config_options": {}}}


@pytest.fixture
def _instance(_provisioner_section_data, config_instance: config.Config):  # type: ignore[no-untyped-def]  # noqa: ANN202
    return ansible_playbooks.AnsiblePlaybooks(config_instance)


def test_cleanup_property_is_optional(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance._config.provisioner.playbooks.cleanup is None


@pytest.mark.skip(reason="create not running for delegated")
def test_create_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    x = os.path.join(_instance._get_playbook_directory(), "default", "create.yml")  # noqa: PTH118

    assert x == _instance._config.provisioner.playbooks.create


def test_converge_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    x = os.path.join(_instance._config.scenario.directory, "converge.yml")  # noqa: PTH118

    assert x == _instance._config.provisioner.playbooks.converge


@pytest.mark.skip(reason="destroy not running for delegated")
def test_destroy_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    x = os.path.join(_instance._get_playbook_directory(), "default", "destroy.yml")  # noqa: PTH118

    assert x == _instance._config.provisioner.playbooks.destroy


def test_prepare_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance._config.provisioner.playbooks.prepare is None


def test_side_effect_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance._config.provisioner.playbooks.side_effect is None


def test_verify_property(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    assert _instance._config.provisioner.playbooks.verify is None


def test_get_playbook_directory(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    result = _instance._get_playbook_directory()
    parts = os_split(result)
    x = ("molecule", "provisioner", "ansible", "playbooks")

    assert x == parts[-4:]


def test_get_playbook(tmpdir, _instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    x = os.path.join(_instance._config.scenario.directory, "create.yml")  # noqa: PTH118
    util.write_file(x, "")

    assert x == _instance._get_playbook("create")


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        ("example.infra.create", True),
        ("example.infra.create.yml", True),
        ("example.infra.lifecycle.create", True),
        ("example.infra.create.yaml", True),
        ("create.yml", False),
        ("foo.bar.yml", False),
        ("./example.infra.create", False),
        ("/var/example.infra.create", False),
        ("Example.infra.create", False),
        ("example.infra.bad-name", False),
    ),
)
def test_is_collection_playbook_reference(  # noqa: D103
    value: str,
    expected: bool,  # noqa: FBT001
) -> None:
    assert ansible_playbooks.is_collection_playbook_reference(value) is expected


@pytest.mark.parametrize(
    ("section", "reference"),
    (
        ("cleanup", "example.infra.cleanup"),
        ("create", "example.infra.create.yml"),
        ("converge", "example.infra.converge"),
        ("destroy", "example.infra.destroy.yml"),
        ("prepare", "example.infra.lifecycle.prepare"),
        ("side_effect", "example.infra.side_effect"),
        ("verify", "example.infra.verify.yml"),
    ),
)
def test_get_playbook_returns_collection_reference_unchanged(  # noqa: D103
    _instance: ansible_playbooks.AnsiblePlaybooks,  # noqa: PT019
    monkeypatch: pytest.MonkeyPatch,
    section: ansible_playbooks.Section,
    reference: str,
) -> None:
    assert _instance._config.provisioner
    _instance._config.config_data["ansible"]["playbooks"][section] = reference
    monkeypatch.setattr(
        _instance,
        "_get_bundled_driver_playbook",
        lambda _: pytest.fail("collection reference should bypass driver fallback"),
    )

    assert _instance._get_playbook(section) == reference


def test_get_playbook_existing_dotted_local_file_precedes_reference(  # noqa: D103
    _instance: ansible_playbooks.AnsiblePlaybooks,  # noqa: PT019
) -> None:
    assert _instance._config.provisioner
    reference = "example.infra.create"
    _instance._config.config_data["ansible"]["playbooks"]["create"] = reference
    local_path = _instance._config.provisioner.abs_path(reference)
    util.write_file(local_path, "")

    assert _instance._get_playbook("create") == local_path


def test_get_playbook_explicit_dotted_path_uses_local_behavior(  # noqa: D103
    _instance: ansible_playbooks.AnsiblePlaybooks,  # noqa: PT019
) -> None:
    assert _instance._config.provisioner
    configured = "./example.infra.create"
    _instance._config.config_data["ansible"]["playbooks"]["create"] = configured
    local_path = _instance._config.provisioner.abs_path(configured)
    util.write_file(local_path, "")

    assert _instance._get_playbook("create") == local_path


def test_get_playbook_missing_local_path_keeps_existing_required_behavior(  # noqa: D103
    _instance: ansible_playbooks.AnsiblePlaybooks,  # noqa: PT019
) -> None:
    assert _instance._config.provisioner
    configured = "missing-converge.yml"
    _instance._config.config_data["ansible"]["playbooks"]["converge"] = configured

    assert _instance._get_playbook("converge") == _instance._config.provisioner.abs_path(
        configured,
    )


def test_get_playbook_missing_local_path_uses_driver_fallback(  # noqa: D103
    _instance: ansible_playbooks.AnsiblePlaybooks,  # noqa: PT019
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    assert _instance._config.provisioner
    _instance._config.config_data["ansible"]["playbooks"]["create"] = "missing-create.yml"
    bundled_playbook = tmp_path / "create.yml"
    bundled_playbook.write_text("---\n", encoding="utf-8")
    monkeypatch.setattr(
        _instance,
        "_get_bundled_driver_playbook",
        lambda _: str(bundled_playbook),
    )

    assert _instance._get_playbook("create") == str(bundled_playbook)


@pytest.mark.skip(reason="create not running for delegated")
def test_get_playbook_returns_bundled_driver_playbook_when_local_not_found(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    tmpdir,
    _instance,  # noqa: PT019
):
    x = os.path.join(_instance._get_playbook_directory(), "default", "create.yml")  # noqa: PTH118

    assert x == _instance._get_playbook("create")


@pytest.fixture
def _provisioner_driver_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {
        "provisioner": {
            "name": "ansible",
            "playbooks": {
                "create": "create.yml",
            },
        },
    }


@pytest.fixture
def _provisioner_driver_playbook_key_missing_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {
        "provisioner": {
            "name": "ansible",
            "playbooks": {
                "side_effect": "side_effect.yml",
            },
        },
    }


@pytest.mark.parametrize(
    "config_instance",
    ["_provisioner_driver_playbook_key_missing_section_data"],  # noqa: PT007
    indirect=True,
)
def test_get_ansible_playbook_with_driver_key_when_playbook_key_missing(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    tmpdir,
    _instance,  # noqa: PT019
):
    x = os.path.join(_instance._config.scenario.directory, "side_effect.yml")  # noqa: PTH118
    util.write_file(x, "")

    assert x == _instance._get_playbook("side_effect")


def test_get_bundled_driver_playbook(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    result = _instance._get_bundled_driver_playbook("create")
    parts = os_split(result)
    x = ("molecule", "driver", "playbooks", "create.yml")

    assert x == parts[-4:]

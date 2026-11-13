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

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from molecule import util
from molecule.config import Config
from molecule.constants import DEFAULT_CONFIG
from molecule.provisioner import ansible_playbooks
from tests.unit.conftest import os_split  # pylint:disable=C0411


if TYPE_CHECKING:
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


@pytest.mark.parametrize(
    "action",
    ("cleanup", "create", "converge", "destroy", "prepare", "side_effect", "verify"),
)
def test_default_playbook_discovery(
    config_instance: Config,
    action: ansible_playbooks.Section,
) -> None:
    """Discover YAML defaults for every playbook action.

    Args:
        config_instance: An isolated scenario configuration.
        action: Playbook action to look up.
    """
    directory = Path(config_instance.scenario.directory)
    playbook = directory / f"{action}.yaml"
    playbook.touch()
    assert ansible_playbooks.AnsiblePlaybooks(config_instance)._get_playbook(action) == str(
        playbook
    )


@pytest.mark.parametrize(
    ("action", "extensions", "expected"),
    (
        pytest.param("converge", ("yaml", "yml"), "converge.yml", id="prefer-yml"),
        pytest.param("converge", (), "converge.yml", id="missing-required"),
        pytest.param("prepare", (), None, id="missing-optional"),
    ),
)
def test_default_playbook_preference_and_missing(
    config_instance: Config,
    action: ansible_playbooks.Section,
    extensions: tuple[str, ...],
    expected: str | None,
) -> None:
    """Preserve suffix preference and required versus optional missing behavior.

    Args:
        config_instance: An isolated scenario configuration.
        action: Playbook action to look up.
        extensions: Playbook files to create.
        expected: Selected filename, or no playbook for an optional action.
    """
    directory = Path(config_instance.scenario.directory)
    for extension in extensions:
        (directory / f"{action}.{extension}").touch()
    result = ansible_playbooks.AnsiblePlaybooks(config_instance)._get_playbook(action)
    assert result == (str(directory / expected) if expected else None)


@pytest.mark.parametrize(
    ("filename", "extensions"),
    (
        pytest.param("converge.yml", ("yaml",), id="explicit-default-no-yaml-sibling"),
        pytest.param("converge.yaml", ("yml",), id="explicit-yaml-no-yml-sibling"),
        pytest.param("custom.yaml", ("yml",), id="custom-path-no-substitution"),
        pytest.param("converge.yml", ("yaml", "yml"), id="exact-yml"),
        pytest.param("converge.yaml", ("yaml", "yml"), id="exact-yaml"),
        pytest.param("custom.yaml", ("yaml",), id="exact-custom"),
        pytest.param("playbook.yaml", ("yml",), id="deprecated-name-is-exact"),
        pytest.param(None, ("yaml", "yml"), id="disabled"),
    ),
)
def test_configured_playbook_resolution(
    config_instance: Config,
    filename: str | None,
    extensions: tuple[str, ...],
) -> None:
    """Configured paths never discover a YAML sibling; null stays disabled.

    Args:
        config_instance: An isolated scenario configuration.
        filename: Configured playbook path.
        extensions: Existing playbook extensions.
    """
    source = Path(config_instance.molecule_file)
    source.write_text(util.safe_dump({"ansible": {"playbooks": {"converge": filename}}}))
    stem = Path(filename).stem if filename else "converge"
    for extension in extensions:
        (source.parent / f"{stem}.{extension}").touch()
    loaded = Config(str(source))
    result = ansible_playbooks.AnsiblePlaybooks(loaded).converge
    if filename is None:
        assert result is None
    else:
        assert result == str(source.parent / filename)


def test_yaml_default_prefers_existing_candidate(
    config_instance: Config,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A YAML default prefers its own suffix and discovers YML only if missing.

    Args:
        config_instance: An isolated scenario configuration.
        monkeypatch: Default configuration patcher.
    """
    monkeypatch.setitem(DEFAULT_CONFIG["ansible"]["playbooks"], "converge", "converge.yaml")
    loaded = Config(config_instance.molecule_file)
    directory = Path(loaded.scenario.directory)
    yml = directory / "converge.yml"
    yaml = directory / "converge.yaml"
    yml.touch()
    yaml.touch()
    playbooks = ansible_playbooks.AnsiblePlaybooks(loaded)
    assert playbooks.converge == str(yaml)
    yaml.unlink()
    assert playbooks.converge == str(yml)


def test_driver_returned_playbook_is_exact(
    config_instance: Config,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Do not re-resolve a filename already selected by the driver.

    Args:
        config_instance: An isolated scenario configuration.
        monkeypatch: Driver patcher.
    """
    requested = Path(config_instance.scenario.directory) / "driver.yml"
    requested.with_suffix(".yaml").touch()
    monkeypatch.setattr(config_instance.driver, "get_playbook", lambda _step: str(requested))
    playbooks = ansible_playbooks.AnsiblePlaybooks(config_instance)
    assert playbooks._get_bundled_driver_playbook("converge") == str(requested)


def test_missing_explicit_playbook_uses_driver_yaml_fallback(
    config_instance: Config,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Preserve independent driver fallback after an explicit scenario path is missing.

    Args:
        config_instance: An isolated scenario configuration.
        monkeypatch: Driver package directory patcher.
    """
    source = Path(config_instance.molecule_file)
    source.write_text("ansible:\n  playbooks:\n    create: create.yml\n")
    source.with_name("create.yaml").touch()
    loaded = Config(str(source))
    directory = source.parent / "driver" / "playbooks"
    directory.mkdir(parents=True)
    bundled = directory / "create.yaml"
    bundled.touch()
    monkeypatch.setattr(loaded.driver, "_path", str(directory.parent))
    assert ansible_playbooks.AnsiblePlaybooks(loaded).create == str(bundled)


@pytest.mark.parametrize("extension", ("yml", "yaml"))
@pytest.mark.parametrize("filename", (None, "converge.yml", "converge.yaml"))
def test_deprecated_playbook_yaml_fallback(
    config_instance: Config,
    extension: str,
    filename: str | None,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Only discover deprecated basenames after both modern default names.

    Args:
        config_instance: An isolated scenario configuration.
        extension: Deprecated playbook extension.
        filename: Optional configured converge filename.
        caplog: Log capture fixture.
    """
    directory = Path(config_instance.scenario.directory)
    if filename:
        Path(config_instance.molecule_file).write_text(
            util.safe_dump({"ansible": {"playbooks": {"converge": filename}}}),
        )
    loaded = Config(config_instance.molecule_file)
    deprecated = directory / f"playbook.{extension}"
    deprecated.touch()
    playbooks = ansible_playbooks.AnsiblePlaybooks(loaded)
    expected = deprecated if extension == "yml" else directory / (filename or "converge.yml")
    assert playbooks.converge == str(expected)
    assert ("was deprecated" in caplog.text) == (extension == "yml")
    caplog.clear()
    modern = directory / (filename or "converge.yaml")
    modern.touch()
    assert playbooks.converge == str(modern)
    assert "was deprecated" not in caplog.text


@pytest.mark.parametrize("filename", (None, "converge.yml", "converge.yaml"))
@pytest.mark.parametrize("location", ("provisioner", "driver"))
def test_bundled_playbook_extension_lookup(
    config_instance: Config,
    monkeypatch: pytest.MonkeyPatch,
    filename: str | None,
    location: str,
) -> None:
    """Search each bundled location in order, preserving the supplied filename first.

    Args:
        config_instance: An isolated scenario configuration.
        monkeypatch: Fixture for isolating driver lookup.
        filename: Configured playbook filename.
        location: Bundled lookup location to exercise.
    """
    source = Path(config_instance.molecule_file)
    if filename:
        source.write_text(util.safe_dump({"ansible": {"playbooks": {"converge": filename}}}))
    loaded = Config(str(source))
    monkeypatch.setattr(loaded.driver, "get_playbook", lambda _step: None)
    playbooks = ansible_playbooks.AnsiblePlaybooks(loaded)
    bundled_root = source.parent / "bundled"
    monkeypatch.setattr(playbooks, "_get_playbook_directory", lambda: bundled_root)
    monkeypatch.setattr(loaded.driver, "_path", str(source.parent / "driver"))
    directory = (
        bundled_root / loaded.driver.name
        if location == "provisioner"
        else Path(loaded.driver._path) / "playbooks"
    )
    directory.mkdir(parents=True)
    requested = filename or "converge.yml"
    alternative_name = "converge.yaml" if requested.endswith(".yml") else "converge.yml"
    alternative = directory / alternative_name
    alternative.touch()
    expected = source.parent / requested if filename else alternative
    assert playbooks.converge == str(expected)
    preferred = directory / requested
    preferred.touch()
    assert playbooks.converge == str(preferred)
    local = source.parent / alternative_name
    local.touch()
    assert playbooks.converge == str(preferred if filename else local)

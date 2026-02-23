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
"""Tests for nested scenario support in collection mode."""

from __future__ import annotations

from pathlib import Path

import pytest

from molecule import config
from molecule.command import base
from molecule.constants import MOLECULE_COLLECTION_GLOB
from molecule.exceptions import ScenarioFailureError
from molecule.scenario import Scenario
from molecule.scenarios import Scenarios


# --- _resolve_scenario_glob (targeting) ---


@pytest.mark.parametrize(
    ("glob_pattern", "scenario_name", "expected"),
    (
        pytest.param(
            "extensions/molecule/*/molecule.yml",
            "default",
            "extensions/molecule/default/molecule.yml",
            id="collection_flat_default",
        ),
        pytest.param(
            "extensions/molecule/*/molecule.yml",
            "appliance_vlans_merged",
            "extensions/molecule/appliance_vlans_merged/molecule.yml",
            id="collection_flat_hyphenated",
        ),
        pytest.param(
            "extensions/molecule/*/molecule.yml",
            "appliance_vlans/merged",
            "extensions/molecule/appliance_vlans/merged/molecule.yml",
            id="collection_nested_one_level",
        ),
        pytest.param(
            "extensions/molecule/*/molecule.yml",
            "appliance_vlans/merged/fast",
            "extensions/molecule/appliance_vlans/merged/fast/molecule.yml",
            id="collection_nested_two_levels",
        ),
        pytest.param(
            "extensions/molecule/**/molecule.yml",
            "appliance_vlans/merged",
            "extensions/molecule/appliance_vlans/merged/molecule.yml",
            id="collection_recursive_glob_nested",
        ),
        pytest.param(
            "extensions/molecule/*/molecule.yml",
            "appliance_vlans/*",
            "extensions/molecule/appliance_vlans/*/molecule.yml",
            id="collection_wildcard_nonrecursive_glob",
        ),
        pytest.param(
            "extensions/molecule/**/molecule.yml",
            "camera_*",
            "extensions/molecule/camera_*/**/molecule.yml",
            id="collection_wildcard_recursive_glob",
        ),
        pytest.param(
            "extensions/molecule/**/molecule.yml",
            "appliance_vlans/*",
            "extensions/molecule/appliance_vlans/*/**/molecule.yml",
            id="collection_wildcard_nested_recursive_glob",
        ),
        pytest.param(
            "molecule/*/molecule.yml",
            "default",
            "molecule/default/molecule.yml",
            id="role_mode_flat",
        ),
        pytest.param(
            "molecule/*/molecule.yml",
            "appliance_vlans/merged",
            "molecule/appliance_vlans/merged/molecule.yml",
            id="role_mode_slash_uses_str_replace",
        ),
    ),
)
def test_resolve_scenario_glob(
    glob_pattern: str,
    scenario_name: str,
    expected: str,
) -> None:
    """Verify glob resolution for flat and nested scenario names.

    Args:
        glob_pattern: The base glob pattern to resolve against.
        scenario_name: The scenario name from -s flag.
        expected: The expected resolved glob string.
    """
    result = base._resolve_scenario_glob(glob_pattern, scenario_name)
    assert result == expected


def test_resolve_scenario_glob_collection_gate() -> None:
    """Path construction always used in collection mode, str.replace in role mode."""
    role_glob = "molecule/*/molecule.yml"
    result = base._resolve_scenario_glob(role_glob, "a/b")
    assert result == role_glob.replace("*", "a/b")

    collection_glob = "extensions/molecule/*/molecule.yml"
    result = base._resolve_scenario_glob(collection_glob, "a/b")
    assert result == "extensions/molecule/a/b/molecule.yml"


# --- _derive_scenario_name (naming) ---


def _make_molecule_file(root: Path, *parts: str) -> str:
    """Create a molecule.yml and return its absolute path.

    Args:
        root: The root directory to create the file under.
        *parts: Path components between root and molecule.yml.

    Returns:
        The absolute path to the created molecule.yml file.
    """
    d = root.joinpath(*parts)
    d.mkdir(parents=True, exist_ok=True)
    f = d / "molecule.yml"
    f.write_text("---\n")
    return str(f)


@pytest.mark.parametrize(
    ("path_parts", "expected_name"),
    (
        pytest.param(
            ("extensions", "molecule", "default"),
            "default",
            id="collection_flat_default",
        ),
        pytest.param(
            ("extensions", "molecule", "merged"),
            "merged",
            id="collection_flat_single",
        ),
        pytest.param(
            ("extensions", "molecule", "appliance_vlans", "merged"),
            "appliance_vlans/merged",
            id="collection_nested_one_level",
        ),
        pytest.param(
            ("extensions", "molecule", "appliance_vlans", "merged", "fast"),
            "appliance_vlans/merged/fast",
            id="collection_nested_two_levels",
        ),
        pytest.param(
            ("molecule", "default"),
            "default",
            id="role_mode_flat",
        ),
        pytest.param(
            ("molecule", "my_scenario"),
            "my_scenario",
            id="role_mode_named",
        ),
    ),
)
def test_derive_scenario_name(
    tmp_path: Path,
    path_parts: tuple[str, ...],
    expected_name: str,
) -> None:
    """Verify scenario name derivation from molecule file path.

    Args:
        tmp_path: Pytest temporary directory fixture.
        path_parts: Directory components for the molecule file path.
        expected_name: The expected derived scenario name.
    """
    molecule_file = _make_molecule_file(tmp_path, *path_parts)
    cfg = config.Config.__new__(config.Config)
    cfg.molecule_file = molecule_file
    assert cfg._derive_scenario_name() == expected_name


def test_derive_scenario_name_role_mode_ignores_nesting(tmp_path: Path) -> None:
    """In role mode (no extensions/molecule/ in path), always returns basename.

    Args:
        tmp_path: Pytest temporary directory fixture.
    """
    molecule_file = _make_molecule_file(tmp_path, "molecule", "group", "nested")
    cfg = config.Config.__new__(config.Config)
    cfg.molecule_file = molecule_file
    assert cfg._derive_scenario_name() == "nested"


# --- Integration: end-to-end nested targeting with get_configs ---


@pytest.fixture(name="collection_project")
def fixture_collection_project(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Path:
    """Set up a collection project with flat and nested scenarios.

    Args:
        tmp_path: Pytest temporary directory fixture.
        monkeypatch: Pytest monkeypatch fixture.

    Returns:
        The path to the collection project root.
    """
    project = tmp_path / "my_collection"
    project.mkdir()

    galaxy = project / "galaxy.yml"
    galaxy.write_text("namespace: acme\nname: widgets\nversion: '1.0.0'\n")

    mol_root = project / "extensions" / "molecule"

    default_dir = mol_root / "default"
    default_dir.mkdir(parents=True)
    (default_dir / "molecule.yml").write_text("---\n")

    nested_dir = mol_root / "appliance_vlans" / "merged"
    nested_dir.mkdir(parents=True)
    (nested_dir / "molecule.yml").write_text("---\n")

    nested_dir2 = mol_root / "appliance_vlans" / "replaced"
    nested_dir2.mkdir(parents=True)
    (nested_dir2 / "molecule.yml").write_text("---\n")

    monkeypatch.chdir(project)
    monkeypatch.setattr(
        "molecule.command.base.filter_ignored_scenarios",
        lambda paths: paths,
    )

    return project


def test_get_configs_nested_scenario(collection_project: Path) -> None:
    """Verify get_configs finds a nested scenario via slash-aware glob resolution.

    Args:
        collection_project: The collection project fixture (used for side effects).
    """
    glob_str = base._resolve_scenario_glob(
        MOLECULE_COLLECTION_GLOB,
        "appliance_vlans/merged",
    )
    configs = base.get_configs({}, {"subcommand": "test"}, glob_str=glob_str)
    assert len(configs) == 1
    assert configs[0].scenario.name == "appliance_vlans/merged"


def test_get_configs_flat_scenario(collection_project: Path) -> None:
    """Verify get_configs still finds flat scenarios.

    Args:
        collection_project: The collection project fixture (used for side effects).
    """
    glob_str = base._resolve_scenario_glob(MOLECULE_COLLECTION_GLOB, "default")
    configs = base.get_configs({}, {"subcommand": "test"}, glob_str=glob_str)
    assert len(configs) == 1
    assert configs[0].scenario.name == "default"


def test_get_configs_all_discovers_nested_with_recursive_glob(
    collection_project: Path,
) -> None:
    """Verify recursive glob discovers both flat and nested scenarios.

    Args:
        collection_project: The collection project fixture (used for side effects).
    """
    configs = base.get_configs(
        {},
        {"subcommand": "test"},
        glob_str="extensions/molecule/**/molecule.yml",
    )
    names = sorted(c.scenario.name for c in configs)
    assert names == ["appliance_vlans/merged", "appliance_vlans/replaced", "default"]


def test_resolve_scenario_glob_wildcard_preserved(
    collection_project: Path,
) -> None:
    """Verify wildcard in scenario name produces a glob that discovers multiple scenarios.

    Args:
        collection_project: The collection project fixture (used for side effects).
    """
    glob_str = base._resolve_scenario_glob(
        MOLECULE_COLLECTION_GLOB,
        "appliance_vlans/*",
    )
    assert glob_str == "extensions/molecule/appliance_vlans/*/molecule.yml"
    configs = base.get_configs({}, {"subcommand": "test"}, glob_str=glob_str)
    names = sorted(c.scenario.name for c in configs)
    assert names == ["appliance_vlans/merged", "appliance_vlans/replaced"]


def test_wildcard_scenario_names_expanded_for_scenarios_verify(
    collection_project: Path,
) -> None:
    """Verify Scenarios._verify passes when scenario_names are expanded from wildcard results.

    After get_configs expands a wildcard like 'appliance_vlans/*' into multiple
    configs, scenario_names must be replaced with the actual discovered names
    so Scenarios(..., scenario_names) does not fail verification.

    Args:
        collection_project: The collection project fixture (used for side effects).
    """
    glob_str = base._resolve_scenario_glob(
        MOLECULE_COLLECTION_GLOB,
        "appliance_vlans/*",
    )
    configs = base.get_configs({}, {"subcommand": "test"}, glob_str=glob_str)

    expanded_names = [c.scenario.name for c in configs]
    scenarios = Scenarios(configs, expanded_names)
    scenario_names = sorted(s.name for s in scenarios.all)
    assert scenario_names == ["appliance_vlans/merged", "appliance_vlans/replaced"]


def test_scenario_name_roundtrip(collection_project: Path) -> None:
    """Verify name from discovery matches what -s needs for targeting.

    Args:
        collection_project: The collection project fixture (used for side effects).
    """
    glob_str = base._resolve_scenario_glob(
        MOLECULE_COLLECTION_GLOB,
        "appliance_vlans/merged",
    )
    configs = base.get_configs({}, {"subcommand": "test"}, glob_str=glob_str)
    discovered_name = configs[0].scenario.name

    roundtrip_glob = base._resolve_scenario_glob(MOLECULE_COLLECTION_GLOB, discovered_name)
    roundtrip_configs = base.get_configs({}, {"subcommand": "test"}, glob_str=roundtrip_glob)
    assert len(roundtrip_configs) == 1
    assert roundtrip_configs[0].scenario.name == discovered_name


# --- Edge cases and validation ---


@pytest.mark.parametrize(
    "scenario_name",
    (
        pytest.param("../etc/passwd", id="path_traversal_parent"),
        pytest.param("appliance_vlans/../merged", id="path_traversal_middle"),
        pytest.param("..", id="path_traversal_dotdot"),
        pytest.param("/absolute/path", id="absolute_path"),
    ),
)
def test_resolve_scenario_glob_rejects_path_traversal(scenario_name: str) -> None:
    """Verify path traversal sequences in scenario names are rejected.

    Args:
        scenario_name: A scenario name containing path traversal.
    """
    with pytest.raises(ScenarioFailureError) as exc_info:
        base._resolve_scenario_glob(MOLECULE_COLLECTION_GLOB, scenario_name)
    assert "path traversal" in exc_info.value.message


@pytest.mark.parametrize(
    "scenario_name",
    (
        pytest.param("appliance_vlans/nonexistent", id="nonexistent_nested"),
        pytest.param("a/b/c/d/e/f/g", id="deeply_nested"),
    ),
)
def test_get_configs_nonexistent_scenarios(
    collection_project: Path,
    scenario_name: str,
) -> None:
    """Verify nonexistent or deeply nested scenarios raise ScenarioFailureError.

    Args:
        collection_project: The collection project fixture (used for side effects).
        scenario_name: A scenario name that does not exist in the project.
    """
    glob_str = base._resolve_scenario_glob(MOLECULE_COLLECTION_GLOB, scenario_name)
    with pytest.raises(ScenarioFailureError) as exc_info:
        base.get_configs({}, {"subcommand": "test"}, glob_str=glob_str)
    assert "glob failed" in exc_info.value.message


def test_ephemeral_directory_safe_with_nested_name(
    collection_project: Path,
) -> None:
    """Verify the Scenario ephemeral directory is a flat path for nested scenario names.

    When a scenario name contains '/', the ephemeral directory must not create
    nested subdirectories. The '/' is replaced with '--' to keep it as a single
    path component.

    Args:
        collection_project: The collection project fixture (used for side effects).
    """
    glob_str = base._resolve_scenario_glob(
        MOLECULE_COLLECTION_GLOB,
        "appliance_vlans/merged",
    )
    configs = base.get_configs({}, {"subcommand": "test"}, glob_str=glob_str)
    assert len(configs) == 1

    scenario = Scenario(configs[0])
    assert scenario.name == "appliance_vlans/merged"

    eph_dir = scenario.ephemeral_directory
    eph_name = Path(eph_dir).name
    assert "/" not in eph_name
    assert "appliance_vlans--merged" in eph_name

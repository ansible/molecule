"""Tests for nested scenario support in collection mode."""

from __future__ import annotations

import os

from pathlib import Path

import pytest

from molecule import config
from molecule.command import base
from molecule.constants import MOLECULE_COLLECTION_GLOB


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
            os.path.join("extensions/molecule/", "appliance_vlans/merged", "molecule.yml"),
            id="collection_nested_one_level",
        ),
        pytest.param(
            "extensions/molecule/*/molecule.yml",
            "appliance_vlans/merged/fast",
            os.path.join("extensions/molecule/", "appliance_vlans/merged/fast", "molecule.yml"),
            id="collection_nested_two_levels",
        ),
        pytest.param(
            "extensions/molecule/**/molecule.yml",
            "appliance_vlans/merged",
            os.path.join("extensions/molecule/", "appliance_vlans/merged", "molecule.yml"),
            id="collection_recursive_glob_nested",
        ),
        pytest.param(
            "extensions/molecule/*/molecule.yml",
            "appliance_vlans/*",
            os.path.join("extensions/molecule/", "appliance_vlans/*", "molecule.yml"),
            id="collection_wildcard_in_scenario_name",
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
    """Verify glob resolution for flat and nested scenario names."""
    result = base._resolve_scenario_glob(glob_pattern, scenario_name)
    assert result == expected


def test_resolve_scenario_glob_collection_gate() -> None:
    """Slash in scenario name only triggers path construction in collection mode."""
    role_glob = "molecule/*/molecule.yml"
    result = base._resolve_scenario_glob(role_glob, "a/b")
    assert result == role_glob.replace("*", "a/b")

    collection_glob = "extensions/molecule/*/molecule.yml"
    result = base._resolve_scenario_glob(collection_glob, "a/b")
    assert result == os.path.join("extensions/molecule/", "a/b", "molecule.yml")


# --- _derive_scenario_name (naming) ---


@pytest.fixture
def _collection_tree(tmp_path: Path) -> Path:
    """Create a minimal collection directory tree and chdir into it."""
    return tmp_path


def _make_molecule_file(root: Path, *parts: str) -> str:
    """Create a molecule.yml at root/parts.../molecule.yml and return its absolute path."""
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
    """Verify scenario name derivation from molecule file path."""
    molecule_file = _make_molecule_file(tmp_path, *path_parts)
    cfg = config.Config.__new__(config.Config)
    cfg.molecule_file = molecule_file
    assert cfg._derive_scenario_name() == expected_name


def test_derive_scenario_name_role_mode_ignores_nesting(tmp_path: Path) -> None:
    """In role mode (no extensions/molecule/ in path), always returns basename."""
    molecule_file = _make_molecule_file(tmp_path, "molecule", "group", "nested")
    cfg = config.Config.__new__(config.Config)
    cfg.molecule_file = molecule_file
    assert cfg._derive_scenario_name() == "nested"


# --- Integration: end-to-end nested targeting with get_configs ---


@pytest.fixture
def collection_project(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Path:
    """Set up a collection project with flat and nested scenarios."""
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
    """get_configs finds a nested scenario via slash-aware glob resolution."""
    glob_str = base._resolve_scenario_glob(
        MOLECULE_COLLECTION_GLOB,
        "appliance_vlans/merged",
    )
    configs = base.get_configs({}, {"subcommand": "test"}, glob_str=glob_str)
    assert len(configs) == 1
    assert configs[0].scenario.name == "appliance_vlans/merged"


def test_get_configs_flat_scenario(collection_project: Path) -> None:
    """get_configs still finds flat scenarios using existing behavior."""
    glob_str = base._resolve_scenario_glob(MOLECULE_COLLECTION_GLOB, "default")
    configs = base.get_configs({}, {"subcommand": "test"}, glob_str=glob_str)
    assert len(configs) == 1
    assert configs[0].scenario.name == "default"


def test_get_configs_all_discovers_nested_with_recursive_glob(
    collection_project: Path,
) -> None:
    """Recursive glob discovers both flat and nested scenarios."""
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
    """Wildcard in scenario name produces a glob that discovers multiple scenarios."""
    glob_str = base._resolve_scenario_glob(
        MOLECULE_COLLECTION_GLOB,
        "appliance_vlans/*",
    )
    assert glob_str == os.path.join(
        "extensions/molecule/",
        "appliance_vlans/*",
        "molecule.yml",
    )
    configs = base.get_configs({}, {"subcommand": "test"}, glob_str=glob_str)
    names = sorted(c.scenario.name for c in configs)
    assert names == ["appliance_vlans/merged", "appliance_vlans/replaced"]


def test_wildcard_scenario_names_expanded_for_scenarios_verify(
    collection_project: Path,
) -> None:
    """Scenarios._verify passes when scenario_names are expanded from wildcard results.

    This covers the scenario_names replacement in execute_cmdline_scenarios:
    after get_configs expands a wildcard like 'appliance_vlans/*' into multiple
    configs, scenario_names must be replaced with the actual discovered names
    so Scenarios(..., scenario_names) does not fail verification.
    """
    from molecule.scenarios import Scenarios

    glob_str = base._resolve_scenario_glob(
        MOLECULE_COLLECTION_GLOB,
        "appliance_vlans/*",
    )
    configs = base.get_configs({}, {"subcommand": "test"}, glob_str=glob_str)

    expanded_names = [c.scenario.name for c in configs]
    scenarios = Scenarios(configs, expanded_names)
    assert len(scenarios.all) == 2
    assert sorted(s.name for s in scenarios.all) == [
        "appliance_vlans/merged",
        "appliance_vlans/replaced",
    ]


def test_scenario_name_roundtrip(collection_project: Path) -> None:
    """Name from discovery matches what -s needs for targeting."""
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

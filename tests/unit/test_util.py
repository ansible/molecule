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

import binascii
import os
import tempfile

from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
import yaml

from molecule import util
from molecule.console import console
from molecule.constants import MOLECULE_COLLECTION_GLOB, MOLECULE_HEADER
from molecule.exceptions import MoleculeError
from molecule.text import strip_ansi_escape


if TYPE_CHECKING:
    from collections.abc import MutableMapping
    from typing import Any
    from unittest.mock import Mock

    from pytest_mock import MockerFixture

    from molecule.app import App
    from molecule.types import Options


def test_print_debug() -> None:  # noqa: D103
    expected = "DEBUG: test_title:\ntest_data\n"
    with console.capture() as capture:
        util.print_debug("test_title", "test_data")

    result = strip_ansi_escape(capture.get())
    assert result == expected


def test_print_environment_vars(  # noqa: D103
    capsys: pytest.CaptureFixture[str],
) -> None:
    env = {
        "ANSIBLE_FOO": "foo",
        "ANSIBLE_BAR": "bar",
        "ANSIBLE": "",
        "MOLECULE_FOO": "foo",
        "MOLECULE_BAR": "bar",
        "MOLECULE": "",
    }
    expected = """DEBUG: ANSIBLE ENVIRONMENT:
ANSIBLE_BAR: bar
ANSIBLE_FOO: foo

DEBUG: MOLECULE ENVIRONMENT:
MOLECULE_BAR: bar
MOLECULE_FOO: foo

DEBUG: SHELL REPLAY:
ANSIBLE_BAR=bar ANSIBLE_FOO=foo MOLECULE_BAR=bar MOLECULE_FOO=foo
"""

    with console.capture() as capture:
        util.print_environment_vars(env)
    result = strip_ansi_escape(capture.get())
    assert result == expected


def test_sysexit() -> None:  # noqa: D103
    with pytest.raises(SystemExit) as e:
        util.sysexit()

    assert e.value.code == 1


def test_sysexit_with_custom_code() -> None:  # noqa: D103
    with pytest.raises(SystemExit) as e:
        util.sysexit(2)

    assert e.value.code == 2  # noqa: PLR2004


def test_run_command(app: App) -> None:  # noqa: D103
    cmd = ["ls"]
    x = app.run_command(cmd)

    assert x.returncode == 0


def test_run_command_with_debug(  # noqa: D103
    mocker: MockerFixture,
    patched_print_debug: Mock,
    app: App,
) -> None:
    env = {"ANSIBLE_FOO": "foo", "MOLECULE_BAR": "bar"}
    app.run_command(["ls"], debug=True, env=env)
    x = [
        mocker.call("ANSIBLE ENVIRONMENT", "ANSIBLE_FOO: foo\n"),
        mocker.call("MOLECULE ENVIRONMENT", "MOLECULE_BAR: bar\n"),
        mocker.call("SHELL REPLAY", "ANSIBLE_FOO=foo MOLECULE_BAR=bar"),
    ]

    assert x == patched_print_debug.mock_calls


def test_run_command_baked_cmd_env(app: App) -> None:  # noqa: D103
    cmd = ["printenv", "myvar"]
    result = app.run_command(cmd, env={"myvar": "value2"})
    assert result.returncode == 0

    cmd = ["printenv", "myvar2"]
    result = app.run_command(cmd, env={"myvar2": "value2"})
    assert result.returncode == 0

    # negative test
    cmd = ["printenv", "myvar"]
    result = app.run_command(cmd)
    assert result.returncode == 1


def test_run_command_with_debug_handles_no_env(  # noqa: D103
    mocker: MockerFixture,
    patched_print_debug: Mock,
    app: App,
) -> None:
    cmd = ["ls"]
    app.run_command(cmd, debug=True)
    # when env is empty we expect not to print anything
    empty_list: list[Any] = []

    assert empty_list == patched_print_debug.mock_calls


def test_os_walk(test_cache_path: Path) -> None:  # noqa: D103
    scenarios = ["scenario1", "scenario2", "scenario3"]
    mol_dir = test_cache_path / "molecule"
    for scenario in scenarios:
        scenario_directory = mol_dir / scenario
        molecule_file = scenario_directory / "molecule.yml"
        os.makedirs(scenario_directory, exist_ok=True)  # noqa: PTH103
        util.write_file(str(molecule_file), "")

    result = list(util.os_walk(mol_dir, "molecule.yml"))
    assert len(result) == 3  # noqa: PLR2004


def test_render_template() -> None:  # noqa: D103
    template = "{{ foo }} = {{ bar }}"

    assert util.render_template(template, foo="foo", bar="bar") == "foo = bar"


def test_render_template_quoted() -> None:  # noqa: D103
    template = """
    {{ 'url = "quoted_str"' }}
    """.strip()

    assert util.render_template(template) == 'url = "quoted_str"'


def test_write_file(test_cache_path: Path) -> None:
    """Test the `write_file` function.

    Args:
        test_cache_path: The path to the test cache directory for the test.
    """
    dest_file = test_cache_path / "test_util_write_file.tmp"
    contents = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
    util.write_file(str(dest_file), contents)
    with dest_file.open() as stream:
        data = stream.read()
    x = f"# Molecule managed\n\n{contents}"
    assert x == data


def test_molecule_prepender(tmp_path: Path) -> None:  # noqa: D103
    fname = tmp_path / "some.txt"
    fname.write_text("foo bar")
    x = f"{MOLECULE_HEADER}\n\nfoo bar"
    util.file_prepender(str(fname))
    assert x == fname.read_text()


def test_safe_dump() -> None:  # noqa: D103
    x = """
---
foo: bar
""".lstrip()

    assert x == util.safe_dump({"foo": "bar"})


def test_safe_dump_with_increase_indent() -> None:  # noqa: D103
    data = {"foo": [{"foo": "bar", "baz": "zzyzx"}]}

    x = """
---
foo:
  - baz: zzyzx
    foo: bar
""".lstrip()
    assert x == util.safe_dump(data)


def test_safe_load() -> None:  # noqa: D103
    assert util.safe_load("foo: bar") == {"foo": "bar"}


def test_safe_load_returns_empty_dict_on_empty_string() -> None:  # noqa: D103
    assert util.safe_load("") == {}


def test_safe_load_exits_when_cannot_parse() -> None:  # noqa: D103
    data = """
---
%foo:
""".strip()

    with pytest.raises(MoleculeError) as e:
        util.safe_load(data)

    assert e.value.code == 1


def test_safe_load_file(test_cache_path: Path) -> None:
    """Test the `safe_load_file` function.

    Args:
        test_cache_path: The path to the test cache directory for the test.
    """
    path = test_cache_path / "test_safe_load_file.yml"
    util.write_file(str(path), "foo: bar")

    assert util.safe_load_file(str(path)) == {"foo": "bar"}


def test_instance_with_scenario_name() -> None:  # noqa: D103
    assert util.instance_with_scenario_name("foo", "bar") == "foo-bar"


def test_verbose_flag() -> None:  # noqa: D103
    options: Options = {"verbose": True, "v": True}

    assert util.verbose_flag(options) == ["-v"]
    # pylint: disable=use-implicit-booleaness-not-comparison
    assert options == {}


def test_verbose_flag_extra_verbose() -> None:  # noqa: D103
    options: Options = {"verbose": True, "vvv": True}

    assert util.verbose_flag(options) == ["-vvv"]
    # pylint: disable=use-implicit-booleaness-not-comparison
    assert options == {}


def test_verbose_flag_preserves_verbose_option() -> None:  # noqa: D103
    options: Options = {"verbose": True}

    # pylint: disable=use-implicit-booleaness-not-comparison
    assert util.verbose_flag(options) == []
    assert options == {"verbose": True}


def test_filter_verbose_permutation() -> None:  # noqa: D103
    options: Options = {
        "v": True,
        "vv": True,
        "vvv": True,
        "vfoo": True,
        "foo": True,
        "bar": True,
    }

    x = {"vfoo": True, "foo": True, "bar": True}
    assert x == util.filter_verbose_permutation(options)


def test_abs_path() -> None:
    """Test the `abs_path` function."""
    test_dir = "/foo/../foo"
    assert util.abs_path(test_dir) == "/foo"


def test_abs_path_with_path() -> None:
    """Test the `abs_path` function."""
    test_dir = Path("/foo/../foo")
    assert util.abs_path(test_dir) == Path("/foo")


def test_abs_path_with_empty_path() -> None:
    """Test the `abs_path` function with an empty path."""
    assert util.abs_path("") == ""


def test_abs_path_with_symlink() -> None:
    """Test the `abs_path` function not resolving symlinks."""
    with tempfile.NamedTemporaryFile() as tmp_file:
        tmpfile_path = Path(tmp_file.name)
        symlink_path = Path(tmp_file.name + "_sym")
        symlink_path.symlink_to(tmpfile_path)
        abs_path_result = util.abs_path(symlink_path)
        symlink_path.unlink()
    assert abs_path_result == symlink_path


@pytest.mark.parametrize(
    ("a", "b", "x"),
    (
        # Base of recursion scenarios
        ({"key": 1}, {"key": 2}, {"key": 2}),
        ({"key": {}}, {"key": 2}, {"key": 2}),
        ({"key": 1}, {"key": {}}, {"key": {}}),
        # Recursive scenario
        ({"a": {"x": 1}}, {"a": {"x": 2}}, {"a": {"x": 2}}),
        ({"a": {"x": 1}}, {"a": {"y": 2}}, {"a": {"x": 1, "y": 2}}),
        # example taken from python-anyconfig/anyconfig/__init__.py
        (
            {"b": [{"c": 0}, {"c": 2}], "d": {"e": "aaa", "f": 3}},
            {"a": 1, "b": [{"c": 3}], "d": {"e": "bbb"}},
            {"a": 1, "b": [{"c": 3}], "d": {"e": "bbb", "f": 3}},
        ),
    ),
)
def test_merge_dicts(a: MutableMapping, b: MutableMapping, x: MutableMapping) -> None:  # type: ignore[type-arg]  # noqa: D103
    assert x == util.merge_dicts(a, b)


@pytest.mark.parametrize(
    ("sequence", "output"),
    (
        ([], ""),
        (["item1"], "'item1'"),
        (["item1", False], "'item1' and 'False'"),
        (["item1", False, Path()], "'item1', 'False', and '.'"),
    ),
    ids=("empty", "one", "two", "three"),
)
def test_oxford_comma(sequence: list[str], output: str) -> None:
    """Test the oxford_comma function.

    Args:
        sequence: sequence of items.
        output: expected output string.
    """
    assert util.oxford_comma(sequence) == output


def test_get_collection_metadata_valid_collection(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Test get_collection_metadata with valid collection.

    Args:
        monkeypatch: pytest fixture for patching.
        tmp_path: pytest fixture for temporary directory.
    """
    # Create a valid galaxy.yml
    galaxy_content = {"name": "test_collection", "namespace": "test_namespace", "version": "1.0.0"}
    galaxy_file = tmp_path / "galaxy.yml"
    galaxy_file.write_text(yaml.dump(galaxy_content))

    # Change to the collection directory
    monkeypatch.chdir(tmp_path)

    # Clear cache to ensure fresh detection
    util.get_collection_metadata.cache_clear()

    collection_dir, collection_data = util.get_collection_metadata()

    assert collection_dir == tmp_path
    assert collection_data is not None
    assert collection_data["name"] == "test_collection"
    assert collection_data["namespace"] == "test_namespace"


def test_get_collection_metadata_missing_galaxy_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test get_collection_metadata with missing galaxy.yml.

    Args:
        monkeypatch: pytest fixture for patching.
        tmp_path: pytest fixture for temporary directory.
        caplog: pytest fixture for log capture.
    """
    # Change to directory without galaxy.yml
    monkeypatch.chdir(tmp_path)

    # Clear cache to ensure fresh detection
    util.get_collection_metadata.cache_clear()

    collection_dir, collection_data = util.get_collection_metadata()

    assert collection_dir is None
    assert collection_data is None
    assert "No galaxy.yml found" in caplog.text


def test_get_collection_metadata_missing_required_fields(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test get_collection_metadata with galaxy.yml missing required fields.

    Args:
        monkeypatch: pytest fixture for patching.
        tmp_path: pytest fixture for temporary directory.
        caplog: pytest fixture for log capture.
    """
    # Create galaxy.yml missing namespace
    galaxy_content = {"name": "test_collection", "version": "1.0.0"}
    galaxy_file = tmp_path / "galaxy.yml"
    galaxy_file.write_text(yaml.dump(galaxy_content))

    # Change to the collection directory
    monkeypatch.chdir(tmp_path)

    # Clear cache to ensure fresh detection
    util.get_collection_metadata.cache_clear()

    collection_dir, collection_data = util.get_collection_metadata()

    assert collection_dir is None
    assert collection_data is None
    assert "is missing required fields: 'namespace'" in caplog.text


def test_get_collection_metadata_invalid_yaml(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test get_collection_metadata with invalid YAML.

    Args:
        monkeypatch: pytest fixture for patching.
        tmp_path: pytest fixture for temporary directory.
        caplog: pytest fixture for log capture.
    """
    # Create invalid galaxy.yml
    galaxy_file = tmp_path / "galaxy.yml"
    galaxy_file.write_text("invalid: yaml: content: [")

    # Change to the collection directory
    monkeypatch.chdir(tmp_path)

    # Clear cache to ensure fresh detection
    util.get_collection_metadata.cache_clear()

    collection_dir, collection_data = util.get_collection_metadata()

    assert collection_dir is None
    assert collection_data is None
    assert "Failed to load galaxy.yml" in caplog.text


def test_get_collection_metadata_invalid_format(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test get_collection_metadata with non-dict galaxy.yml.

    Args:
        monkeypatch: pytest fixture for patching.
        tmp_path: pytest fixture for temporary directory.
        caplog: pytest fixture for log capture.
    """
    # Create galaxy.yml with non-dict content
    galaxy_file = tmp_path / "galaxy.yml"
    galaxy_file.write_text("- item1\n- item2")

    # Change to the collection directory
    monkeypatch.chdir(tmp_path)

    # Clear cache to ensure fresh detection
    util.get_collection_metadata.cache_clear()

    collection_dir, collection_data = util.get_collection_metadata()

    assert collection_dir is None
    assert collection_data is None
    assert "Invalid galaxy.yml format" in caplog.text


def test_get_effective_molecule_glob_collection_without_molecule_dir(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test get_effective_molecule_glob with collection but no molecule directories.

    Args:
        monkeypatch: pytest fixture for patching.
        tmp_path: pytest fixture for temporary directory.
        caplog: pytest fixture for log capture.
    """
    # Create valid collection but no extensions/molecule directory
    galaxy_content = {"name": "test_collection", "namespace": "test_namespace"}
    galaxy_file = tmp_path / "galaxy.yml"
    galaxy_file.write_text(yaml.dump(galaxy_content))

    # Change to collection directory
    monkeypatch.chdir(tmp_path)

    # Clear caches
    util.get_collection_metadata.cache_clear()
    util.get_effective_molecule_glob.cache_clear()

    result = util.get_effective_molecule_glob()

    assert result == MOLECULE_COLLECTION_GLOB
    assert "Collection 'test_namespace.test_collection' detected" in caplog.text


def test_get_effective_molecule_glob_extensions_dir_exists(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test get_effective_molecule_glob with extensions/molecule directory.

    Args:
        monkeypatch: pytest fixture for patching.
        tmp_path: pytest fixture for temporary directory.
        caplog: pytest fixture for log capture.
    """
    # Create valid collection
    galaxy_content = {"name": "test_collection", "namespace": "test_namespace"}
    galaxy_file = tmp_path / "galaxy.yml"
    galaxy_file.write_text(yaml.dump(galaxy_content))

    # Create the extensions/molecule directory structure
    extensions_molecule_dir = tmp_path / "extensions" / "molecule"
    extensions_molecule_dir.mkdir(parents=True)

    # Change to collection directory
    monkeypatch.chdir(tmp_path)

    # Clear caches
    util.get_collection_metadata.cache_clear()
    util.get_effective_molecule_glob.cache_clear()

    result = util.get_effective_molecule_glob()

    # Should detect collection since it's always enabled now
    assert result == MOLECULE_COLLECTION_GLOB
    assert "Collection 'test_namespace.test_collection' detected" in caplog.text


def test_get_effective_molecule_glob_respects_env_var(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Test get_effective_molecule_glob respects MOLECULE_GLOB environment variable.

    Args:
        monkeypatch: pytest fixture for patching.
        tmp_path: pytest fixture for temporary directory.
    """
    # Set custom MOLECULE_GLOB
    custom_glob = "custom/*/molecule.yml"
    monkeypatch.setenv("MOLECULE_GLOB", custom_glob)

    # Change to directory without galaxy.yml
    monkeypatch.chdir(tmp_path)

    # Clear caches
    util.get_collection_metadata.cache_clear()
    util.get_effective_molecule_glob.cache_clear()

    # Test that default MOLECULE_GLOB is returned since no collection
    result = util.get_effective_molecule_glob()

    assert result == custom_glob


def test_lookup_config_file_found_in_vcs_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test lookup_config_file finds config in VCS root.

    Args:
        monkeypatch: pytest fixture for patching.
        tmp_path: pytest fixture for temporary directory.
        caplog: pytest fixture for log capture.
    """
    # Create a git repository structure
    vcs_root = tmp_path / "vcs_root"
    vcs_root.mkdir()
    (vcs_root / ".git").mkdir()

    # Create config file in VCS root
    config_file = vcs_root / "molecule.yml"
    config_file.write_text("config: vcs_root")

    # Mock find_vcs_root to return our test directory
    monkeypatch.setattr("molecule.util.find_vcs_root", lambda _: str(vcs_root))

    # Change to a subdirectory
    subdir = vcs_root / "subdir"
    subdir.mkdir()
    monkeypatch.chdir(subdir)

    # Clear collection cache to avoid interference
    util.get_collection_metadata.cache_clear()

    result = util.lookup_config_file("molecule.yml")

    assert result == str(config_file)
    assert "Found config file" in caplog.text


def test_lookup_config_file_found_in_collection_extensions(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test lookup_config_file finds config in collection extensions directory.

    Args:
        monkeypatch: pytest fixture for patching.
        tmp_path: pytest fixture for temporary directory.
        caplog: pytest fixture for log capture.
    """
    # Create collection structure
    collection_root = tmp_path / "collection"
    collection_root.mkdir()

    # Create galaxy.yml
    galaxy_content = {"name": "test_collection", "namespace": "test_namespace"}
    galaxy_file = collection_root / "galaxy.yml"
    galaxy_file.write_text(yaml.dump(galaxy_content))

    # Create config in extensions/molecule/
    extensions_dir = collection_root / "extensions" / "molecule"
    extensions_dir.mkdir(parents=True)
    config_file = extensions_dir / "molecule.yml"
    config_file.write_text("config: collection_extensions")

    # Change to collection directory
    monkeypatch.chdir(collection_root)

    # Mock find_vcs_root to return empty (no VCS root)
    monkeypatch.setattr("molecule.util.find_vcs_root", lambda _: "~")

    # Clear caches
    util.get_collection_metadata.cache_clear()

    result = util.lookup_config_file("molecule.yml")

    assert result == str(config_file)
    assert "Found config file" in caplog.text


def test_lookup_config_file_found_in_home_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test lookup_config_file finds config in home directory.

    Args:
        monkeypatch: pytest fixture for patching.
        tmp_path: pytest fixture for temporary directory.
        caplog: pytest fixture for log capture.
    """
    # Create a fake home directory
    fake_home = tmp_path / "home"
    fake_home.mkdir()

    # Create config file in home directory
    config_file = fake_home / ".molecule.yml"
    config_file.write_text("config: home")

    # Mock Path.home() to return our fake home
    monkeypatch.setattr("molecule.util.Path.home", lambda: fake_home)

    # Mock find_vcs_root to return empty (no VCS root)
    monkeypatch.setattr("molecule.util.find_vcs_root", lambda _: "~")

    # Change to a different directory (not a collection)
    work_dir = tmp_path / "workdir"
    work_dir.mkdir()
    monkeypatch.chdir(work_dir)

    # Clear collection cache
    util.get_collection_metadata.cache_clear()

    result = util.lookup_config_file(".molecule.yml")

    assert result == str(config_file)
    assert "Found config file" in caplog.text


def test_lookup_config_file_search_priority_vcs_root_wins(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test lookup_config_file search priority - VCS root has highest priority.

    Args:
        monkeypatch: pytest fixture for patching.
        tmp_path: pytest fixture for temporary directory.
        caplog: pytest fixture for log capture.
    """
    # Create VCS root with config
    vcs_root = tmp_path / "vcs_root"
    vcs_root.mkdir()
    (vcs_root / ".git").mkdir()
    vcs_config = vcs_root / "molecule.yml"
    vcs_config.write_text("config: vcs_root")

    # Create fake home with config
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    home_config = fake_home / "molecule.yml"
    home_config.write_text("config: home")

    # Create collection with config
    collection_root = vcs_root / "collection"
    collection_root.mkdir()
    galaxy_content = {"name": "test", "namespace": "test"}
    galaxy_file = collection_root / "galaxy.yml"
    galaxy_file.write_text(yaml.dump(galaxy_content))
    extensions_dir = collection_root / "extensions" / "molecule"
    extensions_dir.mkdir(parents=True)
    collection_config = extensions_dir / "molecule.yml"
    collection_config.write_text("config: collection")

    # Set up mocks
    monkeypatch.setattr("molecule.util.find_vcs_root", lambda _: str(vcs_root))
    monkeypatch.setattr("molecule.util.Path.home", lambda: fake_home)

    # Change to collection directory
    monkeypatch.chdir(collection_root)

    # Clear caches
    util.get_collection_metadata.cache_clear()

    result = util.lookup_config_file("molecule.yml")

    # Should find VCS root config first (highest priority)
    assert result == str(vcs_config)
    assert "Found config file" in caplog.text


def test_lookup_config_file_search_priority_collection_over_home(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test lookup_config_file search priority - collection over home directory.

    Args:
        monkeypatch: pytest fixture for patching.
        tmp_path: pytest fixture for temporary directory.
        caplog: pytest fixture for log capture.
    """
    # Create fake home with config
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    home_config = fake_home / "molecule.yml"
    home_config.write_text("config: home")

    # Create collection with config
    collection_root = tmp_path / "collection"
    collection_root.mkdir()
    galaxy_content = {"name": "test", "namespace": "test"}
    galaxy_file = collection_root / "galaxy.yml"
    galaxy_file.write_text(yaml.dump(galaxy_content))
    extensions_dir = collection_root / "extensions" / "molecule"
    extensions_dir.mkdir(parents=True)
    collection_config = extensions_dir / "molecule.yml"
    collection_config.write_text("config: collection")

    # Set up mocks - no VCS root found
    monkeypatch.setattr("molecule.util.find_vcs_root", lambda _: "~")
    monkeypatch.setattr("molecule.util.Path.home", lambda: fake_home)

    # Change to collection directory
    monkeypatch.chdir(collection_root)

    # Clear caches
    util.get_collection_metadata.cache_clear()

    result = util.lookup_config_file("molecule.yml")

    # Should find collection config (higher priority than home)
    assert result == str(collection_config)
    assert "Found config file" in caplog.text


def test_lookup_config_file_not_found(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Test lookup_config_file returns None when config file not found.

    Args:
        monkeypatch: pytest fixture for patching.
        tmp_path: pytest fixture for temporary directory.
    """
    # Create empty directories
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    work_dir = tmp_path / "workdir"
    work_dir.mkdir()

    # Set up mocks - no VCS root, no collection
    monkeypatch.setattr("molecule.util.find_vcs_root", lambda _: "~")
    monkeypatch.setattr("molecule.util.Path.home", lambda: fake_home)

    # Change to work directory
    monkeypatch.chdir(work_dir)

    # Clear caches
    util.get_collection_metadata.cache_clear()

    result = util.lookup_config_file("nonexistent.yml")

    assert result is None


def test_lookup_config_file_handles_path_filename_extraction(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test lookup_config_file correctly extracts filename from path.

    Args:
        monkeypatch: pytest fixture for patching.
        tmp_path: pytest fixture for temporary directory.
        caplog: pytest fixture for log capture.
    """
    # Create collection structure
    collection_root = tmp_path / "collection"
    collection_root.mkdir()

    # Create galaxy.yml
    galaxy_content = {"name": "test", "namespace": "test"}
    galaxy_file = collection_root / "galaxy.yml"
    galaxy_file.write_text(yaml.dump(galaxy_content))

    # Create config in extensions/molecule/ with just the filename
    extensions_dir = collection_root / "extensions" / "molecule"
    extensions_dir.mkdir(parents=True)
    config_file = extensions_dir / "config.yml"
    config_file.write_text("config: test")

    # Change to collection directory
    monkeypatch.chdir(collection_root)

    # Mock find_vcs_root to return empty
    monkeypatch.setattr("molecule.util.find_vcs_root", lambda _: "~")

    # Clear caches
    util.get_collection_metadata.cache_clear()

    # Test with a full path - should extract just the filename
    result = util.lookup_config_file("/some/path/config.yml")

    assert result == str(config_file)
    assert "Found config file" in caplog.text


def test_lookup_config_file_collection_no_extensions_dir(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Test lookup_config_file when collection exists but no extensions directory.

    Args:
        monkeypatch: pytest fixture for patching.
        tmp_path: pytest fixture for temporary directory.
    """
    # Create collection without extensions directory
    collection_root = tmp_path / "collection"
    collection_root.mkdir()

    # Create galaxy.yml
    galaxy_content = {"name": "test", "namespace": "test"}
    galaxy_file = collection_root / "galaxy.yml"
    galaxy_file.write_text(yaml.dump(galaxy_content))

    # Create home config as fallback
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    home_config = fake_home / "molecule.yml"
    home_config.write_text("config: home")

    # Set up mocks
    monkeypatch.setattr("molecule.util.find_vcs_root", lambda _: "~")
    monkeypatch.setattr("molecule.util.Path.home", lambda: fake_home)

    # Change to collection directory
    monkeypatch.chdir(collection_root)

    # Clear caches
    util.get_collection_metadata.cache_clear()

    result = util.lookup_config_file("molecule.yml")

    # Should fall back to home directory since collection extensions dir doesn't exist
    assert result == str(home_config)

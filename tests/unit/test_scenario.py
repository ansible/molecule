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
import shutil

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from molecule import config, util
from molecule.scenario import Scenario


if TYPE_CHECKING:
    from unittest.mock import Mock


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.fixture
def _instance(
    patched_config_validate: Mock,
    config_instance: config.Config,
) -> Scenario:
    return Scenario(config_instance)


def test_prune(_instance: Scenario) -> None:  # noqa: PT019, D103
    e_dir = Path(_instance.ephemeral_directory)
    # prune data also includes files in the scenario inventory dir,
    # which is "<e_dir>/inventory" by default.
    # items are created in listed order, directories first, safe before pruned
    prune_data = {
        # these files should not be pruned
        "safe_files": ["state.yml", "ansible.cfg", "inventory/ansible_inventory.yml"],
        # these directories should not be pruned
        "safe_dirs": ["inventory"],
        # these files should be pruned
        "pruned_files": ["foo", "bar", "inventory/foo", "inventory/bar"],
        # these directories should be pruned, including empty subdirectories
        "pruned_dirs": ["baz", "roles", "inventory/baz", "roles/foo"],
    }

    for directory in prune_data["safe_dirs"] + prune_data["pruned_dirs"]:
        # inventory dir should already exist, and its existence is
        # required by the assertions below.
        if directory == "inventory":
            continue
        (e_dir / directory).mkdir()

    for file in prune_data["safe_files"] + prune_data["pruned_files"]:
        util.write_file(str(e_dir / file), "")

    _instance.prune()

    for safe_file in prune_data["safe_files"]:
        assert (e_dir / safe_file).is_file()

    for safe_dir in prune_data["safe_dirs"]:
        assert (e_dir / safe_dir).is_dir()

    for pruned_file in prune_data["pruned_files"]:
        assert not (e_dir / pruned_file).is_file()

    for pruned_dir in prune_data["pruned_dirs"]:
        assert not (e_dir / pruned_dir).is_dir()


def test_config_member(_instance: Scenario) -> None:  # noqa: PT019, D103
    assert isinstance(_instance.config, config.Config)


def test_scenario_init_calls_setup(  # noqa: D103
    patched_scenario_setup: Mock,
    _instance: Scenario,  # noqa: PT019
) -> None:
    patched_scenario_setup.assert_called_once_with()


def test_scenario_name_property(  # noqa: D103
    _instance: Scenario,  # noqa: PT019
) -> None:
    assert _instance.name == "default"


def test_ephemeral_directory_property(  # noqa: D103
    _instance: Scenario,  # noqa: PT019
) -> None:
    assert os.access(_instance.ephemeral_directory, os.W_OK)
    # assert that scenario path is included in in repr (useful for debugging)
    assert _instance.ephemeral_directory in repr(_instance)


def test_scenario_inventory_directory_property(  # noqa: D103
    _instance: Scenario,  # noqa: PT019
) -> None:
    e_dir = Path(_instance.config.scenario.ephemeral_directory) / "inventory"

    assert str(e_dir) == _instance.inventory_directory


def test_check_sequence_property(  # noqa: D103
    _instance: Scenario,  # noqa: PT019
) -> None:
    sequence = [
        "dependency",
        "cleanup",
        "destroy",
        "create",
        "prepare",
        "converge",
        "check",
        "cleanup",
        "destroy",
    ]

    assert sequence == _instance.check_sequence


def test_converge_sequence_property(  # noqa: D103
    _instance: Scenario,  # noqa: PT019
) -> None:
    sequence = ["dependency", "create", "prepare", "converge"]

    assert sequence == _instance.converge_sequence


def test_create_sequence_property(  # noqa: D103
    _instance: Scenario,  # noqa: PT019
) -> None:
    sequence = ["dependency", "create", "prepare"]

    assert sequence == _instance.create_sequence


def test_dependency_sequence_property(  # noqa: D103
    _instance: Scenario,  # noqa: PT019
) -> None:
    assert _instance.dependency_sequence == ["dependency"]


def test_destroy_sequence_property(  # noqa: D103
    _instance: Scenario,  # noqa: PT019
) -> None:
    assert _instance.destroy_sequence == ["dependency", "cleanup", "destroy"]


def test_idempotence_sequence_property(  # noqa: D103
    _instance: Scenario,  # noqa: PT019
) -> None:
    assert _instance.idempotence_sequence == ["idempotence"]


def test_prepare_sequence_property(  # noqa: D103
    _instance: Scenario,  # noqa: PT019
) -> None:
    assert _instance.prepare_sequence == ["prepare"]


def test_side_effect_sequence_property(  # noqa: D103
    _instance: Scenario,  # noqa: PT019
) -> None:
    assert _instance.side_effect_sequence == ["side_effect"]


def test_syntax_sequence_property(  # noqa: D103
    _instance: Scenario,  # noqa: PT019
) -> None:
    assert _instance.syntax_sequence == ["syntax"]


def test_test_sequence_property(  # noqa: D103
    _instance: Scenario,  # noqa: PT019
) -> None:
    sequence = [
        "dependency",
        "cleanup",
        "destroy",
        "syntax",
        "create",
        "prepare",
        "converge",
        "idempotence",
        "side_effect",
        "verify",
        "cleanup",
        "destroy",
    ]

    assert sequence == _instance.test_sequence


def test_verify_sequence_property(  # noqa: D103
    _instance: Scenario,  # noqa: PT019
) -> None:
    assert _instance.verify_sequence == ["verify"]


def test_sequence_property_with_invalid_subcommand(  # noqa: D103
    _instance: Scenario,  # noqa: PT019
) -> None:
    _instance.config.command_args = {"subcommand": "invalid"}

    assert _instance.sequence == []


def test_setup_creates_ephemeral_and_inventory_directories(  # noqa: D103
    _instance: Scenario,  # noqa: PT019
) -> None:
    ephemeral_dir = _instance.config.scenario.ephemeral_directory
    inventory_dir = _instance.config.scenario.inventory_directory
    shutil.rmtree(ephemeral_dir)
    _instance._setup()

    assert Path(ephemeral_dir).is_dir()
    assert Path(inventory_dir).is_dir()
    # assure we can write to ephemeral directory
    assert os.access(ephemeral_dir, os.W_OK)


def test_ephemeral_directory_overridden_via_env_var(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Confirm ephemeral_directory is overridden by MOLECULE_EPHEMERAL_DIRECTORY.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        tmp_path: Pytest tmp_path fixture.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MOLECULE_EPHEMERAL_DIRECTORY", "foo/bar")
    scenario = Scenario(config.Config(""))

    assert os.access(scenario.ephemeral_directory, os.W_OK)
    # Confirm MOLECULE_EPHEMERAL_DIRECTORY uses absolute path.
    assert Path(scenario.ephemeral_directory).is_absolute()
    assert scenario.ephemeral_directory.endswith("foo/bar")

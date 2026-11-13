"""End-to-end coverage for Ansible collection playbook references."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

from pathlib import Path
from typing import Any


FIXTURE_DIR = (
    Path(__file__).resolve().parent.parent
    / "fixtures"
    / "integration"
    / "test_collection_playbooks"
)
COLLECTION_NAME = "example.infra"
RECEIPTS = (
    "cleanup",
    "create",
    "converge",
    "destroy",
    "prepare",
    "side_effect",
    "verify",
)


def _copy_fixture(tmp_path: Path) -> Path:
    """Copy the fixture and point its Ansible environment at the local collection.

    Args:
        tmp_path: Temporary directory supplied by pytest.

    Returns:
        Path to the isolated project copy.
    """
    project = tmp_path / "project"
    shutil.copytree(FIXTURE_DIR, project)
    (project / "receipts").mkdir()
    config_path = project / "molecule" / "default" / "molecule.yml"
    config = config_path.read_text(encoding="utf-8")
    collection_path = (project / "collections").resolve()
    config_path.write_text(
        config.replace("__COLLECTIONS_PATH__", str(collection_path)),
        encoding="utf-8",
    )
    return project


def _run_molecule(project: Path, *args: str) -> subprocess.CompletedProcess[Any]:
    """Run Molecule in the isolated project copy.

    Args:
        project: Isolated Molecule project directory.
        *args: Molecule command-line arguments.

    Returns:
        Completed Molecule subprocess.
    """
    env = os.environ.copy()
    env.pop("MOLECULE_PROJECT_DIRECTORY", None)
    env.pop("MOLECULE_EPHEMERAL_DIRECTORY", None)
    env["PATH"] = f"{Path(sys.executable).parent}{os.pathsep}{env.get('PATH', '')}"
    env["ANSIBLE_FORCE_COLOR"] = "0"
    env["PY_COLORS"] = "0"
    return subprocess.run(
        [sys.executable, "-m", "molecule", *args],
        capture_output=True,
        text=True,
        check=False,
        cwd=project,
        env=env,
    )


def test_collection_playbooks_in_test_sequence(tmp_path: Path) -> None:
    """Execute every configured collection playbook through the test sequence.

    Args:
        tmp_path: Temporary directory supplied by pytest.
    """
    project = _copy_fixture(tmp_path)
    result = _run_molecule(project, "test")

    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    assert all((project / "receipts" / f"{name}.txt").is_file() for name in RECEIPTS)
    assert (project / "receipts" / "resource.txt").exists() is False
    assert [path.name for path in (project / "molecule" / "default").glob("*.yml")] == [
        "molecule.yml"
    ]


def test_missing_collection_playbook_fails_through_ansible(tmp_path: Path) -> None:
    """Ensure a missing collection fails without producing its receipt.

    Args:
        tmp_path: Temporary directory supplied by pytest.
    """
    project = _copy_fixture(tmp_path)
    config_path = project / "molecule" / "default" / "molecule.yml"
    config = config_path.read_text(encoding="utf-8")
    config_path.write_text(
        config.replace("example.infra.verify", "missing_namespace.missing_collection.verify"),
        encoding="utf-8",
    )

    result = _run_molecule(project, "test")

    diagnostic = f"{result.stdout}\n{result.stderr}"
    assert result.returncode != 0
    assert "missing_namespace.missing_collection.verify" in diagnostic
    assert not (project / "receipts" / "verify.txt").exists()

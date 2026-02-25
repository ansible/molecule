"""Integration tests for --workers parallel execution."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import textwrap

from pathlib import Path
from typing import Any

import pytest


SCENARIO_COUNT = 6

FIXTURE_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "integration" / "test_workers"


def _run_molecule(
    cwd: Path,
    args: list[str],
) -> subprocess.CompletedProcess[Any]:
    """Run molecule as a subprocess.

    Args:
        cwd: Working directory for the subprocess.
        args: Command-line arguments to pass to molecule.

    Returns:
        The completed process result.
    """
    cmd = [sys.executable, "-m", "molecule", *args]
    env = os.environ.copy()
    env["ANSIBLE_FORCE_COLOR"] = "0"
    env["PY_COLORS"] = "0"
    env.pop("MOLECULE_PROJECT_DIRECTORY", None)
    env.pop("MOLECULE_EPHEMERAL_DIRECTORY", None)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        cwd=cwd,
        env=env,
    )


@pytest.fixture(name="collection_dir")
def fixture_collection_dir(tmp_path: Path) -> Path:
    """Copy the static worker fixture collection into an isolated tmp_path.

    Args:
        tmp_path: Pytest tmp_path fixture.

    Returns:
        Path to the copied collection directory.
    """
    dest = tmp_path / "test_collection"
    shutil.copytree(FIXTURE_DIR, dest)
    return dest


def test_workers_parallel_success(collection_dir: Path) -> None:
    """Parallel run: all scenarios complete, ansible stdout suppressed, report works.

    Args:
        collection_dir: Path to the temporary collection fixture.
    """
    result = _run_molecule(
        collection_dir,
        ["test", "--all", "--workers", "2", "--report"],
    )

    assert result.returncode == 0, (
        f"Parallel execution failed.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "Starting parallel execution with 2 workers" in result.stderr
    for i in range(SCENARIO_COUNT):
        name = f"scenario_{i}"
        assert name in result.stderr
        assert f"STEP_PREPARE_SCENARIO_{name}" not in result.stdout, (
            f"Worker ansible output for {name} should be suppressed.\nstdout:\n{result.stdout}"
        )
    assert "DETAILS" in result.stderr
    assert "SCENARIO RECAP" in result.stderr


def test_workers_verbose_shows_ansible_output(collection_dir: Path) -> None:
    """Verify -v enables full ansible output streaming in worker mode.

    Args:
        collection_dir: Path to the temporary collection fixture.
    """
    result = _run_molecule(
        collection_dir,
        ["--verbose", "test", "--all", "--workers", "2"],
    )

    assert result.returncode == 0, (
        f"Verbose parallel execution failed.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    for i in range(SCENARIO_COUNT):
        name = f"scenario_{i}"
        assert f"STEP_PREPARE_SCENARIO_{name}" in result.stdout, (
            f"prepare output not visible for {name} in verbose mode.\nstdout:\n{result.stdout}"
        )


def test_workers_continue_on_failure(collection_dir: Path) -> None:
    """Continue-on-failure: remaining scenarios finish, failure output grouped, report works.

    Args:
        collection_dir: Path to the temporary collection fixture.
    """
    fail_dir = collection_dir / "extensions" / "molecule" / "scenario_0"
    (fail_dir / "converge.yml").write_text(
        textwrap.dedent("""\
        ---
        - name: Converge that fails
          hosts: all
          gather_facts: false
          tasks:
            - name: "Intentional failure"
              ansible.builtin.fail:
                msg: "WORKER_FAILURE_MARKER"
    """),
    )

    result = _run_molecule(
        collection_dir,
        ["test", "--all", "--workers", "2", "--continue-on-failure", "--report"],
    )

    assert result.returncode != 0
    assert "Scenarios failed" in result.stderr
    for i in range(1, SCENARIO_COUNT):
        assert f"Scenario 'scenario_{i}' completed successfully" in result.stderr
    assert "Failed: scenario_0 > converge" in result.stderr
    assert "WORKER_FAILURE_MARKER" in result.stderr
    assert "DETAILS" in result.stderr
    assert "SCENARIO RECAP" in result.stderr
    assert "failed" in result.stderr.lower()


def test_workers_fail_fast(collection_dir: Path) -> None:
    """Fail-fast stops after first failure; also validates cpus-1 resolution.

    Args:
        collection_dir: Path to the temporary collection fixture.
    """
    fail_dir = collection_dir / "extensions" / "molecule" / "scenario_0"
    (fail_dir / "converge.yml").write_text(
        textwrap.dedent("""\
        ---
        - name: Converge that fails
          hosts: all
          gather_facts: false
          tasks:
            - name: "Intentional failure"
              ansible.builtin.fail:
                msg: "This scenario is designed to fail"
    """),
    )

    result = _run_molecule(
        collection_dir,
        ["test", "--all", "--workers", "cpus-1"],
    )

    assert result.returncode != 0
    assert "Starting parallel execution with" in result.stderr
    assert "Scenarios failed" in result.stderr
    assert "Fail-fast" in result.stderr

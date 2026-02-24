"""Integration tests for --workers parallel execution."""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap

from pathlib import Path
from typing import Any

import pytest


SCENARIO_COUNT = 6

GALAXY_YML = textwrap.dedent("""\
    namespace: test_ns
    name: test_collection
    version: 1.0.0
    authors:
      - test
    readme: README.md
""")

CONFIG_YML = textwrap.dedent("""\
    ---
    prerun: false
    ansible:
      executor:
        args:
          ansible_playbook:
            - --inventory=${MOLECULE_SCENARIO_DIRECTORY}/../inventory.yml
    scenario:
      test_sequence:
        - prepare
        - converge
        - verify
    shared_state: true
""")

INVENTORY_YML = textwrap.dedent("""\
    ---
    all:
      hosts:
        instance:
          ansible_connection: local
""")

MOLECULE_YML_DEFAULT = textwrap.dedent("""\
    ---
    scenario:
      test_sequence:
        - create
        - destroy
""")


def _playbook(step: str, scenario: str) -> str:
    return textwrap.dedent(f"""\
        ---
        - name: {step} for {scenario}
          hosts: all
          gather_facts: false
          tasks:
            - name: "{step} debug"
              ansible.builtin.debug:
                msg: "STEP_{step.upper()}_SCENARIO_{scenario}"
    """)


def _build_collection(base: Path) -> Path:
    """Generate a temporary collection with a default scenario and N test scenarios."""
    (base / "galaxy.yml").write_text(GALAXY_YML)
    (base / "README.md").write_text("Test collection for worker integration tests.\n")

    mol_root = base / "extensions" / "molecule"
    mol_root.mkdir(parents=True)

    (mol_root / "config.yml").write_text(CONFIG_YML)
    (mol_root / "inventory.yml").write_text(INVENTORY_YML)

    default_dir = mol_root / "default"
    default_dir.mkdir()
    (default_dir / "molecule.yml").write_text(MOLECULE_YML_DEFAULT)
    for step in ("create", "destroy"):
        (default_dir / f"{step}.yml").write_text(_playbook(step, "default"))

    for i in range(SCENARIO_COUNT):
        name = f"scenario_{i}"
        scen_dir = mol_root / name
        scen_dir.mkdir()
        (scen_dir / "molecule.yml").write_text("")
        for step in ("prepare", "converge", "verify"):
            (scen_dir / f"{step}.yml").write_text(_playbook(step, name))

    return base


def _run_molecule(
    cwd: Path,
    args: list[str],
) -> subprocess.CompletedProcess[Any]:
    cmd = [sys.executable, "-m", "molecule", *args]
    env = os.environ.copy()
    env["ANSIBLE_FORCE_COLOR"] = "0"
    env["PY_COLORS"] = "0"
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        cwd=cwd,
        env=env,
    )


@pytest.fixture()
def collection_dir(tmp_path: Path) -> Path:
    """Create a temporary collection with multiple scenarios."""
    return _build_collection(tmp_path)


class TestWorkersIntegration:
    """Integration tests for worker-based parallel execution."""

    def test_workers_serial_baseline(self, collection_dir: Path) -> None:
        """Verify the generated collection works with serial execution and prepare runs for each."""
        result = _run_molecule(collection_dir, ["test", "--all"])

        assert result.returncode == 0, (
            f"Serial execution failed.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        for i in range(SCENARIO_COUNT):
            name = f"scenario_{i}"
            assert name in result.stderr
            assert f"STEP_PREPARE_SCENARIO_{name}" in result.stdout, (
                f"prepare did not run for {name}.\nstdout:\n{result.stdout}"
            )

    def test_workers_parallel(self, collection_dir: Path) -> None:
        """Verify parallel execution with --workers 2 and prepare runs for each scenario."""
        result = _run_molecule(
            collection_dir,
            ["test", "--all", "--workers", "2"],
        )

        assert result.returncode == 0, (
            f"Parallel execution failed.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        assert "Starting parallel execution with 2 workers" in result.stderr
        for i in range(SCENARIO_COUNT):
            name = f"scenario_{i}"
            assert name in result.stderr
            assert f"STEP_PREPARE_SCENARIO_{name}" in result.stdout, (
                f"prepare did not run for {name} in parallel mode.\nstdout:\n{result.stdout}"
            )

    def test_workers_all_scenarios_complete(self, collection_dir: Path) -> None:
        """Verify all scenarios produce output when run in parallel."""
        result = _run_molecule(
            collection_dir,
            ["test", "--all", "--workers", "3"],
        )

        assert result.returncode == 0, (
            f"Parallel execution failed.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        for i in range(SCENARIO_COUNT):
            assert f"scenario_{i}" in result.stderr

    def test_workers_cpus_minus_1(self, collection_dir: Path) -> None:
        """Verify --workers cpus-1 resolves and runs."""
        result = _run_molecule(
            collection_dir,
            ["test", "--all", "--workers", "cpus-1"],
        )

        assert result.returncode == 0, (
            f"cpus-1 execution failed.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        assert "Starting parallel execution with" in result.stderr

    def test_workers_report_success(self, collection_dir: Path) -> None:
        """Verify --report produces DETAILS and SCENARIO RECAP for all scenarios."""
        result = _run_molecule(
            collection_dir,
            ["test", "--all", "--workers", "2", "--report"],
        )

        assert result.returncode == 0, (
            f"Report execution failed.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        assert "DETAILS" in result.stderr
        assert "SCENARIO RECAP" in result.stderr
        for i in range(SCENARIO_COUNT):
            assert f"scenario_{i}" in result.stderr

    def test_workers_report_failure(self, collection_dir: Path) -> None:
        """Verify --report captures failed scenario details and correct summary."""
        fail_dir = collection_dir / "extensions" / "molecule" / "scenario_0"
        (fail_dir / "converge.yml").write_text(textwrap.dedent("""\
            ---
            - name: Converge that fails
              hosts: all
              gather_facts: false
              tasks:
                - name: "Intentional failure"
                  ansible.builtin.fail:
                    msg: "This scenario is designed to fail"
        """))

        result = _run_molecule(
            collection_dir,
            ["test", "--all", "--workers", "2", "--report", "--continue-on-failure"],
        )

        assert result.returncode != 0
        assert "DETAILS" in result.stderr
        assert "SCENARIO RECAP" in result.stderr
        assert "scenario_0" in result.stderr
        assert "failed" in result.stderr.lower()
        for i in range(1, SCENARIO_COUNT):
            assert f"scenario_{i}" in result.stderr

    def test_workers_continue_on_failure(self, collection_dir: Path) -> None:
        """Verify --continue-on-failure runs all scenarios even when one fails."""
        fail_dir = collection_dir / "extensions" / "molecule" / "scenario_0"
        (fail_dir / "converge.yml").write_text(textwrap.dedent("""\
            ---
            - name: Converge that fails
              hosts: all
              gather_facts: false
              tasks:
                - name: "Intentional failure"
                  ansible.builtin.fail:
                    msg: "This scenario is designed to fail"
        """))

        result = _run_molecule(
            collection_dir,
            ["test", "--all", "--workers", "2", "--continue-on-failure"],
        )

        assert result.returncode != 0
        assert "Scenarios failed" in result.stderr
        for i in range(1, SCENARIO_COUNT):
            assert f"Scenario 'scenario_{i}' completed successfully" in result.stderr

    def test_workers_fail_fast(self, collection_dir: Path) -> None:
        """Verify fail-fast stops after first failure."""
        fail_dir = collection_dir / "extensions" / "molecule" / "scenario_0"
        (fail_dir / "converge.yml").write_text(textwrap.dedent("""\
            ---
            - name: Converge that fails
              hosts: all
              gather_facts: false
              tasks:
                - name: "Intentional failure"
                  ansible.builtin.fail:
                    msg: "This scenario is designed to fail"
        """))

        result = _run_molecule(
            collection_dir,
            ["test", "--all", "--workers", "2"],
        )

        assert result.returncode != 0
        assert "Scenarios failed" in result.stderr
        assert "Fail-fast" in result.stderr

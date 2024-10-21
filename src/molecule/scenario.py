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
"""Molecule Scenario Module."""
from __future__ import annotations

import fcntl
import fnmatch
import logging
import os
import shutil

from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING

from molecule import scenarios, util
from molecule.constants import RC_TIMEOUT


if TYPE_CHECKING:
    from molecule.config import Config


LOG = logging.getLogger(__name__)


class Scenario:
    """A Molecule scenario."""

    def __init__(self, config: Config) -> None:
        """Initialize a new scenario class and returns None.

        Args:
            config: An instance of a Molecule config.
        """
        self._lock = None
        self.config = config
        self._setup()

    def _remove_scenario_state_directory(self) -> None:
        """Remove scenario cached disk stored state."""
        directory = str(Path(self.ephemeral_directory).parent)
        LOG.info("Removing %s", directory)
        shutil.rmtree(directory)

    def prune(self) -> None:
        """Prune the scenario ephemeral directory files.

        "safe files" will not be pruned, including the ansible configuration
        and inventory used by this scenario, the scenario state file, and
        files declared as "safe_files" in the ``driver`` configuration
        declared in ``molecule.yml``.
        """
        LOG.info("Pruning extra files from scenario ephemeral directory")

        safe_files = [
            self.config.state.state_file,
            *self.config.driver.safe_files,
        ]
        if self.config.provisioner is not None:
            safe_files += [
                self.config.provisioner.config_file,
                self.config.provisioner.inventory_file,
            ]

        existing_files = util.os_walk(self.ephemeral_directory, "*")
        for f in existing_files:
            if not any(sf for sf in safe_files if fnmatch.fnmatch(f, sf)):
                Path(f).unlink(missing_ok=True)

        # Remove empty directories.
        for dirpath, dirs, files in os.walk(self.ephemeral_directory, topdown=False):
            if not dirs and not files:
                os.removedirs(dirpath)

    @property
    def name(self) -> str:
        """Name of the scenario.

        Returns:
            The scenario's name.
        """
        return self.config.config["scenario"]["name"]

    @property
    def directory(self) -> str:
        """Scenario directory.

        Returns:
            The directory containing the scenario.
        """
        path = Path.cwd()
        if self.config.molecule_file:
            path = Path(self.config.molecule_file).parent
        return str(path)

    @property
    def ephemeral_directory(self) -> str:
        """Acquire the ephemeral directory.

        Returns:
            The ephemeral directory for this scenario.

        Raises:
            SystemExit: If lock cannot be acquired before timeout.
        """
        path: str | Path | None = os.getenv("MOLECULE_EPHEMERAL_DIRECTORY", None)
        if not path:
            project_directory = Path(self.config.project_directory).name

            if self.config.is_parallel:
                project_directory = f"{project_directory}-{self.config._run_uuid}"  # noqa: SLF001

            project_scenario_directory = Path(
                self.config.cache_directory,
                project_directory,
                self.name,
            )

            path = ephemeral_directory(project_scenario_directory)

        if isinstance(path, str):
            path = Path(path)

        if os.environ.get("MOLECULE_PARALLEL", False) and not self._lock:
            lock_file = path / ".lock"
            with lock_file.open("w") as self._lock:  # type: ignore[assignment]
                for i in range(1, 5):
                    try:
                        fcntl.lockf(self._lock, fcntl.LOCK_EX | fcntl.LOCK_NB)  # type: ignore[arg-type]
                        break
                    except OSError:
                        delay = 30 * i
                        LOG.warning(
                            "Retrying to acquire lock on %s, waiting for %s seconds",
                            path,
                            delay,
                        )
                        sleep(delay)
                else:
                    LOG.warning("Timedout trying to acquire lock on %s", path)
                    raise SystemExit(RC_TIMEOUT)

        return str(path)

    @property
    def inventory_directory(self) -> str:
        """Inventory directory.

        Returns:
            The directory containing the scenario's inventory.
        """
        path = Path(self.ephemeral_directory) / "inventory"
        return str(path)

    @property
    def check_sequence(self) -> list[str]:
        """Check playbook sequence.

        Returns:
            A list of playbooks to run for 'check'.
        """
        return self.config.config["scenario"]["check_sequence"]

    @property
    def cleanup_sequence(self) -> list[str]:
        """Cleanup playbook sequence.

        Returns:
            A list of playbooks to run for 'cleanup'.
        """
        return self.config.config["scenario"]["cleanup_sequence"]

    @property
    def converge_sequence(self) -> list[str]:
        """Converge playbook sequence.

        Returns:
            A list of playbooks to run for 'converge'.
        """
        return self.config.config["scenario"]["converge_sequence"]

    @property
    def create_sequence(self) -> list[str]:
        """Create playbook sequence.

        Returns:
            A list of playbooks to run for 'create'.
        """
        return self.config.config["scenario"]["create_sequence"]

    @property
    def dependency_sequence(self) -> list[str]:
        """Dependency playbook sequence.

        Returns:
            A list of playbooks to run for 'dependency'.
        """
        return ["dependency"]

    @property
    def destroy_sequence(self) -> list[str]:
        """Destroy playbook sequence.

        Returns:
            A list of playbooks to run for 'destroy'.
        """
        return self.config.config["scenario"]["destroy_sequence"]

    @property
    def idempotence_sequence(self) -> list[str]:
        """Idempotence playbook sequence.

        Returns:
            A list of playbooks to run for 'idempotence'.
        """
        return ["idempotence"]

    @property
    def prepare_sequence(self) -> list[str]:
        """Prepare playbook sequence.

        Returns:
            A list of playbooks to run for 'prepare'.
        """
        return ["prepare"]

    @property
    def side_effect_sequence(self) -> list[str]:
        """Side effect playbook sequence.

        Returns:
            A list of playbooks to run for 'side_effect'.
        """
        return ["side_effect"]

    @property
    def syntax_sequence(self) -> list[str]:
        """Syntax playbook sequence.

        Returns:
            A list of playbooks to run for 'syntax'.
        """
        return ["syntax"]

    @property
    def test_sequence(self) -> list[str]:
        """Test playbook sequence.

        Returns:
            A list of playbooks to run for 'test'.
        """
        return self.config.config["scenario"]["test_sequence"]

    @property
    def verify_sequence(self) -> list[str]:
        """Verify playbook sequence.

        Returns:
            A list of playbooks to run for 'verify'.
        """
        return ["verify"]

    @property
    def sequence(self) -> list[str]:
        """Select the sequence based on scenario and subcommand of the provided scenario.

        Returns:
            A list of playbooks to run.

        Raises:
            RuntimeError: if an unexpected sequence type is requested.
        """
        result = []
        our_scenarios = scenarios.Scenarios([self.config])
        matrix = our_scenarios._get_matrix()  # noqa: SLF001

        try:
            result = matrix[self.name][self.config.subcommand]
            if not isinstance(result, list):
                raise RuntimeError(  # noqa: TRY003, TRY004
                    "Unexpected sequence type {result}.",  # noqa: EM101
                )
        except KeyError:
            pass
        return result

    def _setup(self) -> None:
        """Prepare the scenario for Molecule."""
        inventory = Path(self.inventory_directory)
        if not inventory.is_dir():
            inventory.mkdir(exist_ok=True, parents=True)


def ephemeral_directory(path: Path | None = None) -> Path:
    """Return temporary directory to be used by molecule.

    Molecule users should not make any assumptions about its location,
    permissions or its content as this may change in future release.

    Args:
        path: Ephemeral directory name.

    Returns:
        The full ephemeral directory path.

    Raises:
        RuntimeError: If ephemeral directory location cannot be determined
    """
    d: str | Path | None = os.getenv("MOLECULE_EPHEMERAL_DIRECTORY")
    if not d:
        d = os.getenv("XDG_CACHE_HOME", Path("~/.cache").expanduser())
    if not d:
        msg = "Unable to determine ephemeral directory to use."
        raise RuntimeError(msg)

    if isinstance(d, str):
        d = Path(d)
    d = d.resolve() / (path if path else "molecule")

    if not d.is_dir():
        os.umask(0o077)
        d.mkdir(mode=0o700, parents=True, exist_ok=True)

    return d

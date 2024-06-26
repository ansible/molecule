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

import errno
import fcntl
import fnmatch
import logging
import os
import shutil

from pathlib import Path
from time import sleep

from molecule import scenarios, util
from molecule.constants import RC_TIMEOUT


LOG = logging.getLogger(__name__)


class Scenario:
    """A Molecule scenario."""

    def __init__(self, config) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN001
        """Initialize a new scenario class and returns None.

        Args:
            config: An instance of a Molecule config.
        """
        self._lock = None
        self.config = config
        self._setup()  # type: ignore[no-untyped-call]

    def _remove_scenario_state_directory(self: Scenario) -> None:
        """Remove scenario cached disk stored state."""
        directory = str(Path(self.ephemeral_directory).parent)
        LOG.info("Removing %s", directory)
        shutil.rmtree(directory)

    def prune(self: Scenario) -> None:
        """Prune the scenario ephemeral directory files and returns None.

        "safe files" will not be pruned, including the ansible configuration
        and inventory used by this scenario, the scenario state file, and
        files declared as "safe_files" in the ``driver`` configuration
        declared in ``molecule.yml``.

        """
        LOG.info("Pruning extra files from scenario ephemeral directory")
        safe_files = [
            self.config.provisioner.config_file,
            self.config.provisioner.inventory_file,
            self.config.state.state_file,
            *self.config.driver.safe_files,
        ]
        files = util.os_walk(self.ephemeral_directory, "*")  # type: ignore[no-untyped-call]
        for f in files:
            if not any(sf for sf in safe_files if fnmatch.fnmatch(f, sf)):
                try:
                    os.remove(f)  # noqa: PTH107
                except OSError as e:
                    if e.errno != errno.ENOENT:
                        raise

        # Remove empty directories.
        for dirpath, dirs, files in os.walk(self.ephemeral_directory, topdown=False):
            if not dirs and not files:
                os.removedirs(dirpath)

    @property
    def name(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self.config.config["scenario"]["name"]

    @property
    def directory(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        if self.config.molecule_file:
            return os.path.dirname(self.config.molecule_file)  # noqa: PTH120
        return os.getcwd()  # noqa: PTH109

    @property
    def ephemeral_directory(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        path = os.getenv("MOLECULE_EPHEMERAL_DIRECTORY", None)
        if not path:
            project_directory = os.path.basename(self.config.project_directory)  # noqa: PTH119

            if self.config.is_parallel:
                project_directory = f"{project_directory}-{self.config._run_uuid}"  # noqa: SLF001

            project_scenario_directory = os.path.join(  # noqa: PTH118
                self.config.cache_directory,
                project_directory,
                self.name,
            )

            path = ephemeral_directory(project_scenario_directory)

        if os.environ.get("MOLECULE_PARALLEL", False) and not self._lock:
            with open(os.path.join(path, ".lock"), "w") as self._lock:  # type: ignore[assignment]  # noqa: PTH118, PTH123
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

        return path

    @property
    def inventory_directory(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return os.path.join(self.ephemeral_directory, "inventory")  # noqa: PTH118

    @property
    def check_sequence(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self.config.config["scenario"]["check_sequence"]

    @property
    def cleanup_sequence(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self.config.config["scenario"]["cleanup_sequence"]

    @property
    def converge_sequence(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self.config.config["scenario"]["converge_sequence"]

    @property
    def create_sequence(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self.config.config["scenario"]["create_sequence"]

    @property
    def dependency_sequence(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return ["dependency"]

    @property
    def destroy_sequence(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self.config.config["scenario"]["destroy_sequence"]

    @property
    def idempotence_sequence(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return ["idempotence"]

    @property
    def prepare_sequence(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return ["prepare"]

    @property
    def side_effect_sequence(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return ["side_effect"]

    @property
    def syntax_sequence(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return ["syntax"]

    @property
    def test_sequence(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self.config.config["scenario"]["test_sequence"]

    @property
    def verify_sequence(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return ["verify"]

    @property
    def sequence(self) -> list[str]:
        """Select the sequence based on scenario and subcommand of the provided scenario object and returns a list."""  # noqa: E501
        result = []
        our_scenarios = scenarios.Scenarios([self.config])
        matrix = our_scenarios._get_matrix()  # type: ignore[no-untyped-call]  # noqa: SLF001

        try:
            result = matrix[self.name][self.config.subcommand]
            if not isinstance(result, list):
                raise RuntimeError(  # noqa: TRY003, TRY004
                    "Unexpected sequence type {result}.",  # noqa: EM101
                )
        except KeyError:
            pass
        return result

    def _setup(self):  # type: ignore[no-untyped-def]  # noqa: ANN202
        """Prepare the scenario for Molecule and returns None."""
        if not os.path.isdir(self.inventory_directory):  # noqa: PTH112
            os.makedirs(self.inventory_directory, exist_ok=True)  # noqa: PTH103


def ephemeral_directory(path: str | None = None) -> str:
    """Return temporary directory to be used by molecule.

    Molecule users should not make any assumptions about its location,
    permissions or its content as this may change in future release.
    """
    d = os.getenv("MOLECULE_EPHEMERAL_DIRECTORY")
    if not d:
        d = os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))  # noqa: PTH111
    if not d:
        raise RuntimeError("Unable to determine ephemeral directory to use.")  # noqa: EM101, TRY003
    d = os.path.abspath(os.path.join(d, path if path else "molecule"))  # noqa: PTH100, PTH118

    if not os.path.isdir(d):  # noqa: PTH112
        os.umask(0o077)
        Path(d).mkdir(mode=0o700, parents=True, exist_ok=True)

    return d

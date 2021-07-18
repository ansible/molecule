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

import fcntl
import fnmatch
import logging
import os
import shutil
from pathlib import Path
from time import sleep
from typing import Optional

from molecule import scenarios, util
from molecule.constants import RC_TIMEOUT

LOG = logging.getLogger(__name__)


class Scenario(object):
    """
    A scenario allows Molecule test a role in a particular way, this is a \
    fundamental change from Molecule v1.

    A scenario is a self-contained directory containing everything necessary
    for testing the role in a particular way.  The default scenario is named
    ``default``, and every role should contain a default scenario.

    Unless mentioned explicitly, the scenario name will be the directory name
    hosting the files.

    Any option set in this section will override the defaults.

    .. code-block:: yaml

        scenario:
          create_sequence:
            - dependency
            - create
            - prepare
          check_sequence:
            - dependency
            - cleanup
            - destroy
            - create
            - prepare
            - converge
            - check
            - destroy
          converge_sequence:
            - dependency
            - create
            - prepare
            - converge
          destroy_sequence:
            - dependency
            - cleanup
            - destroy
          test_sequence:
            - dependency
            - lint
            - cleanup
            - destroy
            - syntax
            - create
            - prepare
            - converge
            - idempotence
            - side_effect
            - verify
            - cleanup
            - destroy
    """  # noqa

    def __init__(self, config):
        """
        Initialize a new scenario class and returns None.

        :param config: An instance of a Molecule config.
        :return: None
        """
        self._lock = None
        self.config = config
        self._setup()

    def _remove_scenario_state_directory(self):
        """Remove scenario cached disk stored state.

        :return: None
        """
        directory = str(Path(self.ephemeral_directory).parent)
        LOG.info("Removing {}".format(directory))
        shutil.rmtree(directory)

    def prune(self):
        """
        Prune the scenario ephemeral directory files and returns None.

        "safe files" will not be pruned, including the ansible configuration
        and inventory used by this scenario, the scenario state file, and
        files declared as "safe_files" in the ``driver`` configuration
        declared in ``molecule.yml``.

        :return: None
        """
        LOG.info("Pruning extra files from scenario ephemeral directory")
        safe_files = [
            self.config.provisioner.config_file,
            self.config.provisioner.inventory_file,
            self.config.state.state_file,
        ] + self.config.driver.safe_files
        files = util.os_walk(self.ephemeral_directory, "*")
        for f in files:
            if not any(sf for sf in safe_files if fnmatch.fnmatch(f, sf)):
                os.remove(f)

        # Remove empty directories.
        for dirpath, dirs, files in os.walk(self.ephemeral_directory, topdown=False):
            if not dirs and not files:
                os.removedirs(dirpath)

    @property
    def name(self):
        return self.config.config["scenario"]["name"]

    @property
    def directory(self):
        if self.config.molecule_file:
            return os.path.dirname(self.config.molecule_file)
        else:
            return os.getcwd()

    @property
    def ephemeral_directory(self):
        path = os.getenv("MOLECULE_EPHEMERAL_DIRECTORY", None)
        if not path:

            project_directory = os.path.basename(self.config.project_directory)

            if self.config.is_parallel:
                project_directory = "{}-{}".format(
                    project_directory, self.config._run_uuid
                )

            project_scenario_directory = os.path.join(
                self.config.cache_directory, project_directory, self.name
            )

            path = ephemeral_directory(project_scenario_directory)

        if os.environ.get("MOLECULE_PARALLEL", False) and not self._lock:
            with open(os.path.join(path, ".lock"), "w") as self._lock:
                for i in range(1, 5):
                    try:
                        fcntl.lockf(self._lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
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
    def inventory_directory(self):
        return os.path.join(self.ephemeral_directory, "inventory")

    @property
    def check_sequence(self):
        return self.config.config["scenario"]["check_sequence"]

    @property
    def cleanup_sequence(self):
        return self.config.config["scenario"]["cleanup_sequence"]

    @property
    def converge_sequence(self):
        return self.config.config["scenario"]["converge_sequence"]

    @property
    def create_sequence(self):
        return self.config.config["scenario"]["create_sequence"]

    @property
    def dependency_sequence(self):
        return ["dependency"]

    @property
    def destroy_sequence(self):
        return self.config.config["scenario"]["destroy_sequence"]

    @property
    def idempotence_sequence(self):
        return ["idempotence"]

    @property
    def lint_sequence(self):
        # see https://github.com/ansible-community/molecule/issues/2216
        return ["dependency", "lint"]

    @property
    def prepare_sequence(self):
        return ["prepare"]

    @property
    def side_effect_sequence(self):
        return ["side_effect"]

    @property
    def syntax_sequence(self):
        return ["syntax"]

    @property
    def test_sequence(self):
        return self.config.config["scenario"]["test_sequence"]

    @property
    def verify_sequence(self):
        return ["verify"]

    @property
    def sequence(self):
        """
        Select the sequence based on scenario and subcommand of the provided \
        scenario object and returns a list.

        :param scenario: A scenario object.
        :param skipped: An optional bool to include skipped scenarios.
        :return: list
        """
        s = scenarios.Scenarios([self.config])
        matrix = s._get_matrix()

        try:
            return matrix[self.name][self.config.subcommand]
        except KeyError:
            # TODO(retr0h): May change this handling in the future.
            return []

    def _setup(self):
        """
        Prepare the scenario for Molecule and returns None.

        :return: None
        """
        if not os.path.isdir(self.inventory_directory):
            os.makedirs(self.inventory_directory)


def ephemeral_directory(path: Optional[str] = None) -> str:
    """
    Return temporary directory to be used by molecule.

    Molecule users should not make any assumptions about its location,
    permissions or its content as this may change in future release.
    """
    d = os.getenv("MOLECULE_EPHEMERAL_DIRECTORY")
    if not d:
        d = os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
    if not d:
        raise RuntimeError("Unable to determine ephemeral directory to use.")
    d = os.path.abspath(os.path.join(d, path if path else "molecule"))

    if not os.path.isdir(d):
        os.umask(0o077)
        Path(d).mkdir(mode=0o700, parents=True, exist_ok=True)

    return d

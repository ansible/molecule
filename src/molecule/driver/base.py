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
"""Base Driver Module."""
from __future__ import annotations

import inspect
import os

from abc import ABC, abstractmethod
from importlib.metadata import version
from pathlib import Path
from typing import TYPE_CHECKING

from molecule.status import Status


if TYPE_CHECKING:
    from molecule.config import Config
    from molecule.types import DriverOptions


class Driver(ABC):
    """Driver Class.

    Attributes:
        title: Short description of the driver.
    """

    title = ""

    def __init__(self, config: Config) -> None:
        """Initialize code for all :ref:`Driver` classes.

        Args:
            config: An instance of a Molecule config.
        """
        self._config = config
        self._path = os.path.abspath(  # noqa: PTH100
            os.path.dirname(inspect.getfile(self.__class__)),  # noqa: PTH120
        )
        self.module = self.__module__.split(".", maxsplit=1)[0]
        self.version = version(self.module)

    @property
    @abstractmethod
    def name(self) -> str:  # pragma: no cover
        """Name of the driver.

        Returns:
            Name of the driver.
        """

    @name.setter
    @abstractmethod
    def name(self, value: str) -> None:  # pragma: no cover
        """Driver name setter.

        Args:
            value: New driver name.
        """

    @property
    def testinfra_options(self) -> dict[str, str]:
        """Testinfra specific options and returns a dict.

        :returns: dict
        """
        return {
            "connection": "ansible",
            "ansible-inventory": self._config.provisioner.inventory_directory,  # type: ignore[union-attr]
        }

    @property
    @abstractmethod
    def login_cmd_template(self) -> str:  # pragma: no cover
        """Get the login command template to be populated by ``login_options`` as a string.

        Returns:
            str
        """

    @property
    @abstractmethod
    def default_ssh_connection_options(self) -> list[str]:  # pragma: no cover
        """SSH client options and returns a list.

        :returns: list
        """

    @property
    @abstractmethod
    def default_safe_files(self) -> list[str]:  # pragma: no cover
        """Generate files to be preserved.

        :returns: list
        """

    @abstractmethod
    def login_options(
        self,
        instance_name: str,
    ) -> dict[str, str]:  # pragma: no cover
        """Options used in the login command and returns a dict.

        Args:
            instance_name: A string containing the instance to login to.

        Returns:
            dict
        """

    @abstractmethod
    def ansible_connection_options(
        self,
        instance_name: str,
    ) -> dict[str, str]:  # pragma: no cover
        """Ansible specific connection options supplied to inventory and returns a dict.

        Args:
            instance_name: A string containing the instance to login to.

        Returns:
            dict
        """

    @abstractmethod
    def sanity_checks(self) -> None:
        """Confirm that driver is usable.

        Sanity checks to ensure the driver can do work successfully. For
        example, when using the Docker driver, we want to know that the Docker
        daemon is running and we have the correct Docker Python dependency.
        Each driver implementation can decide what is the most stable sanity
        check for itself.
        """

    @property
    def options(self) -> DriverOptions:
        """Driver options.

        Returns:
            Dictionary of driver options.
        """
        return self._config.config["driver"]["options"]

    @property
    def instance_config(self) -> str:
        """Instance config file location.

        Returns:
            Path to instance_config.yml.
        """
        return str(
            Path(
                self._config.scenario.ephemeral_directory,
                "instance_config.yml",
            ),
        )

    @property
    def ssh_connection_options(self) -> list[str]:
        """SSH connection options.

        Returns:
            List of ssh connection options.
        """
        if self._config.config["driver"]["ssh_connection_options"]:
            return self._config.config["driver"]["ssh_connection_options"]
        return self.default_ssh_connection_options

    @property
    def safe_files(self) -> list[str]:
        """Safe files.

        Returns:
            List of safe files.
        """
        return self.default_safe_files + self._config.config["driver"]["safe_files"]

    @property
    def delegated(self) -> bool:
        """Is the driver delegated.

        Returns:
            Whether the driver is delegated.
        """
        return self.name == "default"

    @property
    def managed(self) -> bool:
        """Is the driver is managed.

        Returns:
            Whether the driver is managed.
        """
        return self.options["managed"]

    def status(self) -> list[Status]:
        """Collect the instances state and returns a list.

        !!! note

            Molecule assumes all instances were created successfully by
            Ansible, otherwise Ansible would return an error on create.  This
            may prove to be a bad assumption.  However, configuring Molecule's
            driver to match the options passed to the playbook may prove
            difficult.  Especially in cases where the user is provisioning
            instances off localhost.

        Returns:
            Status for each instance.
        """
        status_list = []
        for platform in self._config.platforms.instances:
            instance_name = platform["name"]
            driver_name = self.name
            provisioner_name = self._config.provisioner.name if self._config.provisioner else ""
            scenario_name = self._config.scenario.name

            status_list.append(
                Status(
                    instance_name=instance_name,
                    driver_name=driver_name,
                    provisioner_name=provisioner_name,
                    scenario_name=scenario_name,
                    created=self._created(),
                    converged=self._converged(),
                ),
            )

        return status_list

    def _get_ssh_connection_options(self) -> list[str]:
        # LogLevel=ERROR is needed in order to avoid warnings like:
        # Warning: Permanently added ... to the list of known hosts.
        return [
            "-o UserKnownHostsFile=/dev/null",
            "-o ControlMaster=auto",
            "-o ControlPersist=60s",
            "-o ForwardX11=no",
            "-o LogLevel=ERROR",
            "-o IdentitiesOnly=yes",
            "-o StrictHostKeyChecking=no",
        ]

    def _created(self) -> str:
        return str(self._config.state.created).lower()

    def _converged(self) -> str:
        return str(self._config.state.converged).lower()

    def __eq__(self, other: object) -> bool:
        """Implement equality comparison.

        Args:
            other: object to compare against this one.

        Returns:
            Whether other matches the name of this driver.
        """
        # trick that allows us to test if a driver is loaded via:
        # if 'driver-name' in drivers()
        return str(self) == str(other)

    def __lt__(self, other: object) -> bool:
        """Implement lower than comparison.

        Args:
            other: object to compare against this one.

        Returns:
            Whether other is less than the name of this driver.
        """
        return str.__lt__(str(self), str(other))

    def __hash__(self) -> int:
        """Perform object hash.

        Returns:
            Hash of driver name.
        """
        return self.name.__hash__()

    def __str__(self) -> str:
        """Return readable string representation of object.

        Returns:
            Driver name.
        """
        return self.name

    def __repr__(self) -> str:
        """Return detailed string representation of object.

        Returns:
            Driver name.
        """
        return self.name

    def __rich__(self) -> str:
        """Return rich representation of object.

        Returns:
            Driver name.
        """
        return self.__str__()

    def get_playbook(self, step: str) -> str | None:
        """Return embedded playbook location or None.

        The default location is relative to the file implementing the driver
        class, allowing driver writers to define playbooks without having
        to override this method.

        Args:
            step: The step to look for a playbook for.

        Returns:
            The playbook file path, if any.
        """
        p = Path(
            self._path,
            "playbooks",
            step + ".yml",
        )
        if p.is_file():
            return str(p)
        return None

    def schema_file(self) -> str | None:  # pragma: no cover
        """Return schema file path.

        Returns:
            Path to schema file.
        """
        return None

    def modules_dir(self) -> str | None:
        """Return path to ansible modules included with driver.

        Returns:
            Path to modules dir if one exists.
        """
        p = Path(self._path, "modules")
        if p.is_dir():
            return str(p)
        return None

    def reset(self) -> None:
        """Release all resources owned by molecule.

        This is a destructive operation that would affect all resources managed
        by molecule, regardless the scenario name.  Molecule will use metadata
        like labels or tags to annotate resources allocated by it.
        """
        return

    @property
    def required_collections(self) -> dict[str, str]:
        """Return collections dict containing names and versions required."""
        return {}

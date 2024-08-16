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

from abc import ABCMeta, abstractmethod
from importlib.metadata import version

from molecule.status import Status


class Driver:
    """Driver Class.

    Attributes:
        title: Short description of the driver.
    """

    __metaclass__ = ABCMeta
    title = ""

    def __init__(self, config=None) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN001
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
        """Name of the driver and returns a string.

        :returns: str
        """

    @name.setter
    def name(self, value):  # type: ignore[no-untyped-def] # pragma: no cover  # noqa: ANN001, ANN202
        """Driver name setter and returns None.

        :returns: None
        """

    @property
    def testinfra_options(self):  # type: ignore[no-untyped-def]  # noqa: ANN201
        """Testinfra specific options and returns a dict.

        :returns: dict
        """
        return {
            "connection": "ansible",
            "ansible-inventory": self._config.provisioner.inventory_directory,
        }

    @property
    @abstractmethod
    def login_cmd_template(self):  # type: ignore[no-untyped-def] # pragma: no cover  # noqa: ANN201
        """Get the login command template to be populated by ``login_options`` as a string.

        Returns:
            str
        """

    @property
    @abstractmethod
    def default_ssh_connection_options(self):  # type: ignore[no-untyped-def] # pragma: no cover  # noqa: ANN201
        """SSH client options and returns a list.

        :returns: list
        """

    @property
    @abstractmethod
    def default_safe_files(self):  # type: ignore[no-untyped-def] # pragma: no cover  # noqa: ANN201
        """Generate files to be preserved.

        :returns: list
        """

    @abstractmethod
    def login_options(self, instance_name):  # type: ignore[no-untyped-def] # pragma: no cover  # noqa: ANN001, ANN201
        """Options used in the login command and returns a dict.

        Args:
            instance_name: A string containing the instance to login to.

        Returns:
            dict
        """

    @abstractmethod
    def ansible_connection_options(self, instance_name):  # type: ignore[no-untyped-def] # pragma: no cover  # noqa: ANN001, ANN201
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

        :returns: None
        """

    @property
    def options(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self._config.config["driver"]["options"]

    @property
    def instance_config(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return os.path.join(  # noqa: PTH118
            self._config.scenario.ephemeral_directory,
            "instance_config.yml",
        )

    @property
    def ssh_connection_options(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        if self._config.config["driver"]["ssh_connection_options"]:
            return self._config.config["driver"]["ssh_connection_options"]
        return self.default_ssh_connection_options

    @property
    def safe_files(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self.default_safe_files + self._config.config["driver"]["safe_files"]

    @property
    def delegated(self):  # type: ignore[no-untyped-def]  # noqa: ANN201
        """Is the dedriver delegated and returns a bool.

        :returns: bool
        """
        return self.name == "default"

    @property
    def managed(self):  # type: ignore[no-untyped-def]  # noqa: ANN201
        """Is the driver is managed and returns a bool.

        :returns: bool
        """
        return self.options["managed"]

    def status(self):  # type: ignore[no-untyped-def]  # noqa: ANN201
        """Collect the instances state and returns a list.

        !!! note

            Molecule assumes all instances were created successfully by
            Ansible, otherwise Ansible would return an error on create.  This
            may prove to be a bad assumption.  However, configuring Molecule's
            driver to match the options passed to the playbook may prove
            difficult.  Especially in cases where the user is provisioning
            instances off localhost.
        :returns: list
        """
        status_list = []
        for platform in self._config.platforms.instances:
            instance_name = platform["name"]
            driver_name = self.name
            provisioner_name = self._config.provisioner.name
            scenario_name = self._config.scenario.name

            status_list.append(
                Status(
                    instance_name=instance_name,
                    driver_name=driver_name,
                    provisioner_name=provisioner_name,
                    scenario_name=scenario_name,
                    created=self._created(),  # type: ignore[no-untyped-call]
                    converged=self._converged(),  # type: ignore[no-untyped-call]
                ),
            )

        return status_list

    def _get_ssh_connection_options(self):  # type: ignore[no-untyped-def]  # noqa: ANN202
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

    def _created(self):  # type: ignore[no-untyped-def]  # noqa: ANN202
        return str(self._config.state.created).lower()

    def _converged(self):  # type: ignore[no-untyped-def]  # noqa: ANN202
        return str(self._config.state.converged).lower()

    def __eq__(self, other):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN204
        """Implement equality comparison."""
        # trick that allows us to test if a driver is loaded via:
        # if 'driver-name' in drivers()
        return str(self) == str(other)

    def __lt__(self, other):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN204
        """Implement lower than comparison."""
        return str.__lt__(str(self), str(other))

    def __hash__(self):  # type: ignore[no-untyped-def]  # noqa: ANN204
        """Perform object hash."""
        return self.name.__hash__()

    def __str__(self) -> str:
        """Return readable string representation of object."""
        return self.name

    def __repr__(self) -> str:
        """Return detailed string representation of object."""
        return self.name

    def __rich__(self):  # type: ignore[no-untyped-def]  # noqa: ANN204
        """Return rich representation of object."""
        return self.__str__()

    def get_playbook(self, step):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
        """Return embedded playbook location or None.

        The default location is relative to the file implementing the driver
        class, allowing driver writers to define playbooks without having
        to override this method.
        """
        p = os.path.join(  # noqa: PTH118
            self._path,
            "playbooks",
            step + ".yml",
        )
        if os.path.isfile(p):  # noqa: PTH113
            return p
        return None

    def schema_file(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return None

    def modules_dir(self):  # type: ignore[no-untyped-def]  # noqa: ANN201
        """Return path to ansible modules included with driver."""
        p = os.path.join(self._path, "modules")  # noqa: PTH118
        if os.path.isdir(p):  # noqa: PTH112
            return p
        return None

    def reset(self):  # type: ignore[no-untyped-def]  # noqa: ANN201
        """Release all resources owned by molecule.

        This is a destructive operation that would affect all resources managed
        by molecule, regardless the scenario name.  Molecule will use metadata
        like labels or tags to annotate resources allocated by it.
        """

    @property
    def required_collections(self) -> dict[str, str]:
        """Return collections dict containing names and versions required."""
        return {}

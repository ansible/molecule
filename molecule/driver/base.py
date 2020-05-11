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

import abc
import inspect
import os

import molecule
from molecule.status import Status


class Driver(object):
    """Driver Class."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, config=None):
        """
        Initialize code for all :ref:`Driver` classes.

        :param config: An instance of a Molecule config.
        :returns: None
        """
        self._config = config
        self._path = os.path.abspath(os.path.dirname(inspect.getfile(self.__class__)))

    @property  # type: ignore
    @abc.abstractmethod
    def name(self):  # pragma: no cover
        """
        Name of the driver and returns a string.

        :returns: str
        """
        pass

    @name.setter  # type: ignore
    @abc.abstractmethod
    def name(self, value):  # pragma: no cover
        """
        Driver name setter and returns None.

        :returns: None
        """
        pass

    @property
    def testinfra_options(self):
        """
        Testinfra specific options and returns a dict.

        :returns: dict
        """
        return {
            "connection": "ansible",
            "ansible-inventory": self._config.provisioner.inventory_file,
        }

    @abc.abstractproperty
    def login_cmd_template(self):  # pragma: no cover
        """
        Get the login command template to be populated by ``login_options`` as \
        a string.

        :returns: str
        """
        pass

    @abc.abstractproperty
    def default_ssh_connection_options(self):  # pragma: no cover
        """
        SSH client options and returns a list.

        :returns: list
        """
        pass

    @abc.abstractproperty
    def default_safe_files(self):  # pragma: no cover
        """
        Generate files to be preserved.

        :returns: list
        """
        pass

    @abc.abstractmethod
    def login_options(self, instance_name):  # pragma: no cover
        """
        Options used in the login command and returns a dict.

        :param instance_name: A string containing the instance to login to.
        :returns: dict
        """
        pass

    @abc.abstractmethod
    def ansible_connection_options(self, instance_name):  # pragma: no cover
        """
        Ansible specific connection options supplied to inventory and returns a \
        dict.

        :param instance_name: A string containing the instance to login to.
        :returns: dict
        """
        pass

    @abc.abstractmethod
    def sanity_checks(self):
        """
        Confirm that driver is usable.

        Sanity checks to ensure the driver can do work successfully. For
        example, when using the Docker driver, we want to know that the Docker
        daemon is running and we have the correct Docker Python dependency.
        Each driver implementation can decide what is the most stable sanity
        check for itself.

        :returns: None
        """
        pass

    @property
    def options(self):
        return self._config.config["driver"]["options"]

    @property
    def instance_config(self):
        return os.path.join(
            self._config.scenario.ephemeral_directory, "instance_config.yml"
        )

    @property
    def ssh_connection_options(self):
        if self._config.config["driver"]["ssh_connection_options"]:
            return self._config.config["driver"]["ssh_connection_options"]
        return self.default_ssh_connection_options

    @property
    def safe_files(self):
        return self.default_safe_files + self._config.config["driver"]["safe_files"]

    @property
    def delegated(self):
        """
        Is the driver delegated and returns a bool.

        :returns: bool
        """
        return self.name == "delegated"

    @property
    def managed(self):
        """
        Is the driver is managed and returns a bool.

        :returns: bool
        """
        return self.options["managed"]

    def status(self):
        """
        Collect the instances state and returns a list.

        .. important::

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
                    created=self._created(),
                    converged=self._converged(),
                )
            )

        return status_list

    def _get_ssh_connection_options(self):
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

    def _created(self):
        return str(self._config.state.created).lower()

    def _converged(self):
        return str(self._config.state.converged).lower()

    def __eq__(self, other):
        """Implement equality comparision."""
        # trick that allows us to test if a driver is loaded via:
        # if 'driver-name' in drivers()
        return str(self) == str(other)

    def __lt__(self, other):
        """Implement lower than comparison."""
        return str.__lt__(str(self), str(other))

    def __hash__(self):
        """Perform object hash."""
        return self.name.__hash__()

    def __str__(self):
        """Return readable string representation of object."""
        return self.name

    def __repr__(self):
        """Return detailed string representation of object."""
        return self.name

    def template_dir(self):

        p = os.path.join(self._path, "cookiecutter")

        if not os.path.isdir(p):
            p = os.path.abspath(
                os.path.join(
                    os.path.dirname(molecule.__file__),
                    "cookiecutter",
                    "scenario",
                    "driver",
                    self.name,
                )
            )
        return p

    def get_playbook(self, step):
        """Return embedded playbook location or None.

        The default location is relative to the file implementing the driver
        class, allowing driver writers to define playbooks without having
        to override this method.
        """
        p = os.path.join(self._path, "playbooks", step + ".yml",)
        if os.path.isfile(p):
            return p

    def modules_dir(self):
        """Return path to ansible modules included with driver."""
        p = os.path.join(self._path, "modules")
        if os.path.isdir(p):
            return p

    def reset(self):
        """Release all resources owned by molecule.

        This is a destructive operation that would affect all resources managed
        by molecule, regardless the scenario name.  Molecule will use metadata
        like labels or tags to annotate resources allocated by it.
        """
        pass

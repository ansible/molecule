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
"""Delegated Driver Module."""
from __future__ import annotations

import logging

from pathlib import Path
from typing import TYPE_CHECKING, Any

from molecule import util
from molecule.api import Driver
from molecule.data import __file__ as data_module


if TYPE_CHECKING:
    from molecule.config import Config


LOG = logging.getLogger(__name__)


class Delegated(Driver):
    r"""The class responsible for managing default instances.

    Delegated is the default driver used in Molecule.

    Under this driver, it is the developers responsibility to implement the
    create and destroy playbooks.  ``Managed`` is the default behavior of all
    drivers.

    ``` yaml
        driver:
          name: de
    ```

    However, the developer must adhere to the instance-config API. The
    developer's create playbook must provide the following instance-config
    data, and the developer's destroy playbook must reset the instance-config.

    ``` yaml

        - address: ssh_endpoint
          identity_file: ssh_identity_file  # mutually exclusive with password
          instance: instance_name
          port: ssh_port_as_string
          user: ssh_user
          shell_type: sh
          password: ssh_password  # mutually exclusive with identity_file
          become_method: valid_ansible_become_method  # optional
          become_pass: password_if_required  # optional

        - address: winrm_endpoint
          instance: instance_name
          connection: 'winrm'
          port: winrm_port_as_string
          user: winrm_user
          password: winrm_password
          shell_type: powershell
          winrm_transport: ntlm/credssp/kerberos
          winrm_cert_pem: <path to the credssp public certificate key>
          winrm_cert_key_pem: <path to the credssp private certificate key>
          winrm_server_cert_validation: validate/ignore
    ```

    This article covers how to configure and use WinRM with Ansible:
    https://docs.ansible.com/ansible/latest/user_guide/windows_winrm.html

    Molecule can also skip the provisioning/deprovisioning steps.  It is the
    developers responsibility to manage the instances, and properly configure
    Molecule to connect to said instances.

    ``` yaml
        driver:
          name: default
          options:
            managed: False
            login_cmd_template: 'docker exec -ti {instance} bash'
            ansible_connection_options:
              ansible_connection: docker
        platforms:
          - name: instance-docker
    ```

    ``` bash
        $ docker run \
            -d \
            --name instance-docker \
            --hostname instance-docker \
            -it molecule_local/ubuntu:latest sleep infinity & wait
    ```

    Use Molecule with delegated instances, which are accessible over ssh.

    !!! note

        It is the developer's responsibility to configure the ssh config file.

    ``` yaml
        driver:
          name: default
          options:
            managed: False
            login_cmd_template: 'ssh {instance} -F /tmp/ssh-config'
            ansible_connection_options:
              ansible_connection: ssh
              ansible_ssh_common_args: '-F /path/to/ssh-config'
        platforms:
          - name: instance
    ```

    Provide the files Molecule will preserve post ``destroy`` action.

    ``` yaml
        driver:
          name: default
          safe_files:
            - foo
    ```
    And in order to use localhost as molecule's target:

    ``` yaml
        driver:
          name: default
          options:
            managed: False
            ansible_connection_options:
              ansible_connection: local
    ```

    Attributes:
        title: Short description of the driver.
    """

    title = "Default driver, user is expected to manage provisioning of test resources."

    def __init__(self, config: Config) -> None:
        """Construct Delegated.

        Args:
            config: An instance of a Molecule config.
        """
        super().__init__(config)
        self._name = "default"

    @property
    def name(self) -> str:
        """Name of the driver.

        Returns:
            Name of the driver.
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Driver name setter.

        Args:
            value: New name of the driver.
        """
        self._name = value

    @property
    def login_cmd_template(self) -> str:
        """Get the login command template to be populated by ``login_options`` as a string.

        Returns:
            The login command template, if any.
        """
        if "login_cmd_template" in self.options:
            return self.options["login_cmd_template"]

        if self.managed:
            connection_options = " ".join(self.ssh_connection_options)

            return (
                "ssh {address} "
                "-l {user} "
                "-p {port} "
                "-i {identity_file} "
                f"{connection_options}"
            )
        return ""

    @property
    def default_safe_files(self) -> list[str]:
        """Generate files to be preserved.

        Returns:
            List of files to be preserved.
        """
        return []

    @property
    def default_ssh_connection_options(self) -> list[str]:
        """SSH client options.

        Returns:
            List of SSH connection options.
        """
        if self.managed:
            ssh_connopts = self._get_ssh_connection_options()
            if config_connopts := self.options.get("ansible_connection_options", {}).get(
                "ansible_ssh_common_args",
            ):
                ssh_connopts.append(
                    config_connopts,
                )
            return ssh_connopts
        return []

    def login_options(self, instance_name: str) -> dict[str, str]:
        """Login options.

        Args:
            instance_name: The name of the instance to look up login options for.

        Returns:
            Dictionary of options related to logging into the instance.
        """
        if self.managed:
            d = {"instance": instance_name}

            return util.merge_dicts(d, self._get_instance_config(instance_name))
        return {"instance": instance_name}

    def ansible_connection_options(
        self,
        instance_name: str,
    ) -> dict[str, str]:
        """Ansible connection options.

        Args:
            instance_name: The name of the instance to look up Ansible connection options for.

        Returns:
            Dictionary of options related to ansible connection to the instance.
        """
        # list of tuples describing mappable instance params and default values
        instance_params = [
            ("become_pass", None),
            ("become_method", False),
            ("winrm_transport", None),
            ("winrm_cert_pem", None),
            ("winrm_cert_key_pem", None),
            ("winrm_server_cert_validation", None),
            ("shell_type", None),
            ("connection", "smart"),
        ]
        if self.managed:
            try:
                d = self._get_instance_config(instance_name)
                conn_dict = {}
                # Check if optional mappable params are in the instance config
                for i in instance_params:
                    if d.get(i[0], i[1]):
                        conn_dict["ansible_" + i[0]] = d.get(i[0], i[1])

                conn_dict["ansible_user"] = d.get("user")
                conn_dict["ansible_host"] = d.get("address")
                conn_dict["ansible_port"] = d.get("port")

                if d.get("identity_file", None):
                    conn_dict["ansible_private_key_file"] = d.get("identity_file")
                if d.get("password", None):
                    conn_dict["ansible_password"] = d.get("password")
                    # Based on testinfra documentation, ansible password must be passed via ansible_ssh_pass  # noqa: E501
                    # issue to fix this can be found https://github.com/pytest-dev/pytest-testinfra/issues/580
                    conn_dict["ansible_ssh_pass"] = d.get("password")

                conn_dict["ansible_ssh_common_args"] = " ".join(
                    self.ssh_connection_options,
                )

                return conn_dict  # noqa: TRY300

            except StopIteration:
                return {}
            except OSError:
                # Instance has yet to be provisioned , therefore the
                # instance_config is not on disk.
                return {}
        return self.options.get("ansible_connection_options", {})

    def _created(self) -> str:
        if self.managed:
            return super()._created()
        return "unknown"

    def _get_instance_config(self, instance_name: str) -> dict[str, Any]:
        instance_config_dict = util.safe_load_file(self._config.driver.instance_config)

        return next(item for item in instance_config_dict if item["instance"] == instance_name)

    def sanity_checks(self) -> None:
        """Run sanity checks."""
        # Note(decentral1se): Cannot implement driver specifics are unknown

    def schema_file(self) -> str:
        """Return schema file path.

        Returns:
            Path to schema file.
        """
        return str(Path(data_module).parent / "driver.json")

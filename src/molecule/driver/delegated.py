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

import logging

from molecule import util
from molecule.api import Driver

LOG = logging.getLogger(__name__)


class Delegated(Driver):
    r"""
    The class responsible for managing delegated instances.

    Delegated is `not` the default driver used in Molecule.

    Under this driver, it is the developers responsibility to implement the
    create and destroy playbooks.  ``Managed`` is the default behaviour of all
    drivers.

    .. code-block:: yaml

        driver:
          name: delegated

    However, the developer must adhere to the instance-config API. The
    developer's create playbook must provide the following instance-config
    data, and the developer's destroy playbook must reset the instance-config.

    .. code-block:: yaml

        - address: ssh_endpoint
          identity_file: ssh_identity_file  # mutually exclusive with password
          instance: instance_name
          port: ssh_port_as_string
          user: ssh_user
          password: ssh_password  # mutually exclusive with identity_file
          become_method: valid_ansible_become_method  # optional
          become_pass: password_if_required  # optional

        - address: winrm_endpoint
          instance: instance_name
          connection: 'winrm'
          port: winrm_port_as_string
          user: winrm_user
          password: winrm_password
          winrm_transport: ntlm/credssp/kerberos
          winrm_cert_pem: <path to the credssp public certificate key>
          winrm_cert_key_pem: <path to the credssp private certificate key>
          winrm_server_cert_validation: validate/ignore

    This article covers how to configure and use WinRM with Ansible:
    https://docs.ansible.com/ansible/latest/user_guide/windows_winrm.html

    Molecule can also skip the provisioning/deprovisioning steps.  It is the
    developers responsibility to manage the instances, and properly configure
    Molecule to connect to said instances.

    .. code-block:: yaml

        driver:
          name: delegated
          options:
            managed: False
            login_cmd_template: 'docker exec -ti {instance} bash'
            ansible_connection_options:
              ansible_connection: docker
        platforms:
          - name: instance-docker

    .. code-block:: bash

        $ docker run \
            -d \
            --name instance-docker \
            --hostname instance-docker \
            -it molecule_local/ubuntu:latest sleep infinity & wait

    Use Molecule with delegated instances, which are accessible over ssh.

    .. important::

        It is the developer's responsibility to configure the ssh config file.

    .. code-block:: yaml

        driver:
          name: delegated
          options:
            managed: False
            login_cmd_template: 'ssh {instance} -F /tmp/ssh-config'
            ansible_connection_options:
              ansible_connection: ssh
              ansible_ssh_common_args: '-F /path/to/ssh-config'
        platforms:
          - name: instance

    Provide the files Molecule will preserve post ``destroy`` action.

    .. code-block:: yaml

        driver:
          name: delegated
          safe_files:
            - foo

    And in order to use localhost as molecule's target:

    .. code-block:: yaml

        driver:
          name: delegated
          options:
            managed: False
            ansible_connection_options:
              ansible_connection: local
    """

    def __init__(self, config=None):
        """Construct Delegated."""
        super(Delegated, self).__init__(config)
        self._name = "delegated"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def login_cmd_template(self):
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

    @property
    def default_safe_files(self):
        return []

    @property
    def default_ssh_connection_options(self):
        if self.managed:
            ssh_connopts = self._get_ssh_connection_options()
            if self.options.get("ansible_connection_options", {}).get(
                "ansible_ssh_common_args", None
            ):
                ssh_connopts.append(
                    self.options.get("ansible_connection_options").get(
                        "ansible_ssh_common_args"
                    )
                )
            return ssh_connopts
        return []

    def login_options(self, instance_name):
        if self.managed:
            d = {"instance": instance_name}

            return util.merge_dicts(d, self._get_instance_config(instance_name))
        return {"instance": instance_name}

    def ansible_connection_options(self, instance_name):
        if self.managed:
            try:
                d = self._get_instance_config(instance_name)
                conn_dict = {}
                conn_dict["ansible_user"] = d.get("user")
                conn_dict["ansible_host"] = d.get("address")
                conn_dict["ansible_port"] = d.get("port")
                if d.get("connection", None):
                    conn_dict["ansible_connection"] = d.get("connection", "smart")
                if d.get("become_method", False):
                    conn_dict["ansible_become_method"] = d.get("become_method")
                if d.get("become_pass", None):
                    conn_dict["ansible_become_pass"] = d.get("become_pass")
                if d.get("identity_file", None):
                    conn_dict["ansible_private_key_file"] = d.get("identity_file")
                    conn_dict["ansible_ssh_common_args"] = " ".join(
                        self.ssh_connection_options
                    )
                if d.get("password", None):
                    conn_dict["ansible_password"] = d.get("password")
                    # Based on testinfra documentation, ansible password must be passed via ansible_ssh_pass
                    # issue to fix this can be found https://github.com/pytest-dev/pytest-testinfra/issues/580
                    conn_dict["ansible_ssh_pass"] = d.get("password")
                if d.get("winrm_transport", None):
                    conn_dict["ansible_winrm_transport"] = d.get("winrm_transport")
                if d.get("winrm_cert_pem", None):
                    conn_dict["ansible_winrm_cert_pem"] = d.get("winrm_cert_pem")
                if d.get("winrm_cert_key_pem", None):
                    conn_dict["ansible_winrm_cert_key_pem"] = d.get(
                        "winrm_cert_key_pem"
                    )
                if d.get("winrm_server_cert_validation", None):
                    conn_dict["ansible_winrm_server_cert_validation"] = d.get(
                        "winrm_server_cert_validation"
                    )

                return conn_dict

            except StopIteration:
                return {}
            except IOError:
                # Instance has yet to be provisioned , therefore the
                # instance_config is not on disk.
                return {}
        return self.options.get("ansible_connection_options", {})

    def _created(self):
        if self.managed:
            return super(Delegated, self)._created()
        return "unknown"

    def _get_instance_config(self, instance_name):
        instance_config_dict = util.safe_load_file(self._config.driver.instance_config)

        return next(
            item for item in instance_config_dict if item["instance"] == instance_name
        )

    def sanity_checks(self):
        # Note(decentral1se): Cannot implement driver specifics are unknown
        pass

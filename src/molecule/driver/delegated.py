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

import json
import subprocess

from pathlib import Path
from typing import TYPE_CHECKING

from molecule import util
from molecule.api import Driver
from molecule.data import __file__ as data_module
from molecule.logger import get_logger


if TYPE_CHECKING:
    from typing import Any

    from molecule.config import Config


LOG = get_logger(__name__)


class Delegated(Driver):
    """The Default driver.

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
                f"ssh {{address}} -l {{user}} -p {{port}} -i {{identity_file}} {connection_options}"
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

            try:
                return util.merge_dicts(d, self._get_instance_config(instance_name))
            except (StopIteration, OSError):
                # instance_config.yml doesn't exist, or has no entry for
                # this instance - e.g. an ansible-native scenario (no
                # `platforms` declared), whose create playbook has no
                # obligation to populate it (mirrors
                # ansible_connection_options()'s own handling of this exact
                # case). Fall back to whatever the real ansible inventory
                # already has for this host - population of those vars is
                # up to the scenario/create playbook's own author, this
                # just reads what's already there instead of requiring a
                # second, molecule-specific copy of the same facts.
                return util.merge_dicts(d, self._get_inventory_login_options(instance_name))
        return {"instance": instance_name}

    def _ansible_inventory_args(self) -> list[str]:
        """Resolve the same --inventory sources ansible-playbook itself is invoked with.

        See AnsiblePlaybook.bake(): it always passes
        provisioner.inventory_directory, plus whatever extra
        --inventory/-i args are configured in provisioner.ansible_args /
        the top-level ansible_args. Reusing the exact same sources here
        means queries reflect exactly what ansible-playbook itself would
        see - no separate inventory config to keep in sync.

        Returns:
            List of `ansible-inventory` CLI arguments selecting the same
            inventory sources ansible-playbook uses.
        """
        extra_inventory_args = []
        if self._config.provisioner is None:
            return []
        source_args = (*self._config.provisioner.ansible_args, *self._config.ansible_args)
        take_next = False
        for arg in source_args:
            if take_next:
                extra_inventory_args.append(arg)
                take_next = False
            elif arg.startswith(("--inventory=", "-i=")):
                extra_inventory_args.append(arg)
            elif arg in ("--inventory", "-i"):
                extra_inventory_args.append(arg)
                take_next = True

        return [
            "--inventory",
            self._config.provisioner.inventory_directory,
            *extra_inventory_args,
        ]

    def _run_ansible_inventory(self, extra_args: list[str]) -> dict[str, Any] | None:
        """Run `ansible-inventory` against the resolved inventory sources.

        Args:
            extra_args: Additional ansible-inventory CLI arguments, e.g.
                ``["--host", name]`` or ``["--list"]``.

        Returns:
            The parsed JSON output, or None if the command failed for any
            reason (ansible-inventory not available, no matching host,
            malformed output, etc).
        """
        cmd = ["ansible-inventory", *extra_args, *self._ansible_inventory_args()]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
            return json.loads(result.stdout)  # type: ignore[no-any-return]
        except subprocess.CalledProcessError as exc:
            LOG.debug(
                "ansible-inventory %s failed (rc=%d): %s",
                " ".join(extra_args),
                exc.returncode,
                exc.stderr.strip() if exc.stderr else "(no stderr)",
            )
            return None
        except subprocess.TimeoutExpired:
            LOG.debug("ansible-inventory %s timed out after 30s", " ".join(extra_args))
            return None
        except (json.JSONDecodeError, OSError) as exc:
            LOG.debug("ansible-inventory %s failed: %s", " ".join(extra_args), exc)
            return None

    def _get_inventory_login_options(self, instance_name: str) -> dict[str, str]:
        """Resolve login options for an instance from the real ansible inventory.

        Used as a fallback when instance_config.yml has no entry for this
        instance (ansible-native scenarios have no obligation to write one).
        Reflects whatever the scenario's own create playbook already
        populated - e.g. via host_vars - with no separate bookkeeping
        required.

        Args:
            instance_name: The name of the instance to look up.

        Returns:
            Dictionary of options related to logging into the instance, or
            an empty dictionary if none could be resolved.
        """
        host_vars = self._run_ansible_inventory(["--host", instance_name])
        if host_vars is None:
            return {}

        d = {}
        if "ansible_host" in host_vars:
            d["address"] = host_vars["ansible_host"]
        if "ansible_user" in host_vars:
            d["user"] = host_vars["ansible_user"]
        if "ansible_port" in host_vars:
            d["port"] = host_vars["ansible_port"]
        if "ansible_ssh_private_key_file" in host_vars:
            d["identity_file"] = host_vars["ansible_ssh_private_key_file"]
        return d

    def get_ansible_native_hosts(self) -> list[str]:
        """List real host names from the configured inventory.

        For ansible-native scenarios (no `platforms` declared), molecule
        has no static list of instance names to fall back on - this
        queries the same inventory ansible-playbook itself would use and
        returns every host it defines, so `molecule list`/`molecule login`
        can work with real names instead of a blank placeholder / always
        requiring --host.

        Returns:
            Sorted list of host names found in the inventory, or an empty
            list if none could be resolved.
        """
        data = self._run_ansible_inventory(["--list"])
        if data is None:
            return []
        return sorted(data.get("_meta", {}).get("hostvars", {}).keys())

    def ansible_connection_options(
        self,
        instance_name: str,
    ) -> dict[str, Any]:
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
                    # Based on testinfra documentation, ansible password must be passed via ansible_ssh_pass
                    # issue to fix this can be found https://github.com/pytest-dev/pytest-testinfra/issues/580
                    conn_dict["ansible_ssh_pass"] = d.get("password")

                conn_dict["ansible_ssh_common_args"] = " ".join(
                    self.ssh_connection_options,
                )
            except StopIteration:
                return {}
            except OSError:
                # Instance has yet to be provisioned , therefore the
                # instance_config is not on disk.
                return {}
            else:
                return conn_dict

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

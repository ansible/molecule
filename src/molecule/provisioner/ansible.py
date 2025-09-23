#  Copyright (c) 2015-2018 Cisco Systems, Inc.

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
"""Ansible Provisioner Module."""

from __future__ import annotations

import collections
import copy
import os
import shutil

from pathlib import Path
from typing import TYPE_CHECKING

from ansible_compat.ports import cached_property

from molecule import logger, util
from molecule.constants import DEFAULT_ANSIBLE_CFG_OPTIONS, RC_SETUP_ERROR
from molecule.exceptions import MoleculeError
from molecule.provisioner import ansible_playbook, ansible_playbooks, base
from molecule.reporting.definitions import CompletionState


if TYPE_CHECKING:
    from typing import Any

    from molecule.types import Options

    Vivify = collections.defaultdict[str, Any | "Vivify"]


class Ansible(base.Base):
    """The Ansible provisioner."""

    @property
    def _log(self) -> logger.ScenarioLoggerAdapter:
        """Get a fresh scenario logger with current context.

        Returns:
            A scenario logger adapter with current scenario and step context.
        """
        # Get step context from the current action being executed
        step_name = getattr(self._config, "action", "provisioner")
        return logger.get_scenario_logger(__name__, self._config.scenario.name, step_name)

    @property
    def default_config_options(self) -> dict[str, Any]:
        """Provide default options to construct ansible.cfg.

        Returns:
            Default config options.
        """
        return DEFAULT_ANSIBLE_CFG_OPTIONS

    @property
    def default_options(self) -> dict[str, str | bool]:
        """Provide default options.

        Returns:
            Default options.
        """
        d: dict[str, str | bool] = {"skip-tags": "molecule-notest,notest"}

        if self._config.action == "idempotence":
            d["skip-tags"] += ",molecule-idempotence-notest"  # type: ignore[assignment, operator]

        if self._config.debug:
            d["vvv"] = True
            d["diff"] = True

        return d

    @property
    def default_env(self) -> dict[str, str]:
        """Provide default environment variables.

        Returns:
            Default set of environment variables.
        """
        env = util.merge_dicts(
            dict(os.environ),
            {
                "ANSIBLE_CONFIG": self.config_file,
            },
        )
        env = util.merge_dicts(env, self._config.env)
        return env  # noqa: RET504

    @property
    def name(self) -> str:
        """Provisioner name.

        Returns:
            The provisioner name.
        """
        return self._config.config["provisioner"]["name"]

    @property
    def ansible_args(self) -> list[str]:
        """Get ansible args from config file based on executor backend.

        If the executor is ansible-navigator, we need to combine the
        ansible_navigator args with the ansible_playbook args.
        For ansible-playbook, we only use the ansible_playbook args.

        Returns:
            List of ansible arguments from config file for the current executor.
        """
        ansible_config = self._config.config["ansible"]
        executor_config = ansible_config["executor"]
        backend = executor_config["backend"]

        # Get executor-specific args from config file only
        args_config = executor_config["args"]
        if backend == "ansible-navigator":
            playbook_args = args_config["ansible_playbook"]
            navigator_args = args_config["ansible_navigator"]
            # For navigator, we need both navigator args and playbook args (passed via --)
            return navigator_args + (["--", *playbook_args] if playbook_args else [])
        # For ansible-playbook, only use ansible_playbook args
        return args_config["ansible_playbook"]

    @property
    def config_options(self) -> dict[str, Any]:
        """Get ansible config options.

        Returns:
            The ansible config options.
        """
        return util.merge_dicts(
            self.default_config_options,
            self._config.config["ansible"]["cfg"],
        )

    @property
    def options(self) -> Options:
        """Appropriate options for provisioner.

        Returns:
            Dictionary of provisioner options.
        """
        if self._config.action in ["create", "destroy"]:
            return self.default_options

        opts = self._config.config["provisioner"]["options"]
        # NOTE(retr0h): Remove verbose options added by the user while in
        # debug.
        if self._config.debug:
            opts = util.filter_verbose_permutation(opts)

        return util.merge_dicts(self.default_options, opts)

    @property
    def env(self) -> dict[str, str]:
        """Full computed environment variables for provisioner.

        Returns:
            Complete set of collected environment variables.
        """
        default_env = self.default_env
        env = self._config.config["ansible"]["env"].copy()
        # ensure that all keys and values are strings
        env = {str(k): str(v) for k, v in env.items()}
        return util.merge_dicts(default_env, env)

    @property
    def hosts(self) -> dict[str, str]:
        """Provisioner inventory hosts.

        Returns:
            Dictionary of host names.
        """
        return self._config.config["provisioner"]["inventory"]["hosts"]

    @property
    def host_vars(self) -> dict[str, str]:
        """Provisioner inventory host vars.

        Returns:
            Dictionary of host vars.
        """
        return self._config.config["provisioner"]["inventory"]["host_vars"]

    @property
    def group_vars(self) -> dict[str, str]:
        """Provisioner inventory group vars.

        Returns:
            Dictionary of group vars.
        """
        return self._config.config["provisioner"]["inventory"]["group_vars"]

    @property
    def links(self) -> dict[str, str]:
        """Provisioner inventory links.

        Returns:
            Dictionary of links.
        """
        return self._config.config["provisioner"]["inventory"]["links"]

    @property
    def inventory(self) -> dict[str, Any]:
        """Create an inventory structure and returns a dict.

        ``` yaml
            ungrouped:
              vars:
                foo: bar
              hosts:
                instance-1:
                instance-2:
              children:
                $child_group_name:
                  hosts:
                    instance-1:
                    instance-2:
            $group_name:
              hosts:
                instance-1:
                  ansible_connection: docker
                instance-2:
                  ansible_connection: docker
        ```
        """
        dd = self._vivify()

        # Always ensure basic inventory structure with molecule vars
        molecule_vars = {
            "molecule_file": "{{ lookup('env', 'MOLECULE_FILE') }}",
            "molecule_ephemeral_directory": "{{ lookup('env', 'MOLECULE_EPHEMERAL_DIRECTORY') }}",
            "molecule_scenario_directory": "{{ lookup('env', 'MOLECULE_SCENARIO_DIRECTORY') }}",
            "molecule_yml": "{{ lookup('file', molecule_file) | from_yaml }}",
            "molecule_instance_config": "{{ lookup('env', 'MOLECULE_INSTANCE_CONFIG') }}",
            "molecule_no_log": "{{ lookup('env', 'MOLECULE_NO_LOG') or not "
            "molecule_yml.provisioner.log|default(False) | bool }}",
        }

        # Initialize basic groups even if no platforms exist
        dd["all"]["vars"] = molecule_vars
        dd["ungrouped"]["vars"] = {}

        for platform in self._config.platforms.instances:
            for group in platform.get("groups", ["ungrouped"]):
                instance_name = platform["name"]
                connection_options = self.connection_options(instance_name)

                # All group
                dd["all"]["hosts"][instance_name] = connection_options
                # Named group
                dd[group]["hosts"][instance_name] = connection_options
                dd[group]["vars"] = molecule_vars
                # Children
                for child_group in platform.get("children", []):
                    dd[group]["children"][child_group]["hosts"][instance_name] = connection_options

        return self._default_to_regular(dd)

    @property
    def inventory_directory(self) -> str:
        """Inventory directory path.

        Returns:
            Path to the directory containing inventory files.
        """
        return self._config.scenario.inventory_directory

    @property
    def inventory_file(self) -> str:
        """Inventory file path.

        Returns:
            Path to ansible_inventory.yml
        """
        return str(Path(self.inventory_directory, "ansible_inventory.yml"))

    @property
    def config_file(self) -> str:
        """Configuration file path.

        Returns:
            Path to ansible.cfg.
        """
        return str(
            Path(
                self._config.scenario.ephemeral_directory,
                "ansible.cfg",
            ),
        )

    @cached_property
    def playbooks(self) -> ansible_playbooks.AnsiblePlaybooks:
        """Ansible playbooks provisioner instance.

        Returns:
            AnsiblePlaybooks instance based on this config.
        """
        return ansible_playbooks.AnsiblePlaybooks(self._config)

    @property
    def directory(self) -> str:
        """Ansible provisioner directory.

        Returns:
            Path to the ansible provisioner directory.
        """
        return str(Path(__file__).parent.parent.parent / "molecule" / "provisioner" / "ansible")

    def cleanup(self) -> None:
        """Execute `ansible-playbook` against the cleanup playbook and returns None."""
        pb = self._get_ansible_playbook(self.playbooks.cleanup)
        pb.execute()

    def connection_options(
        self,
        instance_name: str,
    ) -> dict[str, Any]:
        """Computed connection options combining instance and provisioner options.

        Args:
            instance_name: The instance to base the connection options on.

        Returns:
            The combined connection options.
        """
        d = self._config.driver.ansible_connection_options(instance_name)

        return util.merge_dicts(
            d,
            self._config.config["provisioner"]["connection_options"],
        )

    def check(self) -> None:
        """Execute ``ansible-playbook`` against the converge playbook with the ``--check`` flag."""
        pb = self._get_ansible_playbook(self.playbooks.converge)
        pb.add_cli_arg("check", value=True)
        pb.execute()

    def converge(self, playbook: str = "", **kwargs: object) -> str:
        """Execute ``ansible-playbook`` against the converge playbook. unless specified otherwise.

        Args:
            playbook: An optional string containing an absolute path to a playbook.
            **kwargs: An optional keyword arguments.

        Returns:
            str: The output from the ``ansible-playbook`` command.
        """
        pb = self._get_ansible_playbook(playbook or self.playbooks.converge, **kwargs)  # type: ignore[arg-type]

        return pb.execute()

    def destroy(self) -> None:
        """Execute ``ansible-playbook`` against the destroy playbook and returns None."""
        pb = self._get_ansible_playbook(self.playbooks.destroy)
        pb.execute()

    def side_effect(self, action_args: list[str] | None = None) -> None:
        """Execute ``ansible-playbook`` against the side_effect playbook.

        Args:
            action_args: Arguments to pass to the side_effect playbook.
        """
        playbooks = []
        if action_args:
            playbooks = [
                self._get_ansible_playbook(self.abs_path(playbook)) for playbook in action_args
            ]
        else:
            playbooks = [self._get_ansible_playbook(self.playbooks.side_effect)]
        for pb in playbooks:
            pb.execute()

    def create(self) -> None:
        """Execute ``ansible-playbook`` against the create playbook and returns None."""
        pb = self._get_ansible_playbook(self.playbooks.create)
        pb.execute()

    def prepare(self) -> None:
        """Execute ``ansible-playbook`` against the prepare playbook and returns None."""
        pb = self._get_ansible_playbook(self.playbooks.prepare)
        pb.execute()

    def syntax(self) -> None:
        """Execute `ansible-playbook` against the converge playbook with the -syntax-check flag."""
        pb = self._get_ansible_playbook(self.playbooks.converge)
        pb.add_cli_arg("syntax-check", value=True)
        pb.execute()

    def verify(self, action_args: list[str] | None = None) -> None:
        """Execute ``ansible-playbook`` against the verify playbook.

        Args:
            action_args: Arguments to pass on to the verify playbook.
        """
        playbooks = []
        if action_args:
            playbooks = [self.abs_path(playbook) for playbook in action_args]
        elif self.playbooks.verify:
            playbooks = [self.playbooks.verify]
        if not playbooks:
            message = "Missing playbook"
            note = f"Remove from {self._config.subcommand}_sequence to suppress"
            self._config.scenario.results.add_completion(
                CompletionState.missing(message=message, note=note),
            )
            return
        for playbook in playbooks:
            # Get ansible playbooks for `verify` instead of `provision`
            pb = self._get_ansible_playbook(playbook, verify=True)
            pb.execute()

    def write_config(self) -> None:
        """Write the provisioner's config file to disk and returns None."""
        template = util.render_template(
            self._get_config_template(),
            config_options=self.config_options,
        )
        util.write_file(self.config_file, template)

    def manage_inventory(self) -> None:
        """Manage inventory for Ansible and returns None."""
        self._write_inventory()
        self._remove_vars()
        if not self.links:
            self._add_or_update_vars()
        else:
            self._link_or_update_vars()

    def abs_path(self, path: str | Path) -> str:
        """Return absolute scenario-adjacent path.

        Args:
            path: Scenario-adjacent relative path.

        Returns:
            Absolute path.
        """
        path = Path(self._config.scenario.directory) / path
        return str(util.abs_path(path))

    def _add_or_update_vars(self) -> None:
        """Create host and/or group vars and returns None."""
        # Create the hosts extra inventory source (only if not empty)
        hosts_file = os.path.join(self.inventory_directory, "hosts")  # noqa: PTH118
        if self.hosts:
            util.write_file(hosts_file, util.safe_dump(self.hosts))
        # Create the host_vars and group_vars directories
        for target in ["host_vars", "group_vars"]:
            if target == "host_vars":
                vars_target = copy.deepcopy(self.host_vars)
                for instance_name in self.host_vars.keys():  # noqa: SIM118
                    instance_key = instance_name
                    vars_target[instance_key] = vars_target.pop(instance_name)

            elif target == "group_vars":
                vars_target = self.group_vars

            if vars_target:
                target_vars_directory = util.abs_path(Path(self.inventory_directory) / target)
                if not target_vars_directory.is_dir():
                    target_vars_directory.mkdir()

                for target in vars_target:  # noqa: PLW2901
                    target_var_content = vars_target[target]
                    path = target_vars_directory / target
                    util.write_file(path, util.safe_dump(target_var_content))

    def _write_inventory(self) -> None:
        """Write the provisioner's inventory file to disk and returns None."""
        self._verify_inventory()

        util.write_file(self.inventory_file, util.safe_dump(self.inventory))

    def _remove_vars(self) -> None:
        """Remove hosts/host_vars/group_vars and returns None."""
        for name in ("hosts", "group_vars", "host_vars"):
            d = os.path.join(self.inventory_directory, name)  # noqa: PTH118
            if os.path.islink(d) or os.path.isfile(d):  # noqa: PTH113, PTH114
                os.unlink(d)  # noqa: PTH108
            elif os.path.isdir(d):  # noqa: PTH112
                shutil.rmtree(d)

    def _link_or_update_vars(self) -> None:
        """Create or updates the symlink to group_vars and returns None.

        Raises:
            MoleculeError: if source file does not exist.
        """
        for d, source in self.links.items():
            target = os.path.join(self.inventory_directory, d)  # noqa: PTH118
            source = os.path.join(self._config.scenario.directory, source)  # noqa: PTH118, PLW2901

            if not os.path.exists(source):  # noqa: PTH110
                msg = f"The source path '{source}' does not exist."
                raise MoleculeError(msg)
            if os.path.exists(target):  # noqa: PTH110
                if os.path.realpath(target) == os.path.realpath(source):
                    msg = f"Required symlink {target} to {source} exist, skip creation"
                    self._log.debug(msg)
                    continue
                msg = f"Required symlink {target} exist with another source"
                self._log.debug(msg)
                os.remove(target)  # noqa: PTH107
            msg = f"Inventory {source} linked to {target}"
            self._log.debug(msg)
            os.symlink(source, target)  # noqa: PTH211

    def _get_ansible_playbook(
        self,
        playbook: str | None,
        verify: bool = False,  # noqa: FBT001, FBT002
        **kwargs: object,
    ) -> ansible_playbook.AnsiblePlaybook:
        """Get an instance of AnsiblePlaybook and returns it.

        Args:
            playbook: A string containing an absolute path to a provisioner's playbook.
            verify: An optional bool to toggle the Playbook mode between provision and verify.
                False: provision; True: verify. Default is False.
            **kwargs: An optional keyword arguments.

        Returns:
            An AnsiblePlaybook object.
        """
        return ansible_playbook.AnsiblePlaybook(
            playbook,
            self._config,
            verify=verify,
            **kwargs,
        )

    def _verify_inventory(self) -> None:
        """Verify the inventory is valid and returns None.

        Check if a specific platform was requested but doesn't exist.
        The inventory property always returns a minimal valid structure
        regardless of the platforms defined in the molecule.yml file.
        """
        if self._config.platform_name is not None and not self._config.platforms.instances:
            msg = "Instances missing from the 'platform' section of molecule.yml."
            util.sysexit_with_message(msg, code=RC_SETUP_ERROR)

    def _get_config_template(self) -> str:
        """Return a config template string.

        Returns:
            str
        """
        return """
{% for section, section_dict in config_options.items() -%}
[{{ section }}]
{% for k, v in section_dict.items() -%}
{{ k }} = {{ v }}
{% endfor -%}
{% endfor -%}
""".strip()

    def _vivify(self) -> Vivify:
        """Return an autovivification default dict.

        Returns:
            A defaultdict whose default value is other defaultdict objects (and so on).
        """
        return collections.defaultdict(self._vivify)

    def _default_to_regular(
        self,
        d: dict[str, Any] | collections.defaultdict[str, Any],
    ) -> dict[str, Any]:
        if isinstance(d, collections.defaultdict):
            d = {k: self._default_to_regular(v) for k, v in d.items()}

        return d

    def _get_plugin_directory(self) -> str:
        return os.path.join(self.directory, "plugins")  # noqa: PTH118

    def _absolute_path_for(self, env: dict[str, str], key: str) -> str:
        return ":".join([self.abs_path(p) for p in env[key].split(":")])

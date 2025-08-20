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
"""Config Module."""

from __future__ import annotations

import copy
import os
import warnings

from pathlib import Path
from typing import TYPE_CHECKING, Any, cast
from uuid import uuid4

import click

from ansible_compat.ports import cache, cached_property

from molecule import api, interpolation, logger, platforms, scenario, state, util
from molecule.app import get_app
from molecule.constants import DEFAULT_CONFIG, ENV_VAR_CONFIG_MAPPING
from molecule.data import __file__ as data_module
from molecule.dependency import ansible_galaxy, shell
from molecule.model import schema_v3
from molecule.provisioner import ansible
from molecule.util import boolean, sysexit_with_message


if TYPE_CHECKING:
    from collections.abc import MutableMapping
    from typing import Literal

    from packaging.version import Version

    from molecule.dependency.base import Base as Dependency
    from molecule.driver.base import Driver
    from molecule.state import State
    from molecule.types import (
        CollectionData,
        CommandArgs,
        ConfigData,
        MoleculeArgs,
    )
    from molecule.verifier.base import Verifier


MOLECULE_PARALLEL: bool = boolean(os.environ.get("MOLECULE_PARALLEL", ""), default=False)
MOLECULE_DEBUG: bool = boolean(os.environ.get("MOLECULE_DEBUG", "False"), default=False)
MOLECULE_VERBOSITY: int = int(os.environ.get("MOLECULE_VERBOSITY", "0"))
MOLECULE_DIRECTORY = "molecule"
MOLECULE_FILE = "molecule.yml"
MOLECULE_KEEP_STRING = "MOLECULE_"
DEFAULT_DRIVER = "default"

MOLECULE_EMBEDDED_DATA_DIR = os.path.dirname(data_module)  # noqa: PTH120


@cache
def ansible_version() -> Version:
    """Retrieve Ansible version.

    Returns:
        Molecule version information.
    """
    warnings.warn(  # noqa: B028
        "molecule.config.ansible_version is deprecated, will be removed in the future.",
        category=DeprecationWarning,
    )
    return get_app(Path()).runtime.version


class Config:
    """Config Class.

    Molecule searches the current directory for ``molecule.yml`` files by
    globbing `molecule/*/molecule.yml`.  The files are instantiated into
    a list of Molecule [molecule.config.Config][] objects, and each Molecule subcommand
    operates on this list.

    The directory in which the ``molecule.yml`` resides is the Scenario's
    directory.  Molecule performs most functions within this directory.

    The [molecule.config.Config][] object instantiates Dependency, Driver,
    Platforms, Provisioner, Verifier_,
    [scenario][], and State_ references.
    """

    # pylint: disable=too-many-instance-attributes
    # Config objects should be allowed to have any number of attributes
    def __init__(
        self,
        molecule_file: str,  # pylint: disable=redefined-outer-name
        args: MoleculeArgs = {},  # noqa: B006
        command_args: CommandArgs = {},  # noqa: B006
        ansible_args: tuple[str, ...] = (),
    ) -> None:
        """Initialize a new config class and returns None.

        Args:
            molecule_file: A string containing the path to the Molecule file to be parsed.
            args: An optional dict of options, arguments and commands from the CLI.
            command_args: An optional dict of options passed to the subcommand from the CLI.
            ansible_args: An optional tuple of arguments provided to the `ansible-playbook` command.
        """
        self.molecule_file = molecule_file
        self.args = args
        self.command_args = command_args
        self.ansible_args = ansible_args
        self.config = self._get_config()
        self._action: str | None = None
        self._run_uuid = str(uuid4())
        self.project_directory = os.getenv(
            "MOLECULE_PROJECT_DIRECTORY",
            os.getcwd(),  # noqa: PTH109
        )
        self.app = get_app(Path(self.project_directory))
        self.runtime = self.app.runtime
        self.scenario_path = Path(molecule_file).parent

        # Former after_init() contents
        self.config = self._reget_config()
        self._apply_env_overrides()
        self._apply_cli_overrides()
        if self.molecule_file:
            self._validate()

    def write(self) -> None:
        """Write config file to filesystem."""
        util.write_file(self.config_file, util.safe_dump(self.config))

    def _apply_cli_overrides(self) -> None:
        """Apply CLI argument overrides to config.

        This method modifies the config dictionary to include CLI overrides,
        creating a single source of truth for configuration values.
        """
        # Apply shared_state CLI override ONLY if it was explicitly provided via CLI
        ctx = click.get_current_context(silent=True)
        if "shared_state" not in self.command_args or ctx is None:
            return
        source = ctx.get_parameter_source("shared_state")
        if source == click.core.ParameterSource.COMMANDLINE:
            self.config["shared_state"] = self.command_args["shared_state"]

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to command_args.

        Precedence: defaults → env vars → CLI args.
        Only applies env vars if the CLI argument wasn't set by the user.
        Includes variables from both os.environ and env_file.
        """
        ctx = click.get_current_context(silent=True)
        if ctx is None or not ENV_VAR_CONFIG_MAPPING or not hasattr(self, "command_args"):
            return

        # Build merged environment (os.environ + env_file) same as _reget_config
        merged_env = util.merge_dicts(os.environ, self.env)
        merged_env = set_env_from_file(merged_env, self.env_file)

        for env_var, config in ENV_VAR_CONFIG_MAPPING.items():
            env_value = merged_env.get(env_var)
            if env_value is None:
                continue

            config_attr, expected_type = config["attr"], config["type"]

            source = ctx.get_parameter_source(config_attr)
            if source == click.core.ParameterSource.COMMANDLINE:
                continue

            try:
                converted_value = (
                    boolean(env_value) if expected_type is bool else expected_type(env_value)
                )
                self.command_args[config_attr] = converted_value
            except (ValueError, TypeError):
                msg = f"Invalid value for {env_var}: {env_value}, ignoring"
                self._log.warning(msg)

    @property
    def config_file(self) -> str:
        """Path to the config file.

        Returns:
            The path to the config file.
        """
        path = Path(self.scenario.ephemeral_directory) / MOLECULE_FILE
        return str(path)

    @property
    def is_parallel(self) -> bool:
        """Is molecule in parallel mode.

        Returns:
            Whether molecule is in parallel mode.
        """
        return self.command_args.get("parallel", False)

    @property
    def shared_state(self) -> bool:
        """Should molecule share ephemeral state.

        Returns:
            Whether molecule should share ephemeral state.
        """
        return self.config.get("shared_state", False)

    @property
    def command_borders(self) -> bool:
        """Return if command borders are enabled."""
        return self.command_args.get("command_borders", False)

    @property
    def platform_name(self) -> str | None:
        """Configured platform.

        Returns:
            The name of the platform plugin specified.
        """
        return self.command_args.get("platform_name", None)

    @property
    def debug(self) -> bool:
        """Is molecule in debug mode.

        Returns:
            Whether molecule is in debug mode.
        """
        return self.args.get("debug", MOLECULE_DEBUG)

    @property
    def env_file(self) -> str | None:
        """Return path to env file.

        Returns:
            Path to configured env file.
        """
        return util.abs_path(self.args.get("env_file"))

    @property
    def subcommand(self) -> str:
        """Subcommand in use.

        Returns:
            The current subcommand being run.
        """
        return self.command_args["subcommand"]

    @property
    def action(self) -> str | None:
        """Action value.

        Returns:
            The value of action.
        """
        return self._action

    @action.setter
    def action(self, value: str) -> None:
        """Action setter.

        Args:
            value: New value for action.
        """
        self._action = value

    @property
    def cache_directory(
        self,
    ) -> Literal["molecule", "molecule_parallel"]:
        """Proper cache directory to use.

        Returns:
            Either "molecule" or "molecule_parallel" if in parallel mode.
        """
        return "molecule_parallel" if self.is_parallel else "molecule"

    @property
    def collection_directory(self) -> Path | None:
        """Location of collection containing the molecule files.

        Returns:
            Root of the collection containing the molecule files, only if galaxy.yml is valid.
        """
        collection_dir, collection_data = util.get_collection_metadata()
        return collection_dir if collection_data else None

    @property
    def molecule_directory(self) -> str:
        """Molecule directory for this project.

        Returns:
            The appropriate molecule directory for this project.
        """
        return molecule_directory(self.project_directory)

    @cached_property
    def collection(self) -> CollectionData | None:
        """Collection metadata sourced from galaxy.yml.

        Returns:
            A dictionary of information about the collection molecule is running inside, if any.
            Only returns collection data when galaxy.yml is valid with required fields.
        """
        _collection_directory, collection_data = util.get_collection_metadata()
        return collection_data

    @cached_property
    def dependency(self) -> Dependency | None:
        """Dependency manager in use.

        Returns:
            Instance of a molecule dependency plugin.
        """
        dependency_name = self.config["dependency"]["name"]
        if dependency_name == "galaxy":
            return ansible_galaxy.AnsibleGalaxy(self)
        if dependency_name == "shell":
            return shell.Shell(self)
        return None

    @cached_property
    def driver(self) -> Driver:
        """Return driver.

        Returns:
            The driver for this scenario.
        """
        driver_name = self._get_driver_name()
        driver = None

        api_drivers = api.drivers(config=self)
        if driver_name not in api_drivers:
            msg = f"Failed to find driver {driver_name}. Please ensure that the driver is correctly installed."
            sysexit_with_message(msg, code=1)

        driver = api_drivers[driver_name]
        driver.name = driver_name

        return driver

    @property
    def executor(self) -> str:
        """Return playbook executor.

        Returns:
            The executor backend.
        """
        return self.config["ansible"]["executor"]["backend"]

    @property
    def env(self) -> dict[str, str]:
        """Environment variables.

        Returns:
            Total set of computed environment variables.
        """
        return {
            "MOLECULE_DEBUG": str(self.debug),
            "MOLECULE_FILE": self.config_file,
            "MOLECULE_ENV_FILE": str(self.env_file),
            "MOLECULE_STATE_FILE": self.state.state_file,
            "MOLECULE_INVENTORY_FILE": self.provisioner.inventory_file,  # type: ignore[union-attr]
            "MOLECULE_EPHEMERAL_DIRECTORY": self.scenario.ephemeral_directory,
            "MOLECULE_SCENARIO_DIRECTORY": self.scenario.directory,
            "MOLECULE_PROJECT_DIRECTORY": self.project_directory,
            "MOLECULE_INSTANCE_CONFIG": self.driver.instance_config,
            "MOLECULE_DEPENDENCY_NAME": self.dependency.name,  # type: ignore[union-attr]
            "MOLECULE_DRIVER_NAME": self.driver.name,
            "MOLECULE_PROVISIONER_NAME": self.provisioner.name,  # type: ignore[union-attr]
            "MOLECULE_SCENARIO_NAME": self.scenario.name,
            "MOLECULE_VERIFIER_NAME": self.verifier.name,
            "MOLECULE_VERIFIER_TEST_DIRECTORY": self.verifier.directory,
        }

    @cached_property
    def platforms(self) -> platforms.Platforms:
        """Platforms for this run.

        Returns:
            A molecule Platforms instance.
        """
        return platforms.Platforms(
            self,
            parallelize_platforms=self.is_parallel,
            platform_name=self.platform_name,
        )

    @cached_property
    def provisioner(self) -> ansible.Ansible | None:
        """Provisioner for this run.

        Returns:
            An instance of the Ansible provisioner.
        """
        provisioner_name = self.config["provisioner"]["name"]
        if provisioner_name == "ansible":
            return ansible.Ansible(self)
        return None

    @cached_property
    def scenario(self) -> scenario.Scenario:
        """Scenario for this run.

        Returns:
            A molecule Scenario instance.
        """
        return scenario.Scenario(self)

    @property
    def _log(self) -> logger.ScenarioLoggerAdapter:
        """Get a scenario logger with config step context.

        Returns:
            A scenario logger adapter with current scenario and step context.
        """
        return logger.get_scenario_logger(__name__, self.scenario.name, "config")

    @cached_property
    def state(self) -> State:
        """Molecule state object.

        Returns:
            A molecule State instance.
        """
        my_state = state.State(self)

        # look at state file for molecule.yml date modified and warn if they do not match
        if self.molecule_file and os.path.isfile(self.molecule_file):  # noqa: PTH113
            modTime = os.path.getmtime(self.molecule_file)  # noqa: PTH204, N806
            if my_state.molecule_yml_date_modified is None:
                my_state.change_state("molecule_yml_date_modified", modTime)
            elif my_state.molecule_yml_date_modified != modTime:
                self._log.warning(
                    "The scenario config file ('%s') has been modified since the scenario was created. "
                    "If recent changes are important, reset the scenario with 'molecule destroy' to clean up created items or "
                    "'molecule reset' to clear current configuration.",
                    self.molecule_file,
                )

        return state.SharedState(self) if self.shared_state else state.State(self)

    @cached_property
    def verifier(self) -> Verifier:
        """Retrieve current verifier.

        Raises:
            RuntimeError: If is not able to find the driver.

        Returns:
            Instance of Verifier driver.
        """
        name = self.config["verifier"]["name"]
        if name not in api.verifiers(self):
            msg = f"Unable to find '{name}' verifier driver."
            raise RuntimeError(msg)
        return api.verifiers(self)[name]

    def _get_driver_name(self) -> str:
        # the state file contains the driver from the last run
        driver_from_state_file = self.state.driver
        # the user may supply a driver on the command line
        driver_from_cli = self.command_args.get("driver_name")
        # the driver may also be edited in the scenario
        driver_from_scenario = self.config["driver"]["name"]

        if driver_from_state_file:
            driver_name = driver_from_state_file
        elif driver_from_cli:
            driver_name = driver_from_cli
        else:
            driver_name = driver_from_scenario
        if driver_name is None:
            driver_name = "default"

        if driver_from_cli and (driver_from_cli != driver_name):
            msg = (
                f"Instance(s) were created with the '{driver_name}' driver, but the "
                f"subcommand is using '{driver_from_cli}' driver."
            )
            sysexit_with_message(msg, code=1)

        if driver_from_state_file and driver_name not in api.drivers():
            msg = (
                f"Driver '{driver_name}' from state-file "
                f"'{self.state.state_file}' is not available."
            )
            sysexit_with_message(msg, code=1)

        if driver_from_scenario != driver_name:
            msg = (
                f"Driver '{driver_name}' is currently in use but the scenario config "
                f"has changed and now defines '{driver_from_scenario}'. "
                "To change drivers, run 'molecule destroy' for converged scenarios or 'molecule reset' otherwise."
            )
            self._log.warning(msg)

        return driver_name

    def _get_config(self) -> ConfigData:
        """Perform a prioritized recursive merge of config files.

        Returns a new dict.  Prior to merging the config files are interpolated with
        environment variables.

        Returns:
            dict: The merged config.
        """
        return self._combine(keep_string=MOLECULE_KEEP_STRING)

    def _reget_config(self) -> ConfigData:
        """Perform the same prioritized recursive merge from `get_config`.

        Interpolates the ``keep_string`` left behind in the original
        ``get_config`` call.  This is probably __very__ bad.

        Returns:
            dict: The merged config.
        """
        env = util.merge_dicts(os.environ, self.env)
        env = set_env_from_file(env, self.env_file)

        return self._combine(env=env)

    def _combine(
        self,
        env: MutableMapping[str, str] = os.environ,
        keep_string: str | None = None,
    ) -> ConfigData:
        """Get configuration with complete migration flow.

        This single function handles the entire config resolution:
        1. Get forward-looking defaults
        2. Load and interpolate user config files
        3. Migrate legacy keys in user config
        4. Merge migrated user config on top of defaults

        Args:
            env: The current set of environment variables to consider.
            keep_string: String to avoid templating.

        Returns:
            dict: The merged config.
        """
        # Step 1: Get forward-looking defaults
        defaults = self._get_defaults()

        # Step 2: Load all user config files into a list of tuples (filename, config)
        user_config_files: list[tuple[str, dict[str, Any]]] = []

        # Load base configs
        base_configs = filter(os.path.exists, self.args.get("base_config", []))
        for base_config in base_configs:
            with open(base_config) as stream:  # noqa: PTH123
                s = stream.read()
                interpolated_config = self._interpolate(s, env, keep_string)
                config_data = util.safe_load(interpolated_config)
                user_config_files.append((base_config, config_data))

        # Load molecule.yml
        if self.molecule_file:
            with open(self.molecule_file) as stream:  # noqa: PTH123
                s = stream.read()
                interpolated_config = self._interpolate(s, env, keep_string)
                config_data = util.safe_load(interpolated_config)
                user_config_files.append((self.molecule_file, config_data))

        # Step 3: Debug log legacy keys that will be migrated
        legacy_keys = ["ansible_args", "config_options", "env", "playbooks"]
        for file_name, config_data in user_config_files:
            provisioner = config_data.get("provisioner", {})
            for key in legacy_keys:
                if key in provisioner:
                    # Use temporary logger since self._log isn't available during init
                    temp_log = logger.get_scenario_logger(__name__, "unknown", "config")
                    temp_log.debug(
                        f"provisioner.{key} found in {file_name}, this can be defined in ansible.{self._get_ansible_key_mapping(key)}",
                    )

        # Step 4: Merge all user configs in order (base configs first, molecule.yml last)
        merged_user_config: dict[str, Any] = {}
        for _file_name, config_data in user_config_files:
            merged_user_config = util.merge_dicts(merged_user_config, config_data)

        # Step 5: Migrate user config (legacy keys -> new ansible section)
        migrated_user_config = self._migrate_user_config(merged_user_config)

        # Step 6: Merge the migrated user config on top of defaults
        return util.merge_dicts(  # type: ignore[type-var]
            defaults,
            cast("ConfigData", migrated_user_config),
        )

    def _get_ansible_key_mapping(self, legacy_key: str) -> str:
        """Map legacy provisioner keys to their ansible section equivalents.

        Args:
            legacy_key: The legacy key name from provisioner section.

        Returns:
            The corresponding key path in ansible section.
        """
        mapping = {
            "ansible_args": "executor.args.ansible_playbook",
            "config_options": "cfg",
            "env": "env",
            "playbooks": "playbooks",
        }
        return mapping.get(legacy_key, legacy_key)

    def _migrate_user_config(self, user_config: dict[str, Any]) -> dict[str, Any]:
        """Migrate legacy provisioner keys to ansible section in user config.

        Migrates the keys defined in _get_ansible_key_mapping() from provisioner
        section to their corresponding locations in the ansible section.

        Args:
            user_config: Raw user configuration (may contain legacy keys)

        Returns:
            User config with legacy keys migrated to ansible section
        """
        # Work on a copy to avoid modifying input
        config = copy.deepcopy(user_config)

        provisioner = config.get("provisioner", {})
        legacy_keys = ["ansible_args", "config_options", "env", "playbooks"]

        # Check if migration is needed
        if not any(key in provisioner for key in legacy_keys):
            return config

        # Create ansible section if it doesn't exist
        if "ansible" not in config:
            config["ansible"] = {}
        ansible_config = config["ansible"]

        # Migrate ansible_args -> ansible.executor.args.ansible_playbook
        if "ansible_args" in provisioner:
            if "executor" not in ansible_config:
                ansible_config["executor"] = {}
            if "args" not in ansible_config["executor"]:
                ansible_config["executor"]["args"] = {}
            ansible_config["executor"]["args"]["ansible_playbook"] = provisioner["ansible_args"]
            del provisioner["ansible_args"]

        # Migrate config_options -> ansible.cfg
        if "config_options" in provisioner:
            ansible_config["cfg"] = provisioner["config_options"]
            del provisioner["config_options"]

        # Migrate env -> ansible.env
        if "env" in provisioner:
            ansible_config["env"] = provisioner["env"]
            del provisioner["env"]

        # Migrate playbooks -> ansible.playbooks
        if "playbooks" in provisioner:
            ansible_config["playbooks"] = provisioner["playbooks"]
            del provisioner["playbooks"]

        return config

    def _interpolate(
        self,
        stream: str,
        env: MutableMapping[str, str],
        keep_string: str | None,
    ) -> str:
        env = set_env_from_file(env, self.env_file)

        i = interpolation.Interpolator(interpolation.TemplateWithDefaults, env)

        try:
            return i.interpolate(stream, keep_string)
        except interpolation.InvalidInterpolation as e:
            msg = f"parsing config file '{self.molecule_file}'.\n\n{e.place}\n{e.string}"
            sysexit_with_message(msg, code=1)
        return ""

    def _get_defaults(self) -> ConfigData:
        """Get default configuration with forward-looking structure.

        Deepcopy here to avoid modifying the original DEFAULT_CONFIG.

        Returns:
            Default configuration from constants.
        """
        defaults = copy.deepcopy(DEFAULT_CONFIG)

        # Handle scenario name dynamically
        if not self.molecule_file:
            scenario_name = "default"
        else:
            scenario_name = (
                os.path.basename(os.path.dirname(self.molecule_file))  # noqa: PTH119, PTH120
                or "default"
            )

        defaults["scenario"]["name"] = scenario_name
        return defaults  # type: ignore[return-value]

    def _validate(self) -> None:
        """Validate molecule file."""
        # Use scenario logger with hardcoded values since scenario property isn't available yet
        scenario_name = self.config["scenario"]["name"]
        validation_log = logger.get_scenario_logger(__name__, scenario_name, "validate")

        msg = f"Validating schema {self.molecule_file}."
        validation_log.debug(msg)

        errors = schema_v3.validate(self.config)
        if errors:
            msg = f"Failed to validate {self.molecule_file}\n\n{errors}"
            sysexit_with_message(msg, code=1)


def molecule_directory(path: str | Path) -> str:
    """Return directory of the current scenario.

    Args:
        path: Base molecule directory.

    Returns:
        The current scenario's directory.
    """
    if isinstance(path, str):
        path = Path(path)
    return str(path / MOLECULE_DIRECTORY)


def molecule_file(path: str) -> str:
    """Return file path of current scenario.

    Args:
        path: Base molecule directory.

    Returns:
        The path to the molecule file.
    """
    return os.path.join(path, MOLECULE_FILE)  # noqa: PTH118


def set_env_from_file(
    env: MutableMapping[str, str],
    env_file: str | None,
) -> MutableMapping[str, str]:
    """Load environment from file.

    Args:
        env: Currently known environment variables.
        env_file: File from which to load more environment variables.

    Returns:
        The combined set of environment variables.
    """
    if env_file and os.path.exists(env_file):  # noqa: PTH110
        env = copy.copy(env)
        d = util.safe_load_file(env_file)
        for k, v in d.items():
            env[k] = v

        return env

    return env

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

import copy
import logging
import os
import warnings
from typing import MutableMapping
from uuid import uuid4

from ansible_compat.ports import cache, cached_property
from packaging.version import Version

from molecule import api, interpolation, platforms, scenario, state, util
from molecule.app import app
from molecule.dependency import ansible_galaxy, shell
from molecule.model import schema_v3
from molecule.provisioner import ansible
from molecule.util import boolean

LOG = logging.getLogger(__name__)
MOLECULE_DEBUG = boolean(os.environ.get("MOLECULE_DEBUG", "False"))
MOLECULE_VERBOSITY = int(os.environ.get("MOLECULE_VERBOSITY", 0))
MOLECULE_DIRECTORY = "molecule"
MOLECULE_FILE = "molecule.yml"
MOLECULE_KEEP_STRING = "MOLECULE_"
DEFAULT_DRIVER = "delegated"


@cache
def ansible_version() -> Version:
    """Retrieve Ansible version."""
    warnings.warn(
        "molecule.config.ansible_version is deprecated, will be removed in the future.",
        category=DeprecationWarning,
    )
    return app.runtime.version


# https://stackoverflow.com/questions/16017397/injecting-function-call-after-init-with-decorator  # noqa
class NewInitCaller(type):
    """NewInitCaller."""

    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        obj.after_init()
        return obj


class Config(object, metaclass=NewInitCaller):
    """
    Config Class.

    Molecule searches the current directory for ``molecule.yml`` files by
    globbing `molecule/*/molecule.yml`.  The files are instantiated into
    a list of Molecule :class:`.Config` objects, and each Molecule subcommand
    operates on this list.

    The directory in which the ``molecule.yml`` resides is the Scenario's
    directory.  Molecule performs most functions within this directory.

    The :class:`.Config` object instantiates Dependency_, Driver_,
    :ref:`lint`, Platforms_, Provisioner_, Verifier_,
    :ref:`root_scenario`, and State_ references.
    """

    # pylint: disable=too-many-instance-attributes
    # Config objects should be allowed to have any number of attributes
    def __init__(self, molecule_file: str, args={}, command_args={}, ansible_args=()):
        """
        Initialize a new config class and returns None.

        :param molecule_file: A string containing the path to the Molecule file
         to be parsed.
        :param args: An optional dict of options, arguments and commands from
         the CLI.
        :param command_args: An optional dict of options passed to the
         subcommand from the CLI.
        :param ansible_args: An optional tuple of arguments provided to the
         ``ansible-playbook`` command.
        :returns: None
        """
        self.molecule_file = molecule_file
        self.args = args
        self.command_args = command_args
        self.ansible_args = ansible_args
        self.config = self._get_config()
        self._action = None
        self._run_uuid = str(uuid4())
        self.project_directory = os.getenv("MOLECULE_PROJECT_DIRECTORY", os.getcwd())
        self.runtime = app.runtime

    def after_init(self):
        self.config = self._reget_config()
        if self.molecule_file:
            self._validate()

    def write(self) -> None:
        util.write_file(self.config_file, util.safe_dump(self.config))

    @property
    def ansible_collections_path(self):
        """Return collection path variable for current version of Ansible."""
        # https://github.com/ansible/ansible/pull/70007
        if self.runtime.version >= Version("2.10.0.dev0"):
            return "ANSIBLE_COLLECTIONS_PATH"
        else:
            return "ANSIBLE_COLLECTIONS_PATHS"

    @property
    def config_file(self):
        return os.path.join(self.scenario.ephemeral_directory, MOLECULE_FILE)

    @property
    def is_parallel(self):
        return self.command_args.get("parallel", False)

    @property
    def debug(self):
        return self.args.get("debug", MOLECULE_DEBUG)

    @property
    def env_file(self):
        return util.abs_path(self.args.get("env_file"))

    @property
    def subcommand(self):
        return self.command_args["subcommand"]

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        self._action = value

    @property
    def cache_directory(self):
        return "molecule_parallel" if self.is_parallel else "molecule"

    @property
    def molecule_directory(self):
        return molecule_directory(self.project_directory)

    @cached_property
    def dependency(self):
        dependency_name = self.config["dependency"]["name"]
        if dependency_name == "galaxy":
            return ansible_galaxy.AnsibleGalaxy(self)
        elif dependency_name == "shell":
            return shell.Shell(self)

    @cached_property
    def driver(self):
        driver_name = self._get_driver_name()
        driver = None

        driver = api.drivers(config=self)[driver_name]
        driver.name = driver_name

        return driver

    @property  # type: ignore
    def env(self):
        return {
            "MOLECULE_DEBUG": str(self.debug),
            "MOLECULE_FILE": self.config_file,
            "MOLECULE_ENV_FILE": str(self.env_file),
            "MOLECULE_STATE_FILE": self.state.state_file,
            "MOLECULE_INVENTORY_FILE": self.provisioner.inventory_file,
            "MOLECULE_EPHEMERAL_DIRECTORY": self.scenario.ephemeral_directory,
            "MOLECULE_SCENARIO_DIRECTORY": self.scenario.directory,
            "MOLECULE_PROJECT_DIRECTORY": self.project_directory,
            "MOLECULE_INSTANCE_CONFIG": self.driver.instance_config,
            "MOLECULE_DEPENDENCY_NAME": self.dependency.name,
            "MOLECULE_DRIVER_NAME": self.driver.name,
            "MOLECULE_PROVISIONER_NAME": self.provisioner.name,
            "MOLECULE_SCENARIO_NAME": self.scenario.name,
            "MOLECULE_VERIFIER_NAME": self.verifier.name,
            "MOLECULE_VERIFIER_TEST_DIRECTORY": self.verifier.directory,
        }

    @cached_property
    def lint(self):
        lint_name = self.config.get("lint", None)
        return lint_name

    @cached_property
    def platforms(self):
        return platforms.Platforms(self, parallelize_platforms=self.is_parallel)

    @cached_property
    def provisioner(self):
        provisioner_name = self.config["provisioner"]["name"]
        if provisioner_name == "ansible":
            return ansible.Ansible(self)

    @cached_property
    def scenario(self):
        return scenario.Scenario(self)

    @cached_property
    def state(self):
        return state.State(self)

    @cached_property
    def verifier(self):
        return api.verifiers(self).get(self.config["verifier"]["name"], None)

    def _get_driver_name(self):
        driver_from_state_file = self.state.driver
        driver_from_cli = self.command_args.get("driver_name")

        if driver_from_state_file:
            driver_name = driver_from_state_file
        elif driver_from_cli:
            driver_name = driver_from_cli
        else:
            driver_name = self.config["driver"]["name"]

        if driver_from_cli and (driver_from_cli != driver_name):
            msg = (
                f"Instance(s) were created with the '{driver_name}' driver, but the "
                f"subcommand is using '{driver_from_cli}' driver."
            )
            util.sysexit_with_message(msg)

        return driver_name

    def _get_config(self) -> MutableMapping:
        """
        Perform a prioritized recursive merge of config files.

        Returns a new dict.  Prior to merging the config files are interpolated with
        environment variables.

        :return: dict
        """
        return self._combine(keep_string=MOLECULE_KEEP_STRING)

    def _reget_config(self):
        """
        Perform the same prioritized recursive merge from `get_config`.

        Interpolates the ``keep_string`` left behind in the original
        ``get_config`` call.  This is probably __very__ bad.

        :return: dict
        """
        env = util.merge_dicts(os.environ, self.env)
        env = set_env_from_file(env, self.env_file)

        return self._combine(env=env)

    def _combine(self, env=os.environ, keep_string=None) -> MutableMapping:
        """
        Perform a prioritized recursive merge of config files.

        Returns a new dict.  Prior to merging the config files are interpolated with
        environment variables.

        1. Loads Molecule defaults.
        2. Loads a base config (if provided) and merges on top of defaults.
        3. Loads the scenario's ``molecule file`` and merges on top of previous
           merge.

        :return: dict
        """
        defaults = self._get_defaults()
        base_configs = filter(os.path.exists, self.args.get("base_config", []))
        for base_config in base_configs:
            with util.open_file(base_config) as stream:
                s = stream.read()
                self._preflight(s)
                interpolated_config = self._interpolate(s, env, keep_string)
                defaults = util.merge_dicts(
                    defaults, util.safe_load(interpolated_config)
                )

        if self.molecule_file:
            with util.open_file(self.molecule_file) as stream:
                s = stream.read()
                self._preflight(s)
                interpolated_config = self._interpolate(s, env, keep_string)
                defaults = util.merge_dicts(
                    defaults, util.safe_load(interpolated_config)
                )

        return defaults

    def _interpolate(self, stream: str, env: MutableMapping, keep_string: str) -> str:
        env = set_env_from_file(env, self.env_file)

        i = interpolation.Interpolator(interpolation.TemplateWithDefaults, env)

        try:
            return i.interpolate(stream, keep_string)
        except interpolation.InvalidInterpolation as e:
            msg = (
                f"parsing config file '{self.molecule_file}'.\n\n{e.place}\n{e.string}"
            )
            util.sysexit_with_message(msg)
        return ""

    def _get_defaults(self) -> MutableMapping:
        if not self.molecule_file:
            scenario_name = "default"
        else:
            scenario_name = (
                os.path.basename(os.path.dirname(self.molecule_file)) or "default"
            )
        return {
            "dependency": {
                "name": "galaxy",
                "command": None,
                "enabled": True,
                "options": {},
                "env": {},
            },
            "driver": {
                "name": "delegated",
                "provider": {"name": None},
                "options": {"managed": True},
                "ssh_connection_options": [],
                "safe_files": [],
            },
            "platforms": [],
            "prerun": True,
            "provisioner": {
                "name": "ansible",
                "config_options": {},
                "ansible_args": [],
                "connection_options": {},
                "options": {},
                "env": {},
                "inventory": {
                    "hosts": {},
                    "host_vars": {},
                    "group_vars": {},
                    "links": {},
                },
                "children": {},
                "playbooks": {
                    "cleanup": "cleanup.yml",
                    "create": "create.yml",
                    "converge": "converge.yml",
                    "destroy": "destroy.yml",
                    "prepare": "prepare.yml",
                    "side_effect": "side_effect.yml",
                    "verify": "verify.yml",
                },
                "log": True,
            },
            "scenario": {
                "name": scenario_name,
                "check_sequence": [
                    "dependency",
                    "cleanup",
                    "destroy",
                    "create",
                    "prepare",
                    "converge",
                    "check",
                    "cleanup",
                    "destroy",
                ],
                "cleanup_sequence": ["cleanup"],
                "converge_sequence": ["dependency", "create", "prepare", "converge"],
                "create_sequence": ["dependency", "create", "prepare"],
                "destroy_sequence": ["dependency", "cleanup", "destroy"],
                "test_sequence": [
                    # dependency must be kept before lint to avoid errors
                    "dependency",
                    "lint",
                    "cleanup",
                    "destroy",
                    "syntax",
                    "create",
                    "prepare",
                    "converge",
                    "idempotence",
                    "side_effect",
                    "verify",
                    "cleanup",
                    "destroy",
                ],
            },
            "verifier": {
                "name": "ansible",
                "enabled": True,
                "options": {},
                "env": {},
                "additional_files_or_dirs": [],
            },
        }

    def _preflight(self, data: MutableMapping):
        env = set_env_from_file(os.environ.copy(), self.env_file)
        errors, data = schema_v3.pre_validate(data, env, MOLECULE_KEEP_STRING)
        if errors:
            msg = f"Failed to pre-validate.\n\n{errors}"
            util.sysexit_with_message(msg, detail=data)

    def _validate(self):
        msg = f"Validating schema {self.molecule_file}."
        LOG.debug(msg)

        errors = schema_v3.validate(self.config)
        if errors:
            msg = f"Failed to validate {self.molecule_file}\n\n{errors}"
            util.sysexit_with_message(msg)


def molecule_directory(path: str) -> str:
    """Return directory of the current scenario."""
    return os.path.join(path, MOLECULE_DIRECTORY)


def molecule_file(path: str) -> str:
    """Return file path of current scenario."""
    return os.path.join(path, MOLECULE_FILE)


def set_env_from_file(env: MutableMapping[str, str], env_file: str) -> MutableMapping:
    """Load environment from file."""
    if env_file and os.path.exists(env_file):
        env = copy.copy(env)
        d = util.safe_load_file(env_file)
        for k, v in d.items():
            env[k] = v

        return env

    return env

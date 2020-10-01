"""Ansible Galaxy dependencies for lists of roles."""
import os
from pathlib import Path

from molecule import logger, util
from molecule.dependency.ansible_galaxy.base import AnsibleGalaxyBase

LOG = logger.get_logger(__name__)


class Roles(AnsibleGalaxyBase):
    """Role-specific Ansible Galaxy dependency handling."""

    FILTER_OPTS = ("requirements-file", "collections-path")  # type: ignore
    COMMANDS = ("install",)

    @property
    def default_options(self):
        general = super(Roles, self).default_options
        specific = util.merge_dicts(
            general,
            {
                "role-file": os.path.join(
                    self._config.scenario.directory, "requirements.yml"
                ),
                "roles-path": os.path.join(
                    self._config.scenario.ephemeral_directory, "roles"
                ),
            },
        )
        return specific

    @property
    def install_path(self):
        return os.path.join(self._config.scenario.directory, self.options["roles-path"])

    @property
    def requirements_file(self):
        return Path(self.options["role-file"]).relative_to(
            self._config.scenario.directory
        )

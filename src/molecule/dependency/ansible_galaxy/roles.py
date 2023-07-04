"""Ansible Galaxy dependencies for lists of roles."""
import logging
import os

from molecule import util
from molecule.dependency.ansible_galaxy.base import AnsibleGalaxyBase

LOG = logging.getLogger(__name__)


class Roles(AnsibleGalaxyBase):
    """Role-specific Ansible Galaxy dependency handling."""

    FILTER_OPTS = ("requirements-file",)  # type: ignore
    COMMANDS = ("install",)

    @property
    def default_options(self):
        general = super().default_options
        specific = util.merge_dicts(
            general,
            {
                "role-file": os.path.join(
                    self._config.scenario.directory,
                    "requirements.yml",
                ),
            },
        )
        return specific

    @property
    def requirements_file(self):
        return self.options["role-file"]

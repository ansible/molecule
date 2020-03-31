"""Ansible Galaxy dependencies for lists of collections."""
import os

from molecule import logger
from molecule import util
from molecule.dependency.ansible_galaxy.base import AnsibleGalaxyBase


LOG = logger.get_logger(__name__)


class Collections(AnsibleGalaxyBase):
    """Collection-specific Ansible Galaxy dependency handling."""

    FILTER_OPTS = ("roles-file", "roles-path")
    COMMANDS = ("collection", "install")

    @property
    def default_options(self):
        general = super(Collections, self).default_options
        specific = util.merge_dicts(
            general,
            {
                "requirements-file": os.path.join(
                    self._config.scenario.directory, "collections.yml"
                ),
                "collections-path": os.path.join(
                    self._config.scenario.ephemeral_directory, "collections"
                ),
            },
        )

        return specific

    @property
    def default_env(self):
        general = super(Collections, self).default_env
        return util.merge_dicts(
            general, {"ANSIBLE_COLLECTIONS_PATHS": self.install_path}
        )

    @property
    def install_path(self):
        return self.options["collections-path"]

    @property
    def requirements_file(self):
        return self.options["requirements-file"]

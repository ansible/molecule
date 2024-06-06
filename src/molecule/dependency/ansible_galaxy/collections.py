"""Ansible Galaxy dependencies for lists of collections."""

import logging
import os

from molecule import util
from molecule.dependency.ansible_galaxy.base import AnsibleGalaxyBase

LOG = logging.getLogger(__name__)


class Collections(AnsibleGalaxyBase):
    """Collection-specific Ansible Galaxy dependency handling."""

    FILTER_OPTS = ("role-file",)  # type: ignore
    COMMANDS = ("collection", "install")

    @property
    def default_options(self):  # type: ignore[no-untyped-def]
        general = super().default_options
        specific = util.merge_dicts(
            general,
            {
                "requirements-file": os.path.join(
                    self._config.scenario.directory,
                    "collections.yml",
                ),
            },
        )

        return specific

    @property
    def default_env(self):  # type: ignore[no-untyped-def]
        return super().default_env

    @property
    def requirements_file(self):  # type: ignore[no-untyped-def]
        return self.options["requirements-file"]

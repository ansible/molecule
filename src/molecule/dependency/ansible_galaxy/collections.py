"""Ansible Galaxy dependencies for lists of collections."""

from __future__ import annotations

import logging
import os

from molecule import util
from molecule.dependency.ansible_galaxy.base import AnsibleGalaxyBase


LOG = logging.getLogger(__name__)


class Collections(AnsibleGalaxyBase):
    """Collection-specific Ansible Galaxy dependency handling."""

    FILTER_OPTS = ("role-file",)  # type: ignore  # noqa: PGH003
    COMMANDS = ("collection", "install")

    @property
    def default_options(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        general = super().default_options
        specific = util.merge_dicts(
            general,
            {
                "requirements-file": os.path.join(  # noqa: PTH118
                    self._config.scenario.directory,
                    "collections.yml",
                ),
            },
        )

        return specific  # noqa: RET504

    @property
    def default_env(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return super().default_env

    @property
    def requirements_file(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self.options["requirements-file"]

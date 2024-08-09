"""Ansible Galaxy dependencies for lists of roles."""

from __future__ import annotations

import logging
import os

from molecule import util
from molecule.dependency.ansible_galaxy.base import AnsibleGalaxyBase


LOG = logging.getLogger(__name__)


class Roles(AnsibleGalaxyBase):
    """Role-specific Ansible Galaxy dependency handling."""

    FILTER_OPTS = ("requirements-file",)  # type: ignore  # noqa: PGH003
    COMMANDS = ("install",)

    @property
    def default_options(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        general = super().default_options
        specific = util.merge_dicts(
            general,
            {
                "role-file": os.path.join(  # noqa: PTH118
                    self._config.scenario.directory,
                    "requirements.yml",
                ),
            },
        )
        return specific  # noqa: RET504

    @property
    def requirements_file(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self.options["role-file"]

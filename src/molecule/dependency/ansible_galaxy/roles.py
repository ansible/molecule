"""Ansible Galaxy dependencies for lists of roles."""

from __future__ import annotations

import logging
import os

from typing import TYPE_CHECKING

from molecule import util
from molecule.dependency.ansible_galaxy.base import AnsibleGalaxyBase


if TYPE_CHECKING:
    from molecule.types import DependencyOptions


LOG = logging.getLogger(__name__)


class Roles(AnsibleGalaxyBase):
    """Role-specific Ansible Galaxy dependency handling."""

    FILTER_OPTS = ("requirements-file",)
    COMMANDS = ("install",)

    @property
    def default_options(self) -> DependencyOptions:
        """Default options for this dependency.

        Returns:
            Default options for this dependency.
        """
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
    def requirements_file(self) -> str:
        """Path to requirements file.

        Returns:
            Path to the requirements file for this dependency.
        """
        return self.options["role-file"]

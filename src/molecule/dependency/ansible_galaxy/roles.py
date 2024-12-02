"""Ansible Galaxy dependencies for lists of roles."""

from __future__ import annotations

import logging

from pathlib import Path
from typing import TYPE_CHECKING, cast

from molecule import util
from molecule.dependency.ansible_galaxy.base import AnsibleGalaxyBase


if TYPE_CHECKING:
    from collections.abc import MutableMapping


LOG = logging.getLogger(__name__)


class Roles(AnsibleGalaxyBase):
    """Role-specific Ansible Galaxy dependency handling.

    Attributes:
        FILTER_OPTS: Keys to remove from the dictionary returned by options().
        COMMANDS: Arguments to send to ansible-galaxy to install the appropriate type of content.
    """

    FILTER_OPTS = ("requirements-file",)
    COMMANDS = ("install",)

    @property
    def default_options(self) -> MutableMapping[str, str | bool]:
        """Default options for this dependency.

        Returns:
            Default options for this dependency.
        """
        general = super().default_options
        specific = util.merge_dicts(
            general,
            {
                "role-file": str(
                    Path(
                        self._config.scenario.directory,
                        "requirements.yml",
                    ),
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
        return cast(str, self.options["role-file"])

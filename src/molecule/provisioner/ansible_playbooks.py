#  Copyright (c) 2015-2018 Cisco Systems, Inc.

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
"""Ansible-Playbooks Provisioner Module."""
from __future__ import annotations

import logging
import os

from pathlib import Path
from typing import TYPE_CHECKING

from molecule import util


if TYPE_CHECKING:
    from typing import Literal

    from molecule.config import Config

    Section = Literal[
        "cleanup",
        "create",
        "converge",
        "destroy",
        "prepare",
        "side_effect",
        "verify",
    ]


LOG = logging.getLogger(__name__)


class AnsiblePlaybooks:
    """A class to act as a module to namespace playbook properties."""

    def __init__(self, config: Config) -> None:
        """Initialize a new namespace class.

        Args:
            config: An instance of a Molecule config.
        """
        self._config = config

    @property
    def cleanup(self) -> str | None:
        """Get the cleanup playbook path.

        Returns:
            Path to cleanup.yml.
        """
        return self._get_playbook("cleanup")

    @property
    def create(self) -> str | None:
        """Get the create playbook path.

        Returns:
            Path to create.yml.
        """
        return self._get_playbook("create")

    @property
    def converge(self) -> str | None:
        """Get the converge playbook path.

        Returns:
            Path to converge.yml.
        """
        return self._get_playbook("converge")

    @property
    def destroy(self) -> str | None:
        """Get the destroy playbook path.

        Returns:
            Path to destroy.yml.
        """
        return self._get_playbook("destroy")

    @property
    def prepare(self) -> str | None:
        """Get the prepare playbook path.

        Returns:
            Path to prepare.yml.
        """
        return self._get_playbook("prepare")

    @property
    def side_effect(self) -> str | None:
        """Get the side_effect playbook path.

        Returns:
            Path to side_effect.yml.
        """
        return self._get_playbook("side_effect")

    @property
    def verify(self) -> str | None:
        """Get the verify playbook path.

        Returns:
            Path to verify.yml.
        """
        return self._get_playbook("verify")

    def _get_playbook_directory(self) -> Path:
        if self._config.provisioner:
            return util.abs_path(
                Path(self._config.provisioner.directory, "playbooks"),
            )
        return Path()

    def _get_playbook(self, section: Section) -> str | None:
        """Return path to playbook or None if playbook is not needed.

        Return None when there is no playbook configured and when action is
        considered skippable.

        Args:
            section: Named section to retrieve playbook for.

        Returns:
            The playbook path, or none if one is not needed.
        """
        c = self._config.config
        driver_dict: dict[Section, str | None] | None = c["provisioner"]["playbooks"].get(  # type: ignore[assignment]
            self._config.driver.name,
        )

        playbook: str | None = c["provisioner"]["playbooks"][section]
        if driver_dict:
            try:
                playbook = driver_dict[section]
            except Exception as exc:
                LOG.exception(exc)  # noqa: TRY401
        if self._config.provisioner and playbook is not None:
            playbook = self._config.provisioner.abs_path(playbook)
            if playbook:
                playbook = self._normalize_playbook(playbook)

                if os.path.exists(playbook):  # noqa: PTH110
                    return playbook

            if os.path.exists(self._get_bundled_driver_playbook(section)):  # noqa: PTH110
                return self._get_bundled_driver_playbook(section)
            if section not in [
                # these playbooks can be considered optional
                "prepare",
                "create",
                "destroy",
                "cleanup",
                "side_effect",
                "verify",
            ]:
                return playbook
        return None

    def _get_bundled_driver_playbook(self, section: Section) -> str:
        driver_path = self._config.driver.get_playbook(section)
        if driver_path:
            return driver_path

        path = Path(
            self._get_playbook_directory(),
            self._config.driver.name,
            self._config.config["provisioner"]["playbooks"][section],
        )
        if path.exists():
            return str(path)
        path = Path(
            self._config.driver._path,  # noqa: SLF001
            "playbooks",
            self._config.config["provisioner"]["playbooks"][section],
        )
        return str(path)

    def _normalize_playbook(self, playbook: str) -> str:
        """Return current filename to use for a playbook by allowing fallbacks.

        Currently used to deprecate use of playbook.yml in favour of converge.yml

        Args:
            playbook: Playbook path to alter.

        Returns:
            Normalized playbook path.
        """
        play_path = Path(playbook)
        if not playbook or play_path.is_file():
            return playbook

        pb_rename_map = {"converge.yml": "playbook.yml"}
        basename = play_path.name
        if basename in pb_rename_map:
            fb_playbook = play_path.parent / pb_rename_map[basename]
            if fb_playbook.is_file():
                LOG.warning(
                    "%s was deprecated, rename it to %s",
                    fb_playbook.name,
                    basename,
                )
                playbook = str(fb_playbook)
        return playbook

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

from molecule import util


LOG = logging.getLogger(__name__)


class AnsiblePlaybooks:
    """A class to act as a module to namespace playbook properties."""

    def __init__(self, config) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN001
        """Initialize a new namespace class and returns None.

        Args:
            config: An instance of a Molecule config.
        """
        self._config = config

    @property
    def cleanup(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self._get_playbook("cleanup")  # type: ignore[no-untyped-call]

    @property
    def create(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self._get_playbook("create")  # type: ignore[no-untyped-call]

    @property
    def converge(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self._get_playbook("converge")  # type: ignore[no-untyped-call]

    @property
    def destroy(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self._get_playbook("destroy")  # type: ignore[no-untyped-call]

    @property
    def prepare(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self._get_playbook("prepare")  # type: ignore[no-untyped-call]

    @property
    def side_effect(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self._get_playbook("side_effect")  # type: ignore[no-untyped-call]

    @property
    def verify(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self._get_playbook("verify")  # type: ignore[no-untyped-call]

    def _get_playbook_directory(self):  # type: ignore[no-untyped-def]  # noqa: ANN202
        return util.abs_path(
            os.path.join(self._config.provisioner.directory, "playbooks"),  # noqa: PTH118
        )

    def _get_playbook(self, section):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN202
        """Return path to playbook or None if playbook is not needed.

        Return None when there is no playbook configured and when action is
        considered skippable.
        """
        c = self._config.config
        driver_dict = c["provisioner"]["playbooks"].get(self._config.driver.name)

        playbook = c["provisioner"]["playbooks"][section]
        if driver_dict:
            try:
                playbook = driver_dict[section]
            except Exception as exc:
                LOG.exception(exc)  # noqa: TRY401
        if playbook is not None:
            playbook = self._config.provisioner.abs_path(playbook)
            playbook = self._normalize_playbook(playbook)  # type: ignore[no-untyped-call]

            if os.path.exists(playbook):  # noqa: PTH110
                return playbook
            if os.path.exists(self._get_bundled_driver_playbook(section)):  # type: ignore[no-untyped-call]  # noqa: PTH110
                return self._get_bundled_driver_playbook(section)  # type: ignore[no-untyped-call]
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

    def _get_bundled_driver_playbook(self, section):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN202
        path = self._config.driver.get_playbook(section)
        if path:
            return path

        path = os.path.join(  # noqa: PTH118
            self._get_playbook_directory(),  # type: ignore[no-untyped-call]
            self._config.driver.name,
            self._config.config["provisioner"]["playbooks"][section],
        )
        if os.path.exists(path):  # noqa: PTH110
            return path
        path = os.path.join(  # noqa: PTH118
            self._config.driver._path,  # noqa: SLF001
            "playbooks",
            self._config.config["provisioner"]["playbooks"][section],
        )
        return path  # noqa: RET504

    def _normalize_playbook(self, playbook):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN202
        """Return current filename to use for a playbook by allowing fallbacks.

        Currently used to deprecate use of playbook.yml in favour of converge.yml
        """
        if not playbook or os.path.isfile(playbook):  # noqa: PTH113
            return playbook

        pb_rename_map = {"converge.yml": "playbook.yml"}
        basename = os.path.basename(playbook)  # noqa: PTH119
        if basename in pb_rename_map:
            fb_playbook = os.path.join(  # noqa: PTH118
                os.path.dirname(playbook),  # noqa: PTH120
                pb_rename_map[basename],
            )
            if os.path.isfile(fb_playbook):  # noqa: PTH113
                LOG.warning(
                    "%s was deprecated, rename it to %s",
                    pb_rename_map[basename],
                    basename,
                )
                playbook = fb_playbook
        return playbook

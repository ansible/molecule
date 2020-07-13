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

from __future__ import absolute_import

import os

from molecule import logger, util

LOG = logger.get_logger(__name__)


class AnsiblePlaybooks(object):
    """A class to act as a module to namespace playbook properties."""

    def __init__(self, config):
        """
        Initialize a new namespace class and returns None.

        :param config: An instance of a Molecule config.
        :return: None
        """
        self._config = config

    @property
    def cleanup(self):
        return self._get_playbook("cleanup")

    @property
    def create(self):
        return self._get_playbook("create")

    @property
    def converge(self):
        return self._get_playbook("converge")

    @property
    def destroy(self):
        return self._get_playbook("destroy")

    @property
    def prepare(self):
        return self._get_playbook("prepare")

    @property
    def side_effect(self):
        return self._get_playbook("side_effect")

    @property
    def verify(self):
        return self._get_playbook("verify")

    def _get_playbook_directory(self):
        return util.abs_path(
            os.path.join(self._config.provisioner.directory, "playbooks")
        )

    def _get_playbook(self, section):
        """
        Return path to playbook or None if playbook is not needed.

        Return None when there is no playbook configured and when action is
        considered skippable.
        """
        c = self._config.config
        driver_dict = c["provisioner"]["playbooks"].get(self._config.driver.name)

        playbook = c["provisioner"]["playbooks"][section]
        if driver_dict:
            try:
                playbook = driver_dict[section]
            except Exception:
                pass

        if playbook is not None:
            playbook = self._config.provisioner.abs_path(playbook)
            playbook = self._normalize_playbook(playbook)

            if os.path.exists(playbook):
                return playbook
            elif os.path.exists(self._get_bundled_driver_playbook(section)):
                return self._get_bundled_driver_playbook(section)
            elif section not in [
                # these playbooks can be considered optional
                "prepare",
                "create",
                "destroy",
                "cleanup",
                "side_effect",
                "verify",
            ]:
                return playbook

    def _get_bundled_driver_playbook(self, section):
        return self._config.driver.get_playbook(section) or os.path.join(
            self._get_playbook_directory(),
            self._config.driver.name,
            self._config.config["provisioner"]["playbooks"][section],
        )

    def _normalize_playbook(self, playbook):
        """
        Return current filename to use for a playook by allowing fallbacks.

        Currently used to deprecate use of playbook.yml in favour of converge.yml
        """
        # TODO(ssbarnea): Remove that deprecation fallback in 3.1+
        if not playbook or os.path.isfile(playbook):
            return playbook

        pb_rename_map = {"converge.yml": "playbook.yml"}
        basename = os.path.basename(playbook)
        if basename in pb_rename_map:
            fb_playbook = os.path.join(
                os.path.dirname(playbook), pb_rename_map[basename]
            )
            if os.path.isfile(fb_playbook):
                LOG.warning(
                    "%s was deprecated, rename it to %s"
                    % (pb_rename_map[basename], basename)
                )
                playbook = fb_playbook
        return playbook

#  Copyright (c) 2015-2018 Cisco Systems, Inc.
#
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
"""Base Ansible Galaxy dependency module."""
from __future__ import annotations

import abc
import copy
import logging
import os

from pathlib import Path
from typing import TYPE_CHECKING

from molecule import util
from molecule.dependency import base


if TYPE_CHECKING:
    from collections.abc import MutableMapping

    from molecule.config import Config


LOG = logging.getLogger(__name__)


class AnsibleGalaxyBase(base.Base):
    """Ansible Galaxy dependency base class.

    Attributes:
        FILTER_OPTS: Keys to remove from the dictionary returned by options().
        COMMANDS: Arguments to send to ansible-galaxy to install the appropriate type of content.
    """

    FILTER_OPTS: tuple[str, ...] = ()
    COMMANDS: tuple[str, ...] = ()

    def __init__(self, config: Config) -> None:
        """Construct AnsibleGalaxy.

        Args:
            config: Molecule Config instance.
        """
        super().__init__(config)
        self._sh_command = []

        self.command = "ansible-galaxy"

    @property
    @abc.abstractmethod
    def requirements_file(self) -> str:  # cover
        """Path to requirements file.

        Returns:
            Path to the requirements file for this dependency.
        """

    @property
    def default_options(self) -> MutableMapping[str, str | bool]:
        """Default options for this dependency.

        Returns:
            Default options for this dependency.
        """
        d: MutableMapping[str, str | bool] = {
            "force": False,
        }
        if self._config.debug:
            d["vvv"] = True

        return d

    def filter_options(
        self,
        opts: MutableMapping[str, str | bool],
        keys: tuple[str, ...],
    ) -> MutableMapping[str, str | bool]:
        """Filter certain keys from a dictionary.

        Removes all the values of ``keys`` from the dictionary ``opts``, if
        they are present. Returns the resulting dictionary. Does not modify the
        existing one.

        Args:
            opts: Options dictionary.
            keys: Key names to exclude from opts.

        Returns:
            A copy of ``opts`` without the value of keys
        """
        c = copy.copy(opts)
        for key in keys:
            if key in c:
                del c[key]
        return c

    # NOTE(retr0h): Override the base classes' options() to handle
    # ``ansible-galaxy`` one-off.
    @property
    def options(self) -> MutableMapping[str, str | bool]:
        """Computed options for this dependency.

        Returns:
            Merged and filtered options for this dependency.
        """
        opts = self._config.config["dependency"]["options"]
        # NOTE(retr0h): Remove verbose options added by the user while in
        # debug.
        if self._config.debug:
            opts = util.filter_verbose_permutation(opts)

        opts = util.merge_dicts(self.default_options, opts)
        return self.filter_options(opts, self.FILTER_OPTS)

    @property
    def default_env(self) -> dict[str, str]:
        """Default environment variables for this dependency.

        Returns:
            Default environment variables for this dependency.
        """
        env = dict(os.environ)
        return util.merge_dicts(env, self._config.env)

    def bake(self) -> None:
        """Bake an ``ansible-galaxy`` command so it's ready to execute and returns None."""
        options = self.options
        verbose_flag = util.verbose_flag(options)

        self._sh_command = [
            self.command,
            *self.COMMANDS,
            *util.dict2args(options),
            *verbose_flag,
        ]

    def execute(self, action_args: list[str] | None = None) -> None:  # noqa: ARG002
        """Execute dependency.

        Args:
            action_args: Arguments for this dependency. Unused.
        """
        if not self.enabled:
            msg = "Skipping, dependency is disabled."
            LOG.warning(msg)
            return
        super().execute()

        if not self._has_requirements_file():
            msg = "Skipping, missing the requirements file."
            LOG.warning(msg)
            return

        if not self._sh_command:
            self.bake()

        self._setup()
        self.execute_with_retries()

    def _setup(self) -> None:
        """Prepare the system for using ``ansible-galaxy`` and returns None."""

    def _has_requirements_file(self) -> bool:
        return Path(self.requirements_file).is_file()

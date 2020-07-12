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
"""Gilt Dependency Module."""

import os

import sh

from molecule import logger, util
from molecule.dependency import base

LOG = logger.get_logger(__name__)


class Gilt(base.Base):
    """
    `Gilt`_ is an alternate dependency manager.

    Additional options can be passed to ``gilt overlay`` through the options
    dict.  Any option set in this section will override the defaults.

    .. code-block:: yaml

        dependency:
          name: gilt
          options:
            debug: True


    The dependency manager can be disabled by setting ``enabled`` to False.

    .. code-block:: yaml

        dependency:
          name: gilt
          enabled: False

    Environment variables can be passed to the dependency.

    .. code-block:: yaml

        dependency:
          name: gilt
          env:
            FOO: bar

    .. _`Gilt`: https://gilt.readthedocs.io
    """

    def __init__(self, config):
        """Construct Gilt."""
        super(Gilt, self).__init__(config)
        self._sh_command = None

        self.command = "gilt"

    @property
    def default_options(self):
        config = os.path.join(self._config.scenario.directory, "gilt.yml")
        d = {"config": config}
        if self._config.debug:
            d["debug"] = True

        return d

    @property
    def default_env(self):
        return util.merge_dicts(os.environ, self._config.env)

    def bake(self):
        """
        Bake a ``gilt`` command so it's ready to execute and returns None.

        :return: None
        """
        self._sh_command = getattr(sh, self.command)
        self._sh_command = self._sh_command.bake(
            self.options, "overlay", _env=self.env, _out=LOG.out, _err=LOG.error
        )

    def execute(self):
        if not self.enabled:
            msg = "Skipping, dependency is disabled."
            LOG.warning(msg)
            return

        if not self._has_requirements_file():
            msg = "Skipping, missing the requirements file."
            LOG.warning(msg)
            return

        if self._sh_command is None:
            self.bake()

        self.execute_with_retries()

    def _config_file(self):
        return self.options.get("config")

    def _has_requirements_file(self):
        return os.path.isfile(self._config_file())

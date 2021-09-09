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
"""Shell Dependency Module."""

import logging

from molecule.dependency import base
from molecule.util import BakedCommand

LOG = logging.getLogger(__name__)


class Shell(base.Base):
    """
    ``Shell`` is an alternate dependency manager.

    It is intended to run a command in situations where `Ansible Galaxy`_
    don't suffice.

    The ``command`` to execute is required, and is relative to Molecule's
    project directory when referencing a script not in $PATH.

    .. note::

        Unlike the other dependency managers, ``options`` are ignored and not
        passed to `shell`.  Additional flags/subcommands should simply be added
        to the `command`.

    .. code-block:: yaml

        dependency:
          name: shell
          command: path/to/command --flag1 subcommand --flag2

    The dependency manager can be disabled by setting ``enabled`` to False.

    .. code-block:: yaml

        dependency:
          name: shell
          command: path/to/command --flag1 subcommand --flag2
          enabled: False

    Environment variables can be passed to the dependency.

    .. code-block:: yaml

        dependency:
          name: shell
          command: path/to/command --flag1 subcommand --flag2
          env:
            FOO: bar
    """

    def __init__(self, config):
        """Construct Shell."""
        super(Shell, self).__init__(config)
        self._sh_command = None

        # self.command = config..config['dependency']['command']

    @property
    def command(self):
        return self._config.config["dependency"]["command"]

    @property
    def default_options(self):
        return {}

    def bake(self) -> None:
        """Bake a ``shell`` command so it's ready to execute."""
        self._sh_command = BakedCommand(cmd=self.command, env=self.env)

    def execute(self):
        if not self.enabled:
            msg = "Skipping, dependency is disabled."
            LOG.warning(msg)
            return
        super().execute()

        if self._sh_command is None:
            self.bake()

        self.execute_with_retries()

    def _has_command_configured(self):
        return "command" in self._config.config["dependency"]

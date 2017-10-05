#  Copyright (c) 2015-2017 Cisco Systems, Inc.
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

import os

from molecule import logger
from molecule.command import base

LOG = logger.get_logger(__name__)


class Prepare(base.Base):
    """
    Prepare leverage the command's base class which sets up the provisioner's
    inventory through init.  However, it is not a subcommand and is executed
    internally.
    """

    def execute(self):
        """
        Execute the actions necessary to prepare the instances and returns
        None.

        :return: None
        """
        self.print_info()

        if self._config.state.prepared:
            msg = 'Skipping, instances already prepared.'
            LOG.warn(msg)
            return

        if self._has_prepare_playbook():
            self._config.provisioner.prepare()
        else:
            msg = ('[DEPRECATION WARNING]:\n  The prepare playbook not found '
                   'at {}/prepare.yml.  Please add one to the scenarios '
                   'directory.').format(self._config.scenario.directory)
            LOG.warn(msg)

        self._config.state.change_state('prepared', True)

    def _has_prepare_playbook(self):
        return os.path.exists(self._config.provisioner.playbooks.prepare)

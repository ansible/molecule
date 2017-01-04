#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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

import sh

from molecule import util
from molecule.dependency import base


class Gilt(base.Base):
    """
    `Gilt`_ is an alternate dependency manager.

    Additional options can be passed to `gilt` through the options
    dict.  Any option set in this section will override the defaults.

    .. code-block:: yaml

        dependency:
          name: gilt
          options:
            debug: True


    The dependency manager can be disabled by setting `enabled` to False.

    .. code-block:: yaml

        dependency:
          name: gilt
          enabled: False

    .. _`Gilt`: http://gilt.readthedocs.io
    """

    def __init__(self, config):
        super(Gilt, self).__init__(config)
        self._gilt_command = None

    @property
    def default_options(self):
        """
        Default CLI arguments provided to `gilt` and returns a dict.

        :return: dict
        """
        config = os.path.join(self._config.scenario.directory, 'gilt.yml')
        d = {'config': config}
        if self._config.args.get('debug'):
            d['debug'] = True

        return d

    def bake(self):
        """
        Bake a `gilt` command so it's ready to execute and returns None.

        :return: None
        """
        self._gilt_command = sh.gilt.bake(
            self.options,
            'overlay',
            _env=os.environ,
            _out=util.callback_info,
            _err=util.callback_error)

    def execute(self):
        """
        Executes `gilt` and returns None.

        :return: None
        """
        if not self.enabled:
            return

        if self._gilt_command is None:
            self.bake()

        try:
            util.run_command(
                self._gilt_command, debug=self._config.args.get('debug'))
        except sh.ErrorReturnCode as e:
            util.sysexit(e.exit_code)

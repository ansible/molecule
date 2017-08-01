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

LOG = logger.get_logger(__name__)


class Scenario(object):
    """
    A scenario allows Molecule test a role in a particular way, this is a
    fundamental change from Molecule v1.

    A scenario is a self-contained directory containing everything necessary
    for testing the role in a particular way.  The default scenario is named
    `default`, and every role should contain a default scenario.

    Any option set in this section will override the defaults.

    .. code-block:: yaml

        scenario:
          name: default
          converge_sequences:
            - create
            - converge
          test_sequences:
            - destroy
            - create
            - converge
            - lint
            - verify
            - destroy

    A good source of examples are the `scenario`_ functional tests.

    .. _`scenario`: https://github.com/metacloud/molecule/tree/master/test/scenarios/driver
    """  # noqa

    def __init__(self, config):
        """
        Initialize a new scenario class and returns None.

        :param config: An instance of a Molecule config.
        :return: None
        """
        self.config = config
        self._setup()

    @property
    def name(self):
        return self.config.config['scenario']['name']

    @property
    def directory(self):
        return os.path.dirname(self.config.molecule_file)

    @property
    def ephemeral_directory(self):
        return os.path.join(self.directory, '.molecule')

    @property
    def check_sequences(self):
        return self.config.config['scenario']['check_sequences']

    @property
    def converge_sequences(self):
        return self.config.config['scenario']['converge_sequences']

    @property
    def test_sequences(self):
        return self.config.config['scenario']['test_sequences']

    def _setup(self):
        """
         Prepare the scenario for Molecule and returns None.

         :return: None
         """
        if not os.path.isdir(self.ephemeral_directory):
            os.mkdir(self.ephemeral_directory)

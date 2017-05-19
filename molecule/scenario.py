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
    Scenarios allow Molecule test a role in various ways.  Scenarios are a
    fundamental change from Molecule v1.

    Molecule will search the `molecule/` directory for directories representing
    scenarios.  These scenario directories contain everything necessary for
    managing the instances, and converging/testing the role.

    Any option set in this section will override the defaults.

    .. code-block:: yaml

        scenario:
          name: default
          converge_sequence:
            - create
            - converge
          test_sequence:
            - destroy
            - create
            - converge
            - lint
            - verify
            - destroy

    A good source of examples are the `scenario`_ functional tests.

    .. important::

        The scenario name cannot be configured through `molecule.yml`.  It is
        determined by the directory name of the scenario.  The config value
        references a `MOLECULE_SCENARIO_NAME` environment variable, which is
        correctly interpolated.  However, it provided so that the config is
        symmetrical.  It may be removed in the future, if the source of much
        confusion.

    .. _`scenario`: https://github.com/metacloud/molecule/tree/v2/test/scenarios/driver
    """  # noqa

    def __init__(self, config):
        """
        A class encapsulating a scenario.

        :param config: An instance of a Molecule config.
        :return: None
        """
        self._config = config

    @property
    def name(self):
        return name(self.directory)

    @property
    def directory(self):
        return directory(self._config.molecule_file)

    @property
    def check_sequence(self):
        return self._config.config['scenario']['check_sequence']

    @property
    def converge_sequence(self):
        return self._config.config['scenario']['converge_sequence']

    @property
    def test_sequence(self):
        return self._config.config['scenario']['test_sequence']


def name(path):
    return os.path.basename(path)

def directory(path):
    return os.path.dirname(path)

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


class Scenario(object):
    """
    Scenarios allow Molecule test a role in various ways.  Scenarios are a
    fundamental change from Molecule v1.

    Molecule will search the `molecule/` directory for directories representing
    scenarios.  These scenario directories contain everything necessary for
    managing the instances, and converging/testing the role.

    Molecule's provisioner manages the instances lifecycle.  However, the user
    must provide the setup, teardown, and converge playbooks.  Molecule's
    `init` subcommand will provide the necessary files for convenience.

    Any option set in this section will override the defaults.

    .. code-block:: yaml

        scenario:
          name: default
          setup: create.yml
          converge: playbook.yml
          teardown: destroy.yml
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
    """

    def __init__(self, config):
        """
        A class encapsulating a scenario.

        :param config: An instance of a Molecule config.
        :return: None
        """
        self._config = config

    @property
    def name(self):
        return self._config.config['scenario']['name']

    @property
    def directory(self):
        return os.path.dirname(self._config.molecule_file)

    @property
    def setup(self):
        return os.path.join(self.directory,
                            self._config.config['scenario']['setup'])

    @property
    def converge(self):
        return os.path.join(self.directory,
                            self._config.config['scenario']['converge'])

    @property
    def teardown(self):
        return os.path.join(self.directory,
                            self._config.config['scenario']['teardown'])

    @property
    def check_sequence(self):
        return self._config.config['scenario']['check_sequence']

    @property
    def converge_sequence(self):
        return self._config.config['scenario']['converge_sequence']

    @property
    def test_sequence(self):
        return self._config.config['scenario']['test_sequence']

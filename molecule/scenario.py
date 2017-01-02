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


class Scenario(object):
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
    def converge_sequence(self):
        return self._config.config['scenario']['converge_sequence']

    @property
    def test_sequence(self):
        return self._config.config['scenario']['test_sequence']

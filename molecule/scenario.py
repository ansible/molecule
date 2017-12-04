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
from molecule import scenarios

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
          create_sequence:
            - create
            - prepare
          check_sequence:
            - destroy
            - create
            - prepare
            - converge
            - check
            - destroy
          converge_sequence:
            - create
            - prepare
            - converge
          destroy_sequence:
            - destroy
          test_sequence:
            - lint
            - destroy
            - dependency
            - syntax
            - create
            - prepare
            - converge
            - idempotence
            - side_effect
            - verify
            - destroy
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
        return ephemeral_directory(self.directory)

    @property
    def check_sequence(self):
        return self.config.config['scenario']['check_sequence']

    @property
    def converge_sequence(self):
        return self.config.config['scenario']['converge_sequence']

    @property
    def create_sequence(self):
        return self.config.config['scenario']['create_sequence']

    @property
    def dependency_sequence(self):
        return ['dependency']

    @property
    def destroy_sequence(self):
        return self.config.config['scenario']['destroy_sequence']

    @property
    def idempotence_sequence(self):
        return ['idempotence']

    @property
    def lint_sequence(self):
        return ['lint']

    @property
    def prepare_sequence(self):
        return ['prepare']

    @property
    def side_effect_sequence(self):
        return ['side_effect']

    @property
    def syntax_sequence(self):
        return ['syntax']

    @property
    def test_sequence(self):
        return self.config.config['scenario']['test_sequence']

    @property
    def verify_sequence(self):
        return ['verify']

    @property
    def sequence(self):
        """
        Select the sequence based on scenario and subcommand of the provided
        scenario object and returns a list.

        :param scenario: A scenario object.
        :param skipped: An optional bool to include skipped scenarios.
        :return: list
        """
        s = scenarios.Scenarios([self.config])
        matrix = s._get_matrix()

        try:
            return matrix[self.name][self.config.subcommand]
        except KeyError:
            # TODO(retr0h): May change this handling in the future.
            return []

    def _setup(self):
        """
         Prepare the scenario for Molecule and returns None.

         :return: None
         """
        if not os.path.isdir(self.ephemeral_directory):
            os.mkdir(self.ephemeral_directory)


def ephemeral_directory(path):
    d = os.getenv('MOLECULE_EPHEMERAL_DIRECTORY')
    if d:
        return os.path.join(path, d)
    return os.path.join(path, '.molecule')

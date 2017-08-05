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

import operator

import tree_format

from molecule import logger
from molecule import util

LOG = logger.get_logger(__name__)


class Scenarios(object):
    """
    The Scenarios object consists of one to many scenario objects Molecule will
    execute.
    """

    def __init__(self, configs, scenario_name=None):
        """
        Initialize a new scenarios class and returns None.

        :param configs: A list containing Molecule config instances.
        :return: None
        """
        self._configs = configs
        self._scenario_name = scenario_name

    @property
    def all(self):
        """
        Return a list containing all scenario objects.

        :return: list
        """
        if self._scenario_name:
            scenarios = self._filter_for_scenario(self._scenario_name)
            self._verify()

            return scenarios

        return [c.scenario for c in self._configs]

    def print_sequence_info(self, scenario, sequence):
        msg = "Scenario: '{}'".format(scenario.name)
        LOG.info(msg)
        msg = "Sequence: '{}'".format(sequence)
        LOG.info(msg)

    def print_matrix(self):
        msg = 'Test matrix'
        LOG.info(msg)

        tree = tuple(
            ('', [(scenario.name,
                   [(sequence, [])
                    for sequence in self.sequences_for_scenario(scenario)])
                  for scenario in self.all]))

        tf = tree_format.format_tree(
            tree,
            format_node=operator.itemgetter(0),
            get_children=operator.itemgetter(1))

        LOG.out(tf.encode('utf-8'))

    def sequences_for_scenario(self, scenario):
        """
        Select the sequence based on scenario and subcommand of the provided
        scenario object and returns a list.

        :param scenario: A scenario object.
        :param skipped: An optional bool to include skipped scenarios.
        :return: list
        """
        matrix = self._get_matrix()

        try:
            return matrix[scenario.name][scenario.subcommand]
        except KeyError:
            # TODO(retr0h): May change this handling in the future.
            return []

    def _verify(self):
        """
        Verify the specified scenario was found and returns None.

        :return: None
        """
        scenario_names = [c.scenario.name for c in self._configs]
        if self._scenario_name not in scenario_names:
            msg = ("Scenario '{}' not found.  Exiting."
                   ).format(self._scenario_name)
            util.sysexit_with_message(msg)

    def _filter_for_scenario(self, scenario_name):
        """
        Find the scenario matching the provided scenario name and returns a
        list.

        :param scenario_name: A string containing the name of the scenario to
         find.
        :return: list
        """

        return [
            c.scenario for c in self._configs
            if c.scenario.name == scenario_name
        ]

    def _get_matrix(self):
        """
        Build a matrix of scenarios with sequences to include and returns a
        dict.

        {
            scenario_1: {
                'subcommand': [
                    'sequence-1',
                    'sequence-2',
                ],
            },
            scenario_2: {
                'subcommand': [
                    'sequence-1',
                ],
            },
        }

        :returns: dict
        """
        return dict({
            scenario.name: {
                'check': scenario.check_sequences,
                'converge': scenario.converge_sequences,
                'create': scenario.create_sequences,
                'dependency': scenario.dependency_sequences,
                'destroy': scenario.destroy_sequences,
                'idempotence': scenario.idempotence_sequences,
                'lint': scenario.lint_sequences,
                'side_effect': scenario.side_effect_sequences,
                'syntax': scenario.syntax_sequences,
                'test': scenario.test_sequences,
                'verify': scenario.verify_sequences,
            }
            for scenario in self.all
        })

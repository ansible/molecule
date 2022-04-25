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
"""Scenarios Module."""
import logging
from typing import List

from molecule import util

LOG = logging.getLogger(__name__)


class Scenarios(object):
    """The Scenarios groups one or more scenario objects Molecule will execute."""

    def __init__(self, configs, scenario_name=None):
        """
        Initialize a new scenarios class and returns None.

        :param configs: A list containing Molecule config instances.
        :param scenario_name: A string containing the name of the scenario.
        :return: None
        """
        self._configs = configs
        self._scenario_name = scenario_name
        self._scenarios = self.all

    def next(self):
        if not self._scenarios:
            raise StopIteration
        return self._scenarios.pop(0)

    def __iter__(self):
        """Make object iterable."""
        return self

    __next__ = next  # Python 3.X compatibility

    @property
    def all(self):
        """
        Return a list containing all scenario objects.

        :return: list
        """
        if self._scenario_name:
            scenarios = self._filter_for_scenario()
            self._verify()

            return scenarios

        scenarios = [c.scenario for c in self._configs]
        scenarios.sort(key=lambda x: x.directory)
        return scenarios

    def print_matrix(self):
        msg = "Test matrix"
        LOG.info(msg)

        tree = {}
        for scenario in self.all:
            tree[scenario.name] = [action for action in scenario.sequence]
        util.print_as_yaml(tree)

    def sequence(self, scenario_name: str) -> List[str]:
        for scenario in self.all:
            if scenario.name == scenario_name:
                return [action for action in scenario.sequence]
        raise RuntimeError(f"Unable to find sequence for {scenario_name} scenario.")

    def _verify(self):
        """
        Verify the specified scenario was found and returns None.

        :return: None
        """
        scenario_names = [c.scenario.name for c in self._configs]
        if self._scenario_name not in scenario_names:
            msg = f"Scenario '{self._scenario_name}' not found.  Exiting."
            util.sysexit_with_message(msg)

    def _filter_for_scenario(self):
        """
        Find the scenario matching the provided scenario name and returns a \
        list.

        :return: list
        """
        return [
            c.scenario for c in self._configs if c.scenario.name == self._scenario_name
        ]

    def _get_matrix(self):
        """
        Build a matrix of scenarios with sequence to include and returns a \
        dict.

        {
            scenario_1: {
                'subcommand': [
                    'action-1',
                    'action-2',
                ],
            },
            scenario_2: {
                'subcommand': [
                    'action-1',
                ],
            },
        }

        :returns: dict
        """
        return dict(
            {
                scenario.name: {
                    "check": scenario.check_sequence,
                    "cleanup": scenario.cleanup_sequence,
                    "converge": scenario.converge_sequence,
                    "create": scenario.create_sequence,
                    "dependency": scenario.dependency_sequence,
                    "destroy": scenario.destroy_sequence,
                    "idempotence": scenario.idempotence_sequence,
                    "lint": scenario.lint_sequence,
                    "prepare": scenario.prepare_sequence,
                    "side_effect": scenario.side_effect_sequence,
                    "syntax": scenario.syntax_sequence,
                    "test": scenario.test_sequence,
                    "verify": scenario.verify_sequence,
                }
                for scenario in self.all
            }
        )

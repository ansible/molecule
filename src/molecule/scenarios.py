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
from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from molecule import util


if TYPE_CHECKING:
    from molecule.config import Config
    from molecule.scenario import Scenario


LOG = logging.getLogger(__name__)


class Scenarios:
    """The Scenarios groups one or more scenario objects Molecule will execute."""

    def __init__(
        self,
        configs: list[Config],
        scenario_name: str | None = None,
    ) -> None:
        """Initialize a new scenarios class and returns None.

        Args:
            configs: Molecule config instances.
            scenario_name: The name of the scenario.
        """
        self._configs = configs
        self._scenario_name = scenario_name
        self._scenarios = self.all

    def __iter__(self) -> Scenarios:
        """Make object iterable.

        Returns:
            The object itself, as Scenarios is iterable.
        """
        return self

    def __next__(self) -> Scenario:
        """Iterate over Scenario objects.

        Returns:
            The next Scenario in the sequence.

        Raises:
            StopIteration: When the scenarios are exhausted.
        """
        if not self._scenarios:
            raise StopIteration
        return self._scenarios.pop(0)

    @property
    def all(self) -> list[Scenario]:
        """Return a list containing all scenario objects.

        Returns:
            All Scenario objects.
        """
        if self._scenario_name:
            scenarios = self._filter_for_scenario()
            self._verify()

            return scenarios

        scenarios = [c.scenario for c in self._configs]
        scenarios.sort(key=lambda x: x.directory)
        return scenarios

    def print_matrix(self) -> None:
        """Show the test matrix for all scenarios."""
        msg = "Test matrix"
        LOG.info(msg)

        tree = {}
        for scenario in self.all:
            tree[scenario.name] = list(scenario.sequence)
        util.print_as_yaml(tree)

    def sequence(self, scenario_name: str) -> list[str]:
        """Sequence for a given scenario.

        Args:
            scenario_name: Name of the scenario to determine the sequence of.

        Returns:
            A list of steps for that scenario.

        Raises:
            RuntimeError: If the scenario cannot be found.
        """
        for scenario in self.all:
            if scenario.name == scenario_name:
                return list(scenario.sequence)
        raise RuntimeError(  # noqa: TRY003
            f"Unable to find sequence for {scenario_name} scenario.",  # noqa: EM102
        )

    def _verify(self) -> None:
        """Verify the specified scenario was found."""
        scenario_names = [c.scenario.name for c in self._configs]
        if self._scenario_name not in scenario_names:
            msg = f"Scenario '{self._scenario_name}' not found.  Exiting."
            util.sysexit_with_message(msg)

    def _filter_for_scenario(self) -> list[Scenario]:
        """Find the scenario matching the provided scenario name and returns a list.

        Returns:
            list
        """
        return [c.scenario for c in self._configs if c.scenario.name == self._scenario_name]

    def _get_matrix(self) -> dict[str, dict[str, list[str]]]:
        """Build a matrix of scenarios and step sequences.

        Returns:
            A dictionary for each scenario listing action sequences for each step.
        """
        return {
            scenario.name: {
                "check": scenario.check_sequence,
                "cleanup": scenario.cleanup_sequence,
                "converge": scenario.converge_sequence,
                "create": scenario.create_sequence,
                "dependency": scenario.dependency_sequence,
                "destroy": scenario.destroy_sequence,
                "idempotence": scenario.idempotence_sequence,
                "prepare": scenario.prepare_sequence,
                "side_effect": scenario.side_effect_sequence,
                "syntax": scenario.syntax_sequence,
                "test": scenario.test_sequence,
                "verify": scenario.verify_sequence,
            }
            for scenario in self.all
        }

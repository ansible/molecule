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
        Return a list containing all config objects.

        :return: list
        """
        if self._scenario_name:
            configs = self._filter_configs_for_scenario(self._scenario_name)
            self._verify_scenario_name()

            return configs

        return self._configs

    def _verify_scenario_name(self):
        """
        Verify the specified scenario was found and returns None.

        :return: None
        """
        scenario_names = [c.scenario.name for c in self._configs]
        if self._scenario_name not in scenario_names:
            msg = ("Scenario '{}' not found.  Exiting."
                   ).format(self._scenario_name)
            util.sysexit_with_message(msg)

    def _filter_configs_for_scenario(self, scenario_name):
        """
        Find the config matching the provided scenario name and returns a list.

        :param scenario_name: A string representing the name of the scenario's
         config to return
        :return: list
        """

        return [c for c in self._configs if c.scenario.name == scenario_name]

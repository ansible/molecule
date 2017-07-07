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

import copy

import pytest

from molecule import scenarios


@pytest.fixture
def scenarios_instance(config_instance):
    config_instance_1 = copy.deepcopy(config_instance)
    config_instance_2 = copy.deepcopy(config_instance)
    config_instance_2.config['scenario']['name'] = 'foo'

    return scenarios.Scenarios([config_instance_1, config_instance_2])


def test_all_property(scenarios_instance):
    assert 2 == len(scenarios_instance.all)


def test_all_filters_on_scenario_name_property(scenarios_instance):
    scenarios_instance._scenario_name = 'default'

    assert 1 == len(scenarios_instance.all)


def test_verify_scenario_name_does_not_raise_when_found(scenarios_instance):
    scenarios_instance._scenario_name = 'default'

    assert scenarios_instance._verify_scenario_name() is None


def test_verify_scenario_name_raises_when_scenario_not_found(
        scenarios_instance, patched_logger_critical):
    scenarios_instance._scenario_name = 'invalid'
    with pytest.raises(SystemExit) as e:
        scenarios_instance._verify_scenario_name()

    assert 1 == e.value.code

    msg = "Scenario 'invalid' not found.  Exiting."
    patched_logger_critical.assert_called_once_with(msg)


def test_filter_configs_for_scenario(scenarios_instance):
    result = scenarios_instance._filter_configs_for_scenario('default')
    assert 1 == len(result)

    result = scenarios_instance._filter_configs_for_scenario('invalid')
    assert [] == result

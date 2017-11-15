#  Copyright (c) 2015-2017 Cisco Systems, Inc.
# -*- coding: utf-8 -*-
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

from molecule import config
from molecule import scenario
from molecule import scenarios


@pytest.fixture
def scenarios_instance(config_instance):
    config_instance_1 = copy.deepcopy(config_instance)

    config_instance_2 = copy.deepcopy(config_instance)
    config_instance_2.config['scenario']['name'] = 'foo'

    return scenarios.Scenarios([config_instance_1, config_instance_2])


def test_configs_private_member(scenarios_instance):
    assert 2 == len(scenarios_instance._configs)
    assert isinstance(scenarios_instance._configs[0], config.Config)
    assert isinstance(scenarios_instance._configs[1], config.Config)


def test_scenario_name_private_member(scenarios_instance):
    assert scenarios_instance._scenario_name is None


def test_scenarios_private_member(scenarios_instance):
    assert 2 == len(scenarios_instance._scenarios)
    assert isinstance(scenarios_instance._scenarios[0], scenario.Scenario)
    assert isinstance(scenarios_instance._scenarios[1], scenario.Scenario)


def test_scenarios_iterator(scenarios_instance):
    s = [scenario for scenario in scenarios_instance]

    assert 'default' == s[0].name
    assert 'foo' == s[1].name


def test_all_property(scenarios_instance):
    result = scenarios_instance.all

    assert 2 == len(result)
    assert 'default' == result[0].name
    assert 'foo' == result[1].name


def test_all_filters_on_scenario_name_property(scenarios_instance):
    scenarios_instance._scenario_name = 'default'

    assert 1 == len(scenarios_instance.all)


def test_print_matrix(mocker, patched_logger_info, patched_logger_out,
                      scenarios_instance):
    scenarios_instance.print_matrix()

    msg = 'Test matrix'
    patched_logger_info(msg)

    x = u"""
├── default
│   ├── lint
│   ├── destroy
│   ├── dependency
│   ├── syntax
│   ├── create
│   ├── prepare
│   ├── converge
│   ├── idempotence
│   ├── side_effect
│   ├── verify
│   └── destroy
└── foo
    ├── lint
    ├── destroy
    ├── dependency
    ├── syntax
    ├── create
    ├── prepare
    ├── converge
    ├── idempotence
    ├── side_effect
    ├── verify
    └── destroy
"""
    assert x.encode('utf-8') == patched_logger_out.mock_calls[0][1][0]
    assert mocker.call('') == patched_logger_out.mock_calls[1]


def test_verify_does_not_raise_when_found(scenarios_instance):
    scenarios_instance._scenario_name = 'default'

    assert scenarios_instance._verify() is None


def test_verify_raises_when_scenario_not_found(scenarios_instance,
                                               patched_logger_critical):
    scenarios_instance._scenario_name = 'invalid'
    with pytest.raises(SystemExit) as e:
        scenarios_instance._verify()

    assert 1 == e.value.code

    msg = "Scenario 'invalid' not found.  Exiting."
    patched_logger_critical.assert_called_once_with(msg)


def test_filter_for_scenario(scenarios_instance):
    scenarios_instance._scenario_name = 'default'
    result = scenarios_instance._filter_for_scenario()
    assert 1 == len(result)
    assert 'default' == result[0].name

    scenarios_instance._scenario_name = 'invalid'
    result = scenarios_instance._filter_for_scenario()
    assert [] == result


def test_get_matrix(scenarios_instance):
    x = {
        'default': {
            'lint': ['lint'],
            'idempotence': ['idempotence'],
            'syntax': ['syntax'],
            'converge': [
                'dependency',
                'create',
                'prepare',
                'converge',
            ],
            'check': [
                'destroy',
                'dependency',
                'create',
                'prepare',
                'converge',
                'check',
                'destroy',
            ],
            'verify': ['verify'],
            'create': [
                'create',
                'prepare',
            ],
            'prepare': ['prepare'],
            'side_effect': ['side_effect'],
            'dependency': ['dependency'],
            'test': [
                'lint',
                'destroy',
                'dependency',
                'syntax',
                'create',
                'prepare',
                'converge',
                'idempotence',
                'side_effect',
                'verify',
                'destroy',
            ],
            'destroy': ['destroy']
        },
        'foo': {
            'lint': ['lint'],
            'idempotence': ['idempotence'],
            'syntax': ['syntax'],
            'converge': [
                'dependency',
                'create',
                'prepare',
                'converge',
            ],
            'check': [
                'destroy',
                'dependency',
                'create',
                'prepare',
                'converge',
                'check',
                'destroy',
            ],
            'create': [
                'create',
                'prepare',
            ],
            'verify': ['verify'],
            'prepare': ['prepare'],
            'side_effect': ['side_effect'],
            'dependency': ['dependency'],
            'test': [
                'lint',
                'destroy',
                'dependency',
                'syntax',
                'create',
                'prepare',
                'converge',
                'idempotence',
                'side_effect',
                'verify',
                'destroy',
            ],
            'destroy': ['destroy']
        }
    }

    assert x == scenarios_instance._get_matrix()

#  Copyright (c) 2015-2018 Cisco Systems, Inc.
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

from molecule import config, scenario, scenarios
from molecule.console import console
from molecule.text import chomp, strip_ansi_escape


@pytest.fixture
def _instance(config_instance):
    config_instance_1 = copy.deepcopy(config_instance)

    config_instance_2 = copy.deepcopy(config_instance)
    config_instance_2.config["scenario"]["name"] = "foo"

    return scenarios.Scenarios([config_instance_1, config_instance_2])


def test_configs_private_member(_instance):
    assert 2 == len(_instance._configs)
    assert isinstance(_instance._configs[0], config.Config)
    assert isinstance(_instance._configs[1], config.Config)


def test_scenario_name_private_member(_instance):
    assert _instance._scenario_name is None


def test_scenarios_private_member(_instance):
    assert 2 == len(_instance._scenarios)
    assert isinstance(_instance._scenarios[0], scenario.Scenario)
    assert isinstance(_instance._scenarios[1], scenario.Scenario)


def test_scenarios_iterator(_instance):
    s = [scenario for scenario in _instance]

    assert "default" == s[0].name
    assert "foo" == s[1].name


def test_all_property(_instance):
    result = _instance.all

    assert 2 == len(result)
    assert "default" == result[0].name
    assert "foo" == result[1].name


def test_all_filters_on_scenario_name_property(_instance):
    _instance._scenario_name = "default"

    assert 1 == len(_instance.all)


def test_print_matrix(capsys, _instance):
    with console.capture() as capture:
        _instance.print_matrix()
    result = chomp(strip_ansi_escape(capture.get()))

    matrix_out = u"""---
default:
  - dependency
  - lint
  - cleanup
  - destroy
  - syntax
  - create
  - prepare
  - converge
  - idempotence
  - side_effect
  - verify
  - cleanup
  - destroy
foo:
  - dependency
  - lint
  - cleanup
  - destroy
  - syntax
  - create
  - prepare
  - converge
  - idempotence
  - side_effect
  - verify
  - cleanup
  - destroy"""
    assert matrix_out in result


def test_verify_does_not_raise_when_found(_instance):
    _instance._scenario_name = "default"

    assert _instance._verify() is None


def test_verify_raises_when_scenario_not_found(_instance, patched_logger_critical):
    _instance._scenario_name = "invalid"
    with pytest.raises(SystemExit) as e:
        _instance._verify()

    assert 1 == e.value.code

    msg = "Scenario 'invalid' not found.  Exiting."
    patched_logger_critical.assert_called_once_with(msg)


def test_filter_for_scenario(_instance):
    _instance._scenario_name = "default"
    result = _instance._filter_for_scenario()
    assert 1 == len(result)
    assert "default" == result[0].name

    _instance._scenario_name = "invalid"
    result = _instance._filter_for_scenario()
    assert [] == result


def test_get_matrix(_instance):
    matrix = {
        "default": {
            "lint": ["dependency", "lint"],
            "idempotence": ["idempotence"],
            "syntax": ["syntax"],
            "converge": ["dependency", "create", "prepare", "converge"],
            "cleanup": ["cleanup"],
            "check": [
                "dependency",
                "cleanup",
                "destroy",
                "create",
                "prepare",
                "converge",
                "check",
                "cleanup",
                "destroy",
            ],
            "verify": ["verify"],
            "create": ["dependency", "create", "prepare"],
            "prepare": ["prepare"],
            "side_effect": ["side_effect"],
            "dependency": ["dependency"],
            "test": [
                "dependency",
                "lint",
                "cleanup",
                "destroy",
                "syntax",
                "create",
                "prepare",
                "converge",
                "idempotence",
                "side_effect",
                "verify",
                "cleanup",
                "destroy",
            ],
            "destroy": ["dependency", "cleanup", "destroy"],
        },
        "foo": {
            "lint": ["dependency", "lint"],
            "idempotence": ["idempotence"],
            "syntax": ["syntax"],
            "converge": ["dependency", "create", "prepare", "converge"],
            "check": [
                "dependency",
                "cleanup",
                "destroy",
                "create",
                "prepare",
                "converge",
                "check",
                "cleanup",
                "destroy",
            ],
            "cleanup": ["cleanup"],
            "create": ["dependency", "create", "prepare"],
            "verify": ["verify"],
            "prepare": ["prepare"],
            "side_effect": ["side_effect"],
            "dependency": ["dependency"],
            "test": [
                "dependency",
                "lint",
                "cleanup",
                "destroy",
                "syntax",
                "create",
                "prepare",
                "converge",
                "idempotence",
                "side_effect",
                "verify",
                "cleanup",
                "destroy",
            ],
            "destroy": ["dependency", "cleanup", "destroy"],
        },
    }

    assert matrix == _instance._get_matrix()

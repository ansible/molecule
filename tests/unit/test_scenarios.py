#  Copyright (c) 2015-2018 Cisco Systems, Inc.  # noqa: D100
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
from __future__ import annotations

import copy

import pytest

from molecule import config, scenario, scenarios
from molecule.console import console
from molecule.text import chomp, strip_ansi_escape


@pytest.fixture
def _instance(config_instance: config.Config) -> scenarios.Scenarios:
    config_instance_1 = copy.deepcopy(config_instance)

    config_instance_2 = copy.deepcopy(config_instance)
    config_instance_2.config["scenario"]["name"] = "foo"

    return scenarios.Scenarios([config_instance_1, config_instance_2])


def test_configs_private_member(  # noqa: D103
    _instance: scenarios.Scenarios,  # noqa: PT019
) -> None:
    assert len(_instance._configs) == 2  # noqa: PLR2004
    assert isinstance(_instance._configs[0], config.Config)
    assert isinstance(_instance._configs[1], config.Config)


def test_scenario_name_private_member(  # noqa: D103
    _instance: scenarios.Scenarios,  # noqa: PT019
) -> None:
    assert _instance._scenario_names == []


def test_scenarios_private_member(  # noqa: D103
    _instance: scenarios.Scenarios,  # noqa: PT019
) -> None:
    assert len(_instance._scenarios) == 2  # noqa: PLR2004
    assert isinstance(_instance._scenarios[0], scenario.Scenario)
    assert isinstance(_instance._scenarios[1], scenario.Scenario)


def test_scenarios_iterator(  # noqa: D103
    _instance: scenarios.Scenarios,  # noqa: PT019
) -> None:
    s = list(_instance)

    assert s[0].name == "default"
    assert s[1].name == "foo"


def test_all_property(_instance: scenarios.Scenarios) -> None:  # noqa: PT019, D103
    result = _instance.all

    assert len(result) == 2  # noqa: PLR2004
    assert result[0].name == "default"
    assert result[1].name == "foo"


def test_all_filters_on_scenario_name_property(  # noqa: D103
    _instance: scenarios.Scenarios,  # noqa: PT019
) -> None:
    _instance._scenario_names = ["default"]

    assert len(_instance.all) == 1


def test_print_matrix(  # noqa: D103
    capsys: pytest.CaptureFixture[str],
    _instance: scenarios.Scenarios,  # noqa: PT019
) -> None:
    with console.capture() as capture:
        _instance.print_matrix()
    result = chomp(strip_ansi_escape(capture.get()))

    matrix_out = """---
default:
  - dependency
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


def test_verify_does_not_raise_when_found(  # noqa: D103
    _instance: scenarios.Scenarios,  # noqa: PT019
) -> None:
    _instance._scenario_names = ["default"]

    _instance._verify()


def test_verify_raises_when_scenario_not_found(  # noqa: D103
    _instance: scenarios.Scenarios,  # noqa: PT019
    caplog: pytest.LogCaptureFixture,
) -> None:
    _instance._scenario_names = ["invalid"]
    with pytest.raises(SystemExit) as e:
        _instance._verify()

    assert e.value.code == 1

    msg = "Scenario 'invalid' not found.  Exiting."
    assert msg in caplog.text


def test_verify_raises_when_multiple_scenarios_not_found(  # noqa: D103
    _instance: scenarios.Scenarios,  # noqa: PT019
    caplog: pytest.LogCaptureFixture,
) -> None:
    _instance._scenario_names = ["invalid", "also invalid"]
    with pytest.raises(SystemExit) as e:
        _instance._verify()

    assert e.value.code == 1

    msg = "Scenarios 'also invalid, invalid' not found.  Exiting."
    assert msg in caplog.text


def test_filter_for_scenario(  # noqa: D103
    _instance: scenarios.Scenarios,  # noqa: PT019
) -> None:
    _instance._scenario_names = ["default"]
    result = _instance._filter_for_scenario()
    assert len(result) == 1
    assert result[0].name == "default"

    _instance._scenario_names = ["invalid"]
    result = _instance._filter_for_scenario()
    assert result == []


def test_get_matrix(_instance: scenarios.Scenarios) -> None:  # noqa: PT019, D103
    matrix = {
        "default": {
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

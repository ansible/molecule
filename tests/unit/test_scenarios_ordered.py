#  Copyright (c) 2018 Marc Dequènes (Duck) <duck@redhat.com>  # noqa: D100
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

from molecule import config, scenarios


@pytest.fixture
def _instance(config_instance: config.Config):  # type: ignore[no-untyped-def]  # noqa: ANN202
    config_instance_1 = copy.deepcopy(config_instance)
    config_instance_1.config["scenario"]["name"] = "two"
    config_instance_1.molecule_file = config_instance_1.molecule_file.replace(
        "default",
        "02_foo",
    )

    config_instance_2 = copy.deepcopy(config_instance)
    config_instance_2.config["scenario"]["name"] = "one"
    config_instance_2.molecule_file = config_instance_2.molecule_file.replace(
        "default",
        "01_foo",
    )

    config_instance_3 = copy.deepcopy(config_instance)
    config_instance_3.config["scenario"]["name"] = "three"
    config_instance_3.molecule_file = config_instance_3.molecule_file.replace(
        "default",
        "03_foo",
    )

    return scenarios.Scenarios(
        [config_instance_1, config_instance_2, config_instance_3],
    )


def test_all_ordered(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN201, PT019, D103
    result = _instance.all

    assert len(result) == 3  # noqa: PLR2004
    assert result[0].name == "one"
    assert result[1].name == "two"
    assert result[2].name == "three"

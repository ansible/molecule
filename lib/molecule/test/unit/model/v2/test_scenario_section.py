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

import pytest

from molecule.model import schema_v3


@pytest.fixture
def _model_scenario_section_data():
    return {
        "scenario": {
            "name": "foo",
            "check_sequence": ["foo"],
            "converge_sequence": ["foo"],
            "create_sequence": ["foo"],
            "destroy_sequence": ["foo"],
            "test_sequence": ["foo"],
        }
    }


@pytest.mark.parametrize("_config", ["_model_scenario_section_data"], indirect=True)
def test_scenario(_config):
    assert {} == schema_v3.validate(_config)


@pytest.fixture
def _model_scenario_errors_section_data():
    return {
        "scenario": {
            "name": int(),
            "check_sequence": [int()],
            "converge_sequence": [int()],
            "create_sequence": [int()],
            "destroy_sequence": [int()],
            "test_sequence": [int()],
        }
    }


@pytest.mark.parametrize(
    "_config", ["_model_scenario_errors_section_data"], indirect=True
)
def test_scenario_has_errors(_config):
    x = {
        "scenario": [
            {
                "converge_sequence": [{0: ["must be of string type"]}],
                "check_sequence": [{0: ["must be of string type"]}],
                "create_sequence": [{0: ["must be of string type"]}],
                "destroy_sequence": [{0: ["must be of string type"]}],
                "test_sequence": [{0: ["must be of string type"]}],
            }
        ]
    }

    assert x == schema_v3.validate(_config)

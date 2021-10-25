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


@pytest.mark.parametrize(
    "_config", ["_model_platforms_delegated_section_data"], indirect=True
)
def test_platforms_delegated(_config):
    assert {} == schema_v3.validate(_config)


@pytest.mark.parametrize(
    "_config", ["_model_platforms_delegated_section_data"], indirect=True
)
def test_platforms_unique_names(_config):
    instance_name = _config["platforms"][0]["name"]
    _config["platforms"] += [{"name": instance_name}]  # duplicate platform name

    expected_validation_errors = {
        "platforms": [
            {
                0: [{"name": [f"'{instance_name}' is not unique"]}],
                1: [{"name": [f"'{instance_name}' is not unique"]}],
            }
        ]
    }

    assert expected_validation_errors == schema_v3.validate(_config)


def test_platforms_driver_name_required(_config):
    if "platforms" in _config:
        del _config["platforms"][0]["name"]
    else:
        _config["platforms"] = [{"foo": "bar"}]
    x = {"platforms": [{0: [{"name": ["required field"]}]}]}

    assert x == schema_v3.validate(_config)

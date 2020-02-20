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
def _model_driver_section_data():
    return {
        "driver": {
            "name": "docker",
            "provider": {"name": None},
            "options": {"managed": True, "foo": "bar"},
            "ssh_connection_options": ["foo", "bar"],
            "safe_files": ["foo", "bar"],
        }
    }


@pytest.mark.parametrize("_config", ["_model_driver_section_data"], indirect=True)
def test_driver(_config):
    assert {} == schema_v3.validate(_config)


@pytest.fixture
def _model_driver_errors_section_data():
    return {
        "driver": {
            "name": int(),
            "provider": {"name": int(), "foo": "bar"},
            "options": {"managed": str()},
            "ssh_connection_options": [int()],
            "safe_files": [int()],
        }
    }


@pytest.mark.parametrize(
    "_config", ["_model_driver_errors_section_data"], indirect=True
)
def test_driver_has_errors(_config):
    x = {
        "driver": [
            {
                "safe_files": [{0: ["must be of string type"]}],
                "options": [{"managed": ["must be of boolean type"]}],
                "ssh_connection_options": [{0: ["must be of string type"]}],
                "name": ["must be of string type"],
                "provider": [{"name": ["must be of string type"]}],
            }
        ]
    }

    assert x == schema_v3.validate(_config)


@pytest.fixture
def _model_driver_provider_name_nullable_section_data():
    return {"driver": {"provider": {"name": None}}}


@pytest.mark.parametrize(
    "_config", ["_model_driver_provider_name_nullable_section_data"], indirect=True
)
def test_driver_provider_name_nullable(_config):
    assert {} == schema_v3.validate(_config)


@pytest.fixture
def _model_driver_allows_delegated_section_data():
    return {"driver": {"name": "delegated"}}


@pytest.fixture
def _model_driver_allows_docker_section_data():
    return {"driver": {"name": "docker"}}


###
@pytest.mark.parametrize(
    "_config",
    [
        ("_model_driver_allows_delegated_section_data"),
        ("_model_driver_allows_docker_section_data"),
    ],
    indirect=True,
)
def test_driver_allows_name(_config):
    assert {} == schema_v3.validate(_config)

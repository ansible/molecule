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
def _model_dependency_section_data():
    return {
        "dependency": {
            "name": "galaxy",
            "enabled": True,
            "options": {"foo": "bar"},
            "env": {"FOO": "foo", "FOO_BAR": "foo_bar"},
        }
    }


@pytest.mark.parametrize("_config", ["_model_dependency_section_data"], indirect=True)
def test_dependency(_config):
    assert {} == schema_v3.validate(_config)


@pytest.fixture
def _model_dependency_errors_section_data():
    return {
        "dependency": {
            "name": int(),
            "command": None,
            "enabled": str(),
            "options": [],
            "env": {"foo": "foo", "foo-bar": "foo-bar"},
        }
    }


@pytest.mark.parametrize(
    "_config", ["_model_dependency_errors_section_data"], indirect=True
)
def test_dependency_has_errors(_config):
    x = {
        "dependency": [
            {
                "name": ["must be of string type"],
                "enabled": ["must be of boolean type"],
                "options": ["must be of dict type"],
                "env": [
                    {
                        "foo": ["value does not match regex '^[A-Z0-9_-]+$'"],
                        "foo-bar": ["value does not match regex '^[A-Z0-9_-]+$'"],
                    }
                ],
            }
        ]
    }

    assert x == schema_v3.validate(_config)


@pytest.fixture
def _model_dependency_allows_galaxy_section_data():
    return {"dependency": {"name": "galaxy"}}


@pytest.fixture
def _model_dependency_allows_gilt_section_data():
    return {"dependency": {"name": "gilt"}}


@pytest.fixture
def _model_dependency_allows_shell_section_data():
    return {"dependency": {"name": "shell"}}


@pytest.mark.parametrize(
    "_config",
    [
        ("_model_dependency_allows_galaxy_section_data"),
        ("_model_dependency_allows_gilt_section_data"),
        ("_model_dependency_allows_shell_section_data"),
    ],
    indirect=True,
)
def test_dependency_allows_shell_name(_config):
    assert {} == schema_v3.validate(_config)


@pytest.fixture
def _model_dependency_shell_errors_section_data():
    return {"dependency": {"name": "shell", "command": None}}


@pytest.mark.parametrize(
    "_config", ["_model_dependency_shell_errors_section_data"], indirect=True
)
def test_dependency_shell_has_errors(_config):
    x = {"dependency": [{"command": ["null value not allowed"]}]}

    assert x == schema_v3.validate(_config)

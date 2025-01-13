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

import pytest

from molecule.model import schema_v3


@pytest.fixture
def _model_dependency_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {
        "dependency": {
            "name": "galaxy",
            "enabled": True,
            "options": {"foo": "bar"},
            "env": {"FOO": "foo", "FOO_BAR": "foo_bar"},
        },
    }


@pytest.mark.parametrize(
    "config",
    ["_model_dependency_section_data"],  # noqa: PT007
    indirect=True,
)
def test_dependency(config):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    assert not schema_v3.validate(config)


@pytest.fixture
def _model_dependency_errors_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {"dependency": {"name": 0}}


@pytest.mark.parametrize(
    "config",
    ["_model_dependency_errors_section_data"],  # noqa: PT007
    indirect=True,
)
def test_dependency_has_errors(config):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    x = ["0 is not one of ['galaxy', 'shell']"]

    assert x == schema_v3.validate(config)


@pytest.fixture
def _model_dependency_allows_galaxy_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {"dependency": {"name": "galaxy"}}


@pytest.fixture
def _model_dependency_allows_shell_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {"dependency": {"name": "shell"}}


@pytest.mark.parametrize(
    "config",
    [  # noqa: PT007
        ("_model_dependency_allows_galaxy_section_data"),
        ("_model_dependency_allows_shell_section_data"),
    ],
    indirect=True,
)
def test_dependency_allows_shell_name(config):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    assert not schema_v3.validate(config)


@pytest.fixture
def _model_dependency_shell_errors_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {"dependency": {"name": "shell", "command": None}}


@pytest.mark.parametrize(
    "config",
    ["_model_dependency_shell_errors_section_data"],  # noqa: PT007
    indirect=True,
)
def test_dependency_shell_has_errors(config):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    x = ["None is not of type 'string'"]

    assert x == schema_v3.validate(config)

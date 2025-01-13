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
def _model_verifier_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {
        "verifier": {
            "name": "testinfra",
            "enabled": True,
            "directory": "foo",
            "options": {"foo": "bar"},
            "env": {"FOO": "foo", "FOO_BAR": "foo_bar"},
            "additional_files_or_dirs": ["foo"],
        },
    }


@pytest.mark.parametrize("config", ["_model_verifier_section_data"], indirect=True)  # noqa: PT007
def test_verifier(config):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    assert not schema_v3.validate(config)


@pytest.fixture
def _model_verifier_errors_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {
        "verifier": {
            "name": 0,
        },
    }


@pytest.mark.parametrize(
    "config",
    ["_model_verifier_errors_section_data"],  # noqa: PT007
    indirect=True,
)
def test_verifier_has_errors(config):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    x = ["0 is not one of ['ansible', 'goss', 'inspec', 'testinfra']"]

    assert x == schema_v3.validate(config)


@pytest.fixture
def _model_verifier_allows_testinfra_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {"verifier": {"name": "testinfra"}}


@pytest.fixture
def _model_verifier_allows_ansible_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {"verifier": {"name": "ansible"}}


@pytest.mark.parametrize(
    "config",
    [  # noqa: PT007
        ("_model_verifier_allows_testinfra_section_data"),
        ("_model_verifier_allows_ansible_section_data"),
    ],
    indirect=True,
)
def test_verifier_allows_name(config):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    assert not schema_v3.validate(config)

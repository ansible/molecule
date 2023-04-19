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


@pytest.fixture()
def _model_provisioner_section_data():
    return {
        "provisioner": {
            "name": "ansible",
            "log": True,
            "config_options": {"foo": "bar"},
            "connection_options": {"foo": "bar"},
            "options": {"foo": "bar"},
            "env": {"FOO": "foo", "FOO_BAR": "foo_bar"},
            "inventory": {
                "hosts": {"foo": "bar"},
                "host_vars": {"foo": "bar"},
                "group_vars": {"foo": "bar"},
                "links": {"foo": "bar"},
            },
            "children": {"foo": "bar"},
            "playbooks": {
                "create": "foo.yml",
                "converge": "bar.yml",
                "destroy": "baz.yml",
                "prepare": "qux.yml",
                "side_effect": "quux.yml",
                "foo": {"foo": "bar"},
            },
        },
    }


@pytest.mark.parametrize("_config", ["_model_provisioner_section_data"], indirect=True)
def test_provisioner(_config):
    assert not schema_v3.validate(_config)


@pytest.fixture()
def _model_provisioner_errors_section_data():
    return {
        "provisioner": {
            "name": 0,
        },
    }


@pytest.mark.parametrize(
    "_config",
    ["_model_provisioner_errors_section_data"],
    indirect=True,
)
def test_provisioner_has_errors(_config):
    x = ["0 is not one of ['ansible']"]

    assert x == schema_v3.validate(_config)


@pytest.fixture()
def _model_provisioner_allows_ansible_section_data():
    return {"provisioner": {"name": "ansible"}}


@pytest.mark.parametrize(
    "_config",
    [("_model_provisioner_allows_ansible_section_data")],
    indirect=True,
)
def test_provisioner_allows_name(_config):
    assert not schema_v3.validate(_config)

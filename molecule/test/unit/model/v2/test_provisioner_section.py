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
        }
    }


@pytest.mark.parametrize("_config", ["_model_provisioner_section_data"], indirect=True)
def test_provisioner(_config):
    assert {} == schema_v3.validate(_config)


@pytest.fixture
def _model_provisioner_errors_section_data():
    return {
        "provisioner": {
            "name": int(),
            "log": int,
            "config_options": [],
            "connection_options": [],
            "options": [],
            "env": {"foo": "foo", "foo-bar": "foo-bar", "foo-bar-baz": None},
            "inventory": {"hosts": [], "host_vars": [], "group_vars": [], "links": []},
            "children": [],
            "playbooks": {
                "create": int(),
                "converge": int(),
                "destroy": int(),
                "prepare": int(),
                "side_effect": int(),
            },
        }
    }


@pytest.mark.parametrize(
    "_config", ["_model_provisioner_errors_section_data"], indirect=True
)
def test_provisioner_has_errors(_config):
    x = {
        "provisioner": [
            {
                "config_options": ["must be of dict type"],
                "connection_options": ["must be of dict type"],
                "playbooks": [
                    {
                        "destroy": ["must be of string type"],
                        "create": ["must be of string type"],
                        "side_effect": ["must be of string type"],
                        "prepare": ["must be of string type"],
                        "converge": ["must be of string type"],
                    }
                ],
                "children": ["must be of dict type"],
                "inventory": [
                    {
                        "hosts": ["must be of dict type"],
                        "group_vars": ["must be of dict type"],
                        "host_vars": ["must be of dict type"],
                        "links": ["must be of dict type"],
                    }
                ],
                "env": [
                    {
                        "foo": ["value does not match regex '^[A-Z0-9_-]+$'"],
                        "foo-bar": ["value does not match regex '^[A-Z0-9_-]+$'"],
                        "foo-bar-baz": [
                            "value does not match regex '^[A-Z0-9_-]+$'",
                            "null value not allowed",
                        ],
                    }
                ],
                "options": ["must be of dict type"],
                "name": ["must be of string type"],
                "log": ["must be of boolean type"],
            }
        ]
    }

    assert x == schema_v3.validate(_config)


@pytest.fixture
def _model_provisioner_config_options_disallowed_section_data():
    return {
        "provisioner": {
            "config_options": {
                "defaults": {
                    "roles_path": "foo",
                    "library": "foo",
                    "filter_plugins": "foo",
                    "foo": "bar",
                },
                "foo": {"foo": "bar"},
                "privilege_escalation": {"foo": "bar"},
            }
        }
    }


@pytest.mark.parametrize(
    "_config",
    ["_model_provisioner_config_options_disallowed_section_data"],
    indirect=True,
)
def test_provisioner_config_options_disallowed_field(_config):
    x = {
        "provisioner": [
            {
                "config_options": [
                    {
                        "defaults": [
                            {
                                "filter_plugins": [
                                    "disallowed user provided config option"
                                ],
                                "library": ["disallowed user provided config option"],
                                "roles_path": [
                                    "disallowed user provided config option"
                                ],
                            }
                        ],
                        "privilege_escalation": [
                            "disallowed user provided config option"
                        ],
                    }
                ]
            }
        ]
    }

    assert x == schema_v3.validate(_config)


@pytest.fixture
def _model_provisioner_env_disallowed_section_data():
    return {
        "provisioner": {
            "env": {
                "ANSIBLE_BECOME": str(),
                "ANSIBLE_BECOME_METHOD": str(),
                "ANSIBLE_BECOME_USER": str(),
            }
        }
    }


@pytest.mark.parametrize(
    "_config", ["_model_provisioner_env_disallowed_section_data"], indirect=True
)
def test_provisioner_config_env_disallowed_field(_config):
    x = {
        "provisioner": [
            {
                "env": [
                    {
                        "ANSIBLE_BECOME_METHOD": [
                            "disallowed user provided config option"
                        ],
                        "ANSIBLE_BECOME": ["disallowed user provided config option"],
                        "ANSIBLE_BECOME_USER": [
                            "disallowed user provided config option"
                        ],
                    }
                ]
            }
        ]
    }

    assert x == schema_v3.validate(_config)


@pytest.fixture
def _model_provisioner_allows_ansible_section_data():
    return {"provisioner": {"name": "ansible"}}


@pytest.mark.parametrize(
    "_config", [("_model_provisioner_allows_ansible_section_data")], indirect=True
)
def test_provisioner_allows_name(_config):
    assert {} == schema_v3.validate(_config)

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
"""Schema v2 Validation Module."""

import collections
import functools
import re
from typing import Any, MutableMapping

import cerberus
import cerberus.errors

from molecule import api, interpolation, util


def coerce_env(env, keep_string, v):
    """Interpolate environment."""
    i = interpolation.Interpolator(interpolation.TemplateWithDefaults, env)

    return i.interpolate(v, keep_string)


def pre_validate_base_schema(env: MutableMapping, keep_string: str):
    """Pre-validate base schema."""
    return {
        "dependency": {
            "type": "dict",
            "schema": {
                "name": {
                    "type": "string",
                    "molecule_env_var": True,
                    "allowed": ["galaxy", "shell"],
                }
            },
        },
        "driver": {
            "type": "dict",
            "schema": {
                "name": {
                    "type": "string",
                    "molecule_env_var": True,
                    "allowed": api.drivers(),
                    # NOTE(retr0h): Some users use an environment variable to
                    # change the driver name.  May add this coercion to rest of
                    # config using allowed validation.
                    "coerce": (str, functools.partial(coerce_env, env, keep_string)),
                }
            },
        },
        "lint": {"type": "string"},
        "platforms": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "registry": {
                        "type": "dict",
                        "schema": {
                            "credentials": {
                                "type": "dict",
                                "schema": {"password": {"type": "string"}},
                            }
                        },
                    }
                },
            },
        },
        "provisioner": {
            "type": "dict",
            "schema": {
                "name": {
                    "type": "string",
                    "molecule_env_var": True,
                    "allowed": ["ansible"],
                },
            },
        },
        "scenario": {"type": "dict", "schema": {"name": {"molecule_env_var": True}}},
        "verifier": {
            "type": "dict",
            "schema": {
                "name": {
                    "type": "string",
                    "molecule_env_var": True,
                    "allowed": api.verifiers(),
                },
            },
        },
    }


base_schema = {
    "dependency": {
        "type": "dict",
        "schema": {
            "name": {"type": "string"},
            "enabled": {"type": "boolean"},
            "options": {"type": "dict"},
            "env": {
                "type": "dict",
                "keysrules": {"type": "string", "regex": "^[A-Z0-9_-]+$"},
            },
            "command": {"type": "string", "nullable": True},
        },
    },
    "driver": {
        "type": "dict",
        "schema": {
            "name": {"type": "string"},
            "provider": {
                "type": "dict",
                "schema": {"name": {"type": "string", "nullable": True}},
            },
            "options": {"type": "dict", "schema": {"managed": {"type": "boolean"}}},
            "ssh_connection_options": {"type": "list", "schema": {"type": "string"}},
            "safe_files": {"type": "list", "schema": {"type": "string"}},
        },
    },
    "lint": {"type": "string"},
    "platforms": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "name": {
                    "type": "string",
                    "required": True,
                    "unique": True,  # https://github.com/pyeve/cerberus/issues/467
                },
                "groups": {"type": "list", "schema": {"type": "string"}},
                "children": {"type": "list", "schema": {"type": "string"}},
            },
        },
    },
    "provisioner": {
        "type": "dict",
        "schema": {
            "name": {"type": "string"},
            "log": {"type": "boolean"},
            "config_options": {
                "type": "dict",
                "schema": {
                    "defaults": {
                        "type": "dict",
                        "schema": {
                            "roles_path": {"type": "string", "disallowed": True},
                            "library": {"type": "string", "disallowed": True},
                            "filter_plugins": {"type": "string", "disallowed": True},
                        },
                    },
                    "privilege_escalation": {"type": "dict", "disallowed": True},
                },
            },
            "connection_options": {"type": "dict"},
            "options": {"type": "dict"},
            "env": {
                "type": "dict",
                "keysrules": {"type": "string", "regex": "^[A-Z0-9_-]+$"},
                "valuesrules": {"nullable": False},
                "schema": {
                    "ANSIBLE_BECOME": {"type": "string", "disallowed": True},
                    "ANSIBLE_BECOME_METHOD": {"type": "string", "disallowed": True},
                    "ANSIBLE_BECOME_USER": {"type": "string", "disallowed": True},
                },
            },
            "inventory": {
                "type": "dict",
                "schema": {
                    "hosts": {"type": "dict"},
                    "host_vars": {"type": "dict"},
                    "group_vars": {"type": "dict"},
                    "links": {"type": "dict"},
                },
            },
            "children": {"type": "dict"},
            "playbooks": {
                "type": "dict",
                "schema": {
                    "cleanup": {"type": "string"},
                    "create": {"type": "string"},
                    "converge": {"type": "string"},
                    "destroy": {"type": "string"},
                    "prepare": {"type": "string"},
                    "side_effect": {"type": "string"},
                    "verify": {"type": "string"},
                },
            },
        },
    },
    "scenario": {
        "type": "dict",
        "schema": {
            "check_sequence": {"type": "list", "schema": {"type": "string"}},
            "converge_sequence": {"type": "list", "schema": {"type": "string"}},
            "create_sequence": {"type": "list", "schema": {"type": "string"}},
            "destroy_sequence": {"type": "list", "schema": {"type": "string"}},
            "test_sequence": {"type": "list", "schema": {"type": "string"}},
        },
    },
    "verifier": {
        "type": "dict",
        "schema": {
            "name": {"type": "string"},
            "enabled": {"type": "boolean"},
            "options": {"type": "dict"},
            "env": {
                "type": "dict",
                "keysrules": {"type": "string", "regex": "^[A-Z0-9_-]+$"},
            },
            "directory": {"type": "string"},
            "additional_files_or_dirs": {"type": "list", "schema": {"type": "string"}},
        },
    },
}

platforms_docker_schema = {
    "platforms": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string"},
                "hostname": {"type": "string"},
                "image": {"type": "string"},
                "dockerfile": {"type": "string"},
                "pull": {"type": "boolean"},
                "pre_build_image": {"type": "boolean"},
                "registry": {
                    "type": "dict",
                    "schema": {
                        "url": {"type": "string"},
                        "credentials": {
                            "type": "dict",
                            "schema": {
                                "username": {"type": "string"},
                                "password": {"type": "string"},
                                "email": {"type": "string"},
                            },
                        },
                    },
                },
                "override_command": {"type": "boolean", "nullable": True},
                "command": {"type": "string", "nullable": True},
                "tty": {"type": "boolean", "nullable": True},
                "pid_mode": {"type": "string"},
                "privileged": {"type": "boolean"},
                "security_opts": {"type": "list", "schema": {"type": "string"}},
                "volumes": {"type": "list", "schema": {"type": "string"}},
                "keep_volumes": {"type": "boolean"},
                "tmpfs": {"type": "list", "schema": {"type": "string"}},
                "capabilities": {"type": "list", "schema": {"type": "string"}},
                "sysctls": {"type": "dict", "keysrules": {"type": "string"}},
                "exposed_ports": {
                    "type": "list",
                    "schema": {"type": "string", "coerce": "exposed_ports"},
                },
                "published_ports": {"type": "list", "schema": {"type": "string"}},
                "user": {"type": "string"},
                "ulimits": {"type": "list", "schema": {"type": "string"}},
                "dns_servers": {"type": "list", "schema": {"type": "string"}},
                "etc_hosts": {
                    "type": ["string", "dict"],
                    "keysrules": {"type": "string"},
                },
                "env": {
                    "type": "dict",
                    "keysrules": {"type": "string", "regex": "^[a-zA-Z0-9._-]+$"},
                },
                "restart_policy": {"type": "string"},
                "restart_retries": {"type": "integer"},
                "networks": {
                    "type": "list",
                    "schema": {"type": "dict", "schema": {"name": {"type": "string"}}},
                },
                "network_mode": {"type": "string"},
                "purge_networks": {"type": "boolean"},
                "docker_host": {"type": "string"},
                "cacert_path": {"type": "string"},
                "cert_path": {"type": "string"},
                "key_path": {"type": "string"},
                "tls_verify": {"type": "boolean"},
            },
        },
    }
}


dependency_command_nullable_schema = {
    "dependency": {
        "type": "dict",
        "schema": {"command": {"type": "string", "nullable": False}},
    }
}


class Validator(cerberus.Validator):
    """Validator Class."""

    def __init__(self, *args: Any, **kwargs: Any):
        """Construct Validator."""
        super(Validator, self).__init__(*args, **kwargs)

    def _validate_unique(self, unique, field, value):
        """Ensure value uniqueness.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if unique:
            root_key = self.schema_path[0]
            data = (doc[field] for doc in self.root_document[root_key])
            for key, count in collections.Counter(data).items():
                if count > 1:
                    msg = "'{}' is not unique".format(key)
                    self._error(field, msg)

    def _validate_disallowed(self, disallowed, field, value):
        """Readonly but with a custom error.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if disallowed:
            msg = "disallowed user provided config option"
            self._error(field, msg)

    def _normalize_coerce_exposed_ports(self, value):
        """Coerce ``exposed_ports`` values to string.

        Not all types that can be specified by the user are acceptable and
        therefore we cannot simply pass a ``'coerce': 'string'`` to the schema
        definition.
        """
        if type(value) == int:
            return str(value)
        return value

    def _validate_molecule_env_var(self, molecule_env_var, field, value):
        """Readonly but with a custom error.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        # TODO(retr0h): This needs to be better handled.
        pattern = r"^[{$]+MOLECULE[_a-z0-9A-Z]+[}]*$"

        if molecule_env_var:
            if re.match(pattern, value):
                msg = "cannot reference $MOLECULE special variables " "in this section"
                self._error(field, msg)


def pre_validate(stream, env: MutableMapping, keep_string: str):
    """Pre-validate stream."""
    data = util.safe_load(stream)

    v = Validator(allow_unknown=True)
    v.validate(data, pre_validate_base_schema(env, keep_string))

    return v.errors, data


def validate(c):
    """Perform schema validation."""
    schema = base_schema

    # Dependency
    if c["dependency"]["name"] == "shell":
        schema = util.merge_dicts(schema, dependency_command_nullable_schema)

    # Verifier
    schema = util.merge_dicts(schema, api.verifiers()[c["verifier"]["name"]].schema())

    v = Validator(allow_unknown=True)
    v.validate(c, schema)

    return v.errors

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

import collections
import copy
import functools
import re

import cerberus
import cerberus.errors

from molecule import interpolation, util


def coerce_env(env, keep_string, v):
    i = interpolation.Interpolator(interpolation.TemplateWithDefaults, env)

    return i.interpolate(v, keep_string)


def pre_validate_base_schema(env, keep_string):
    return {
        'dependency': {
            'type': 'dict',
            'schema': {
                'name': {
                    'type': 'string',
                    'molecule_env_var': True,
                    'allowed': [
                        'galaxy',
                        'gilt',
                        'shell',
                    ],
                },
            }
        },
        'driver': {
            'type': 'dict',
            'schema': {
                'name': {
                    'type':
                    'string',
                    'molecule_env_var':
                    True,
                    'allowed': [
                        'azure',
                        'delegated',
                        'digitalocean',
                        'docker',
                        'ec2',
                        'gce',
                        'linode',
                        'lxc',
                        'lxd',
                        'openstack',
                        'vagrant',
                    ],
                    # NOTE(retr0h): Some users use an environment variable to
                    # change the driver name.  May add this coercion to rest of
                    # config using allowed validation.
                    'coerce': (str,
                               functools.partial(coerce_env, env, keep_string))
                },
            }
        },
        'lint': {
            'type': 'dict',
            'schema': {
                'name': {
                    'type': 'string',
                    'molecule_env_var': True,
                    'allowed': [
                        'yamllint',
                    ],
                },
            }
        },
        'platforms': {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': {
                    'registry': {
                        'type': 'dict',
                        'schema': {
                            'credentials': {
                                'type': 'dict',
                                'schema': {
                                    'password': {
                                        'type': 'string'
                                    },
                                }
                            },
                        }
                    },
                }
            }
        },
        'provisioner': {
            'type': 'dict',
            'schema': {
                'name': {
                    'type': 'string',
                    'molecule_env_var': True,
                    'allowed': [
                        'ansible',
                    ],
                },
                'lint': {
                    'type': 'dict',
                    'schema': {
                        'name': {
                            'type': 'string',
                            'molecule_env_var': True,
                            'allowed': [
                                'ansible-lint',
                            ],
                        },
                    }
                },
            }
        },
        'scenario': {
            'type': 'dict',
            'schema': {
                'name': {
                    'type': 'string',
                    'molecule_env_var': True,
                },
            }
        },
        'verifier': {
            'type': 'dict',
            'schema': {
                'name': {
                    'type': 'string',
                    'molecule_env_var': True,
                    'allowed': [
                        'testinfra',
                        'inspec',
                        'goss',
                        'ansible',
                    ],
                },
                'lint': {
                    'type': 'dict',
                    'schema': {
                        'name': {
                            'type':
                            'string',
                            'molecule_env_var':
                            True,
                            'allowed': [
                                'flake8',
                                'rubocop',
                                'yamllint',
                                'ansible-lint',
                            ],
                        },
                    }
                },
            }
        },
    }


base_schema = {
    'dependency': {
        'type': 'dict',
        'schema': {
            'name': {
                'type': 'string',
            },
            'enabled': {
                'type': 'boolean',
            },
            'options': {
                'type': 'dict',
            },
            'env': {
                'type': 'dict',
                'keyschema': {
                    'type': 'string',
                    'regex': '^[A-Z0-9_-]+$',
                },
            },
            'command': {
                'type': 'string',
                'nullable': True,
            },
        }
    },
    'driver': {
        'type': 'dict',
        'schema': {
            'name': {
                'type': 'string',
            },
            'provider': {
                'type': 'dict',
                'schema': {
                    'name': {
                        'type': 'string',
                        'nullable': True,
                    },
                }
            },
            'options': {
                'type': 'dict',
                'schema': {
                    'managed': {
                        'type': 'boolean',
                    },
                }
            },
            'ssh_connection_options': {
                'type': 'list',
                'schema': {
                    'type': 'string',
                }
            },
            'safe_files': {
                'type': 'list',
                'schema': {
                    'type': 'string',
                }
            },
        }
    },
    'lint': {
        'type': 'dict',
        'schema': {
            'name': {
                'type': 'string',
            },
            'enabled': {
                'type': 'boolean',
            },
            'options': {
                'type': 'dict',
            },
            'env': {
                'type': 'dict',
                'keyschema': {
                    'type': 'string',
                    'regex': '^[A-Z0-9_-]+$',
                },
            },
        }
    },
    'platforms': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'name': {
                    'type': 'string',
                    'required': True,
                    'unique':  # https://github.com/pyeve/cerberus/issues/467
                    True,
                },
                'groups': {
                    'type': 'list',
                    'schema': {
                        'type': 'string',
                    }
                },
                'children': {
                    'type': 'list',
                    'schema': {
                        'type': 'string',
                    }
                },
            }
        }
    },
    'provisioner': {
        'type': 'dict',
        'schema': {
            'name': {
                'type': 'string',
            },
            'log': {
                'type': 'boolean',
            },
            'config_options': {
                'type': 'dict',
                'schema': {
                    'defaults': {
                        'type': 'dict',
                        'schema': {
                            'roles_path': {
                                'type': 'string',
                                'disallowed': True,
                            },
                            'library': {
                                'type': 'string',
                                'disallowed': True,
                            },
                            'filter_plugins': {
                                'type': 'string',
                                'disallowed': True,
                            },
                        }
                    },
                    'privilege_escalation': {
                        'type': 'dict',
                        'disallowed': True,
                    },
                }
            },
            'connection_options': {
                'type': 'dict',
            },
            'options': {
                'type': 'dict',
            },
            'env': {
                'type': 'dict',
                'keyschema': {
                    'type': 'string',
                    'regex': '^[A-Z0-9_-]+$',
                },
                'valueschema': {
                    'nullable': False,
                },
                'schema': {
                    'ANSIBLE_BECOME': {
                        'type': 'string',
                        'disallowed': True,
                    },
                    'ANSIBLE_BECOME_METHOD': {
                        'type': 'string',
                        'disallowed': True,
                    },
                    'ANSIBLE_BECOME_USER': {
                        'type': 'string',
                        'disallowed': True,
                    },
                }
            },
            'inventory': {
                'type': 'dict',
                'schema': {
                    'hosts': {
                        'type': 'dict',
                    },
                    'host_vars': {
                        'type': 'dict',
                    },
                    'group_vars': {
                        'type': 'dict',
                    },
                    'links': {
                        'type': 'dict',
                    },
                }
            },
            'children': {
                'type': 'dict',
            },
            'playbooks': {
                'type': 'dict',
                'schema': {
                    'cleanup': {
                        'type': 'string',
                    },
                    'create': {
                        'type': 'string',
                    },
                    'converge': {
                        'type': 'string',
                    },
                    'destroy': {
                        'type': 'string',
                    },
                    'prepare': {
                        'type': 'string',
                    },
                    'side_effect': {
                        'type': 'string',
                    },
                    'verify': {
                        'type': 'string',
                    },
                }
            },
            'lint': {
                'type': 'dict',
                'schema': {
                    'name': {
                        'type': 'string',
                    },
                    'enabled': {
                        'type': 'boolean',
                    },
                    'options': {
                        'type': 'dict',
                    },
                    'env': {
                        'type': 'dict',
                        'keyschema': {
                            'type': 'string',
                            'regex': '^[A-Z0-9_-]+$',
                        },
                    },
                }
            },
        }
    },
    'scenario': {
        'type': 'dict',
        'schema': {
            'name': {
                'type': 'string',
            },
            'check_sequence': {
                'type': 'list',
                'schema': {
                    'type': 'string',
                }
            },
            'converge_sequence': {
                'type': 'list',
                'schema': {
                    'type': 'string',
                }
            },
            'create_sequence': {
                'type': 'list',
                'schema': {
                    'type': 'string',
                }
            },
            'destroy_sequence': {
                'type': 'list',
                'schema': {
                    'type': 'string',
                }
            },
            'test_sequence': {
                'type': 'list',
                'schema': {
                    'type': 'string',
                }
            },
        }
    },
    'verifier': {
        'type': 'dict',
        'schema': {
            'name': {
                'type': 'string',
            },
            'enabled': {
                'type': 'boolean',
            },
            'options': {
                'type': 'dict',
            },
            'env': {
                'type': 'dict',
                'keyschema': {
                    'type': 'string',
                    'regex': '^[A-Z0-9_-]+$',
                },
            },
            'directory': {
                'type': 'string',
            },
            'additional_files_or_dirs': {
                'type': 'list',
                'schema': {
                    'type': 'string',
                }
            },
            'lint': {
                'type': 'dict',
                'schema': {
                    'name': {
                        'type': 'string',
                    },
                    'enabled': {
                        'type': 'boolean',
                    },
                    'options': {
                        'type': 'dict',
                    },
                    'env': {
                        'type': 'dict',
                        'keyschema': {
                            'type': 'string',
                            'regex': '^[A-Z0-9_-]+$',
                        },
                    },
                }
            },
        }
    },
}

driver_vagrant_provider_section_schema = {
    'driver': {
        'type': 'dict',
        'schema': {
            'name': {
                'type': 'string',
            },
            'provider': {
                'type': 'dict',
                'schema': {
                    'name': {
                        'type':
                        'string',
                        'nullable':
                        False,
                        'allowed': [
                            'virtualbox',
                            'vmware_fusion',
                            'vmware_workstation',
                            'vmware_desktop',
                            'parallels',
                            'libvirt',
                        ],
                    },
                }
            },
        }
    },
}

platforms_vagrant_schema = {
    'platforms': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'name': {
                    'type': 'string',
                },
                'interfaces': {
                    'type': 'list',
                    'schema': {
                        'type': 'dict',
                    }
                },
                'instance_raw_config_args': {
                    'type': 'list',
                    'schema': {
                        'type': 'string',
                    }
                },
                'config_options': {
                    'type': 'dict',
                },
                'box': {
                    'type': 'string',
                },
                'box_version': {
                    'type': 'string',
                },
                'box_url': {
                    'type': 'string',
                },
                'memory': {
                    'type': 'integer',
                },
                'cpus': {
                    'type': 'integer',
                },
                'provider_options': {
                    'type': 'dict',
                },
                'provider_raw_config_args': {
                    'type': 'list',
                    'schema': {
                        'type': 'string',
                    }
                },
                'provision': {
                    'type': 'boolean',
                },
            }
        }
    },
}

platforms_docker_schema = {
    'platforms': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'name': {
                    'type': 'string',
                },
                'hostname': {
                    'type': 'string',
                },
                'image': {
                    'type': 'string',
                },
                'dockerfile': {
                    'type': 'string',
                },
                'pull': {
                    'type': 'boolean',
                },
                'pre_build_image': {
                    'type': 'boolean',
                },
                'registry': {
                    'type': 'dict',
                    'schema': {
                        'url': {
                            'type': 'string',
                        },
                        'credentials': {
                            'type': 'dict',
                            'schema': {
                                'username': {
                                    'type': 'string',
                                },
                                'password': {
                                    'type': 'string',
                                },
                                'email': {
                                    'type': 'string',
                                },
                            }
                        },
                    }
                },
                'override_command': {
                    'type': 'boolean',
                    'nullable': True,
                },
                'command': {
                    'type': 'string',
                    'nullable': True,
                },
                'tty': {
                    'type': 'boolean',
                    'nullable': True,
                },
                'pid_mode': {
                    'type': 'string',
                },
                'privileged': {
                    'type': 'boolean',
                },
                'security_opts': {
                    'type': 'list',
                    'schema': {
                        'type': 'string',
                    }
                },
                'volumes': {
                    'type': 'list',
                    'schema': {
                        'type': 'string',
                    }
                },
                'tmpfs': {
                    'type': 'list',
                    'schema': {
                        'type': 'string',
                    }
                },
                'capabilities': {
                    'type': 'list',
                    'schema': {
                        'type': 'string',
                    }
                },
                'exposed_ports': {
                    'type': 'list',
                    'schema': {
                        'type': 'string',
                        'coerce': 'exposed_ports'
                    }
                },
                'published_ports': {
                    'type': 'list',
                    'schema': {
                        'type': 'string',
                    }
                },
                'ulimits': {
                    'type': 'list',
                    'schema': {
                        'type': 'string',
                    }
                },
                'dns_servers': {
                    'type': 'list',
                    'schema': {
                        'type': 'string',
                    }
                },
                'env': {
                    'type': 'dict',
                    'keyschema': {
                        'type': 'string',
                        'regex': '^[a-zA-Z0-9_-]+$',
                    }
                },
                'restart_policy': {
                    'type': 'string',
                },
                'restart_retries': {
                    'type': 'integer',
                },
                'networks': {
                    'type': 'list',
                    'schema': {
                        'type': 'dict',
                        'schema': {
                            'name': {
                                'type': 'string',
                            },
                        }
                    }
                },
                'network_mode': {
                    'type': 'string',
                },
                'purge_networks': {
                    'type': 'boolean',
                }
            }
        }
    },
}

platforms_lxd_schema = {
    'platforms': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'name': {
                    'type': 'string',
                },
                'url': {
                    'type': 'string',
                },
                'cert_file': {
                    'type': 'string',
                },
                'key_file': {
                    'type': 'string',
                },
                'trust_password': {
                    'type': 'string',
                },
                'source': {
                    'type': 'dict',
                    'schema': {
                        'type': {
                            'type': 'string',
                        },
                        'mode': {
                            'type': 'string',
                            'allowed': [
                                'pull',
                                'local',
                            ],
                        },
                        'server': {
                            'type': 'string',
                        },
                        'protocol': {
                            'type': 'string',
                            'allowed': [
                                'lxd',
                                'simplestreams',
                            ],
                        },
                        'alias': {
                            'type': 'string',
                        },
                    },
                },
                'architecture': {
                    'type': 'string',
                    'allowed': [
                        'x86_64',
                        'i686',
                    ],
                },
                'config': {
                    'type': 'dict',
                    'allow_unknown': True,
                },
                'devices': {
                    'type': 'dict',
                    'allow_unknown': True,
                },
                'profiles': {
                    'type': 'list',
                    'schema': {
                        'type': 'string'
                    }
                },
                'force_stop': {
                    'type': 'boolean',
                },
            }
        }
    },
}

platforms_linode_schema = {
    'platforms': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'name': {
                    'type': 'string',
                },
                'plan': {
                    'type': 'integer',
                    'required': True,
                },
                'datacenter': {
                    'type': 'integer',
                    'required': True,
                },
                'distribution': {
                    'type': 'integer',
                    'required': True,
                },
            },
        },
    },
}

dependency_command_nullable_schema = {
    'dependency': {
        'type': 'dict',
        'schema': {
            'command': {
                'type': 'string',
                'nullable': False,
            },
        }
    },
}

verifier_options_readonly_schema = {
    'verifier': {
        'type': 'dict',
        'schema': {
            'options': {
                'keyschema': {
                    'readonly': True,
                },
            },
        }
    },
}

verifier_goss_mutually_exclusive_schema = {
    'verifier': {
        'type': 'dict',
        'schema': {
            'name': {
                'type': 'string',
                'allowed': [
                    'goss',
                ],
            },
            'lint': {
                'type': 'dict',
                'schema': {
                    'name': {
                        'type': 'string',
                        'allowed': [
                            'yamllint',
                        ],
                    },
                }
            },
        }
    },
}

verifier_inspec_mutually_exclusive_schema = {
    'verifier': {
        'type': 'dict',
        'schema': {
            'name': {
                'type': 'string',
                'allowed': [
                    'inspec',
                ],
            },
            'lint': {
                'type': 'dict',
                'schema': {
                    'name': {
                        'type': 'string',
                        'allowed': [
                            'rubocop',
                        ],
                    },
                }
            },
        }
    },
}
verifier_testinfra_mutually_exclusive_schema = {
    'verifier': {
        'type': 'dict',
        'schema': {
            'name': {
                'type': 'string',
                'allowed': [
                    'testinfra',
                ],
            },
            'lint': {
                'type': 'dict',
                'schema': {
                    'name': {
                        'type': 'string',
                        'allowed': [
                            'flake8',
                        ],
                    },
                }
            },
        }
    },
}

verifier_ansible_mutually_exclusive_schema = {
    'verifier': {
        'type': 'dict',
        'schema': {
            'name': {
                'type': 'string',
                'allowed': [
                    'ansible',
                ],
            },
            'lint': {
                'type': 'dict',
                'schema': {
                    'name': {
                        'type': 'string',
                        'allowed': [
                            'ansible-lint',
                        ],
                    },
                }
            },
        }
    },
}


class Validator(cerberus.Validator):
    def __init__(self, *args, **kwargs):
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
        """ Readonly but with a custom error.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if disallowed:
            msg = 'disallowed user provided config option'
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
        """ Readonly but with a custom error.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        # TODO(retr0h): This needs to be better handled.
        pattern = r'^[{$]+MOLECULE[_a-z0-9A-Z]+[}]*$'

        if molecule_env_var:
            if re.match(pattern, value):
                msg = ('cannot reference $MOLECULE special variables '
                       'in this section')
                self._error(field, msg)


def pre_validate(stream, env, keep_string):
    data = util.safe_load(stream)

    v = Validator(allow_unknown=True)
    v.validate(data, pre_validate_base_schema(env, keep_string))

    return v.errors


def validate(c):
    schema = copy.deepcopy(base_schema)

    util.merge_dicts(schema, base_schema)

    # Dependency
    if c['dependency']['name'] == 'shell':
        util.merge_dicts(schema, dependency_command_nullable_schema)

    # Driver
    if c['driver']['name'] == 'docker':
        util.merge_dicts(schema, platforms_docker_schema)
    elif c['driver']['name'] == 'vagrant':
        util.merge_dicts(schema, driver_vagrant_provider_section_schema)
        util.merge_dicts(schema, platforms_vagrant_schema)
    elif c['driver']['name'] == 'lxd':
        util.merge_dicts(schema, platforms_lxd_schema)
    elif c['driver']['name'] == 'linode':
        util.merge_dicts(schema, platforms_linode_schema)

    # Verifier
    if c['verifier']['name'] == 'goss':
        util.merge_dicts(schema, verifier_options_readonly_schema)
        util.merge_dicts(schema, verifier_goss_mutually_exclusive_schema)
    elif c['verifier']['name'] == 'inspec':
        util.merge_dicts(schema, verifier_options_readonly_schema)
        util.merge_dicts(schema, verifier_inspec_mutually_exclusive_schema)
    elif c['verifier']['name'] == 'testinfra':
        util.merge_dicts(schema, verifier_testinfra_mutually_exclusive_schema)
    elif c['verifier']['name'] == 'ansible':
        util.merge_dicts(schema, verifier_ansible_mutually_exclusive_schema)

    v = Validator(allow_unknown=True)
    v.validate(c, schema)

    return v.errors

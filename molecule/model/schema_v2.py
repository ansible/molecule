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

import copy

import cerberus
import cerberus.errors

from molecule import util

base_schema = {
    'dependency': {
        'type': 'dict',
        'schema': {
            'name': {
                'type': 'string',
                'allowed': [
                    'galaxy',
                    'gilt',
                    'shell',
                ],
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
                'type':
                'string',
                'allowed': [
                    'azure',
                    'delegated',
                    'docker',
                    'ec2',
                    'gce',
                    'lxc',
                    'lxd',
                    'openstack',
                    'vagrant',
                ],
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
                'allowed': [
                    'yamllint',
                ],
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
    'platforms': {},
    'provisioner': {
        'type': 'dict',
        'schema': {
            'name': {
                'type': 'string',
                'allowed': [
                    'ansible',
                ],
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
                        'allowed': [
                            'ansible-lint',
                        ],
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
                'allowed': [
                    'testinfra',
                    'inspec',
                    'goss',
                ],
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
                        'allowed': [
                            'flake8',
                            'rubocop',
                            'yamllint',
                        ],
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

platforms_base_schema = {
    'platforms': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'name': {
                    'type': 'string',
                    'required': True,
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
                                    'regex': '^[{$]+[a-z0-9A-z]+[}]*$',
                                },
                                'password': {
                                    'type': 'string',
                                    'regex': '^[{$]+[a-z0-9A-z]+[}]*$',
                                },
                                'email': {
                                    'type': 'string',
                                },
                            }
                        },
                    }
                },
                'command': {
                    'type': 'string',
                },
                'privileged': {
                    'type': 'boolean',
                },
                'volumes': {
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
            }
        }
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


class Validator(cerberus.Validator):
    def __init__(self, *args, **kwargs):
        super(Validator, self).__init__(*args, **kwargs)

    def _validate_disallowed(self, disallowed, field, value):
        """ Readonly but with a custom error.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if disallowed:
            msg = 'disallowed user provided config option'
            self._error(field, msg)


def validate(c):
    schema = copy.deepcopy(base_schema)

    # Dependency
    if c['dependency']['name'] == 'shell':
        util.merge_dicts(schema, dependency_command_nullable_schema)

    # Driver
    util.merge_dicts(schema, platforms_base_schema)
    if c['driver']['name'] == 'docker':
        util.merge_dicts(schema, platforms_docker_schema)
    elif c['driver']['name'] == 'vagrant':
        util.merge_dicts(schema, driver_vagrant_provider_section_schema)
        util.merge_dicts(schema, platforms_vagrant_schema)
    else:
        util.merge_dicts(schema, platforms_base_schema)

    # Verifier
    if c['verifier']['name'] == 'goss':
        util.merge_dicts(schema, verifier_options_readonly_schema)
        util.merge_dicts(schema, verifier_goss_mutually_exclusive_schema)
    elif c['verifier']['name'] == 'inspec':
        util.merge_dicts(schema, verifier_options_readonly_schema)
        util.merge_dicts(schema, verifier_inspec_mutually_exclusive_schema)
    elif c['verifier']['name'] == 'testinfra':
        util.merge_dicts(schema, verifier_testinfra_mutually_exclusive_schema)

    v = Validator(allow_unknown=True)
    v.validate(c, schema)

    return v.errors

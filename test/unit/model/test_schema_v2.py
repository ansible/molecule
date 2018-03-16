#  Copyright (c) 2015-2017 Cisco Systems, Inc.
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

import os

import pytest

from molecule import util
from molecule.model import schema_v2


@pytest.fixture
def _molecule_file():
    return os.path.join(
        os.path.dirname(__file__), os.path.pardir, os.path.pardir, 'resources',
        'molecule_docker.yml')


@pytest.fixture
def _config(_molecule_file, request):
    d = util.safe_load(open(_molecule_file))
    if hasattr(request, 'param'):
        d = util.merge_dicts(d, request.getfuncargvalue(request.param))

    return d


def test_base_config(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_dependency_section_data():
    return {
        'dependency': {
            'name': 'galaxy',
            'enabled': True,
            'options': {
                'foo': 'bar',
            },
            'env': {
                'FOO': 'foo',
                'FOO_BAR': 'foo_bar',
            },
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_dependency_section_data'], indirect=True)
def test_dependency(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_dependency_errors_section_data():
    return {
        'dependency': {
            'name': int(),
            'command': None,
            'enabled': str(),
            'options': [],
            'env': {
                'foo': 'foo',
                'foo-bar': 'foo-bar',
            },
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_dependency_errors_section_data'], indirect=True)
def test_dependency_has_errors(_config):
    x = {
        'dependency': [{
            'name': ['must be of string type'],
            'enabled': ['must be of boolean type'],
            'command': ['null value not allowed'],
            'options': ['must be of dict type'],
            'env': [{
                'foo': ["value does not match regex '^[A-Z0-9_-]+$'"],
                'foo-bar': ["value does not match regex '^[A-Z0-9_-]+$'"],
            }],
        }]
    }

    assert x == schema_v2.validate(_config)


@pytest.fixture
def _model_dependency_allows_galaxy_section_data():
    return {
        'dependency': {
            'name': 'galaxy',
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_dependency_allows_galaxy_section_data'], indirect=True)
def test_dependency_allows_galaxy_name(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_dependency_allows_gilt_section_data():
    return {
        'dependency': {
            'name': 'gilt',
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_dependency_allows_gilt_section_data'], indirect=True)
def test_dependency_allows_gilt_name(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_dependency_allows_shell_section_data():
    return {
        'dependency': {
            'name': 'shell',
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_dependency_allows_shell_section_data'], indirect=True)
def test_dependency_allows_shell_name(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_dependency_errors_invalid_section_data():
    return {
        'dependency': {
            'name': str(),
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_dependency_errors_invalid_section_data'],
    indirect=True)
def test_dependency_invalid_dependency_name_has_errors(_config):
    x = {'dependency': [{'name': ['unallowed value ']}]}

    assert x == schema_v2.validate(_config)


@pytest.fixture
def _model_driver_section_data():
    return {
        'driver': {
            'name': 'docker',
            'provider': {
                'name': None,
            },
            'options': {
                'managed': True,
                'foo': 'bar',
            },
            'ssh_connection_options': [
                'foo',
                'bar',
            ],
            'safe_files': [
                'foo',
                'bar',
            ],
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_driver_section_data'], indirect=True)
def test_driver(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_driver_errors_section_data():
    return {
        'driver': {
            'name': int(),
            'provider': {
                'name': int(),
                'foo': 'bar',
            },
            'options': {
                'managed': str(),
            },
            'ssh_connection_options': [
                int(),
            ],
            'safe_files': [
                int(),
            ],
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_driver_errors_section_data'], indirect=True)
def test_driver_has_errors(_config):
    x = {
        'driver': [{
            'safe_files': [{
                0: ['must be of string type'],
            }],
            'options': [{
                'managed': ['must be of boolean type']
            }],
            'ssh_connection_options': [{
                0: ['must be of string type'],
            }],
            'name': ['must be of string type'],
            'provider': [{
                'foo': ['unknown field'],
                'name': ['must be of string type'],
            }],
        }]
    }

    assert x == schema_v2.validate(_config)


@pytest.fixture
def _model_driver_provider_name_nullable_section_data():
    return {
        'driver': {
            'provider': {
                'name': None,
            },
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_driver_provider_name_nullable_section_data'],
    indirect=True)
def test_driver_provider_name_nullable(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_driver_provider_name_not_nullable_when_vagrant_section_data():
    return {
        'driver': {
            'name': 'vagrant',
            'provider': {
                'name': None,
            },
        }
    }


@pytest.mark.parametrize(
    '_config',
    ['_model_driver_provider_name_not_nullable_when_vagrant_section_data'],
    indirect=True)
def test_driver_provider_name_not_nullable_when_vagrant_driver(_config):
    x = {'driver': [{'provider': [{'name': ['null value not allowed']}]}]}

    assert x == schema_v2.validate(_config)


@pytest.fixture
def _model_driver_allows_azure_section_data():
    return {
        'driver': {
            'name': 'azure',
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_driver_allows_azure_section_data'], indirect=True)
def test_driver_allows_azure_name(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_driver_allows_delegated_section_data():
    return {
        'driver': {
            'name': 'delegated',
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_driver_allows_delegated_section_data'], indirect=True)
def test_driver_allows_delegated_name(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_driver_allows_docker_section_data():
    return {
        'driver': {
            'name': 'docker',
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_driver_allows_docker_section_data'], indirect=True)
def test_driver_allows_docker_name(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_driver_allows_ec2_section_data():
    return {
        'driver': {
            'name': 'ec2',
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_driver_allows_ec2_section_data'], indirect=True)
def test_driver_allows_ec2_name(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_driver_allows_gce_section_data():
    return {
        'driver': {
            'name': 'gce',
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_driver_allows_gce_section_data'], indirect=True)
def test_driver_allows_gce_name(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_driver_allows_lxc_section_data():
    return {
        'driver': {
            'name': 'lxc',
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_driver_allows_lxc_section_data'], indirect=True)
def test_driver_allows_lxc_name(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_driver_allows_lxd_section_data():
    return {
        'driver': {
            'name': 'lxd',
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_driver_allows_lxd_section_data'], indirect=True)
def test_driver_allows_lxd_name(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_driver_allows_openstack_section_data():
    return {
        'driver': {
            'name': 'openstack',
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_driver_allows_openstack_section_data'], indirect=True)
def test_driver_allows_openstack_name(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_driver_allows_vagrant_section_data():
    return {
        'driver': {
            'name': 'vagrant',
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_driver_allows_vagrant_section_data'], indirect=True)
def test_driver_allows_vagrant_name(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_driver_errors_invalid_section_data():
    return {
        'driver': {
            'name': str(),
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_driver_errors_invalid_section_data'], indirect=True)
def test_driver_invalid_driver_name_has_errors(_config):
    x = {'driver': [{'name': ['unallowed value ']}]}

    assert x == schema_v2.validate(_config)


@pytest.fixture
def _model_lint_section_data():
    return {
        'lint': {
            'name': 'yamllint',
            'enabled': True,
            'options': {
                'foo': 'bar',
            },
            'env': {
                'FOO': 'foo',
                'FOO_BAR': 'foo_bar',
            },
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_lint_section_data'], indirect=True)
def test_lint(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_lint_errors_section_data():
    return {
        'lint': {
            'name': int(),
            'enabled': str(),
            'options': [],
            'env': {
                'foo': 'foo',
                'foo-bar': 'foo-bar',
            },
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_lint_errors_section_data'], indirect=True)
def test_lint_has_errors(_config):
    x = {
        'lint': [{
            'enabled': ['must be of boolean type'],
            'name': ['must be of string type'],
            'env': [{
                'foo': ["value does not match regex '^[A-Z0-9_-]+$'"],
                'foo-bar': ["value does not match regex '^[A-Z0-9_-]+$'"],
            }],
            'options': ['must be of dict type'],
        }]
    }

    assert x == schema_v2.validate(_config)


@pytest.fixture
def _model_lint_allows_yamllint_section_data():
    return {
        'lint': {
            'name': 'yamllint',
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_lint_allows_yamllint_section_data'], indirect=True)
def test_lint_allows_yamllint_name(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_lint_errors_invalid_section_data():
    return {
        'lint': {
            'name': str(),
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_lint_errors_invalid_section_data'], indirect=True)
def test_lint_invalid_lint_name_has_errors(_config):
    x = {'lint': [{'name': ['unallowed value ']}]}

    assert x == schema_v2.validate(_config)


@pytest.fixture
def _model_platforms_docker_section_data():
    return {
        'platforms': [{
            'name':
            'instance',
            'hostname':
            'instance',
            'image':
            'image_name:tag',
            'registry': {
                'url': 'registry.example.com',
                'credentials': {
                    'username': '$USERNAME',
                    'password': '$PASSWORD',
                    'email': 'user@example.com',
                },
            },
            'command':
            'sleep infinity',
            'privileged':
            True,
            'volumes': [
                '/sys/fs/cgroup:/sys/fs/cgroup:ro',
            ],
            'capabilities': [
                'SYS_ADMIN',
            ],
            'exposed_ports': [
                '53/udp',
                '53/tcp',
            ],
            'published_ports': [
                '0.0.0.0:8053:53/udp',
                '0.0.0.0:8053:53/tcp',
            ],
            'ulimits': [
                'nofile:262144:262144',
            ],
            'dns_servers': [
                '8.8.8.8',
            ],
            'networks': [
                {
                    'name': 'foo',
                },
                {
                    'name': 'bar',
                },
            ],
            'foo':
            'bar'
        }]
    }


@pytest.mark.parametrize(
    '_config', ['_model_platforms_docker_section_data'], indirect=True)
def test_platforms_docker(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_platforms_docker_errors_section_data():
    return {
        'platforms': [{
            'name': int(),
            'hostname': int(),
            'image': int(),
            'registry': {
                'url': int(),
                'credentials': {
                    'username': int(),
                    'password': int(),
                    'email': int(),
                },
            },
            'command': int(),
            'privileged': str(),
            'volumes': [
                int(),
            ],
            'capabilities': [
                int(),
            ],
            'exposed_ports': [
                int(),
            ],
            'published_ports': [
                int(),
            ],
            'ulimits': [
                int(),
            ],
            'dns_servers': [
                int(),
            ],
            'networks': [
                {
                    'name': int(),
                },
            ],
        }]
    }


@pytest.mark.parametrize(
    '_config', ['_model_platforms_docker_errors_section_data'], indirect=True)
def test_platforms_docker_has_errors(_config):
    x = {
        'platforms': [{
            0: [{
                'exposed_ports': [{
                    0: ['must be of string type'],
                }],
                'dns_servers': [{
                    0: ['must be of string type'],
                }],
                'name': ['must be of string type'],
                'image': ['must be of string type'],
                'hostname': ['must be of string type'],
                'capabilities': [{
                    0: ['must be of string type'],
                }],
                'privileged': ['must be of boolean type'],
                'command': ['must be of string type'],
                'registry': [{
                    'url': ['must be of string type'],
                    'credentials': [{
                        'username': ['must be of string type'],
                        'password': ['must be of string type'],
                        'email': ['must be of string type'],
                    }]
                }],
                'volumes': [{
                    0: ['must be of string type'],
                }],
                'published_ports': [{
                    0: ['must be of string type'],
                }],
                'networks': [{
                    0: [{
                        'name': ['must be of string type'],
                    }]
                }],
                'ulimits': [{
                    0: ['must be of string type'],
                }]
            }]
        }]
    }

    assert x == schema_v2.validate(_config)


@pytest.fixture
def _model_platforms_docker_registry_credentials_section_data():
    return {
        'platforms': [{
            'name': str(),
            'registry': {
                'credentials': {
                    'username': 'foo',
                    'password': 'bar',
                },
            },
        }]
    }


@pytest.mark.parametrize(
    '_config', ['_model_platforms_docker_registry_credentials_section_data'],
    indirect=True)
def test_platforms_docker_registry_credentials_are_interpolated(_config):
    x = {
        'platforms': [{
            0: [{
                'registry': [{
                    'credentials': [{
                        'username': [
                            "value does not match regex '^[{$]+[a-z0-9A-z]+[}]*$'",  # noqa
                        ],
                        'password': [
                            "value does not match regex '^[{$]+[a-z0-9A-z]+[}]*$'",  # noqa
                        ]
                    }]
                }]
            }]
        }]
    }

    assert x == schema_v2.validate(_config)


@pytest.fixture
def _model_platforms_vagrant_section_data():
    return {
        'platforms': [{
            'name':
            'instance',
            'interfaces': [{
                'auto_config': True,
                'network_name': 'private_network',
                'type': 'dhcp'
            }],
            'instance_raw_config_args':
            ["vm.network 'forwarded_port', guest: 80, host: 8080"],
            'config_options': {
                'ssh.insert_key': False,
            },
            'box':
            'sleep infinity',
            'box_version':
            'sleep infinity',
            'box_url':
            'sleep infinity',
            'memory':
            1024,
            'cpus':
            2,
            'provider_options': {
                'gui': True,
            },
            'provider_raw_config_args': [
                "customize ['modifyvm', :id, '--cpuexecutioncap', '50']",
            ],
            'provision':
            True,
        }]
    }


@pytest.mark.parametrize(
    '_config', ['_model_platforms_vagrant_section_data'], indirect=True)
def test_platforms_vagrant(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_platforms_vagrant_errors_section_data():
    return {
        'platforms': [{
            'name': int(),
            'interfaces': [],
            'instance_raw_config_args': [
                int(),
            ],
            'config_options': [],
            'box': int(),
            'box_version': int(),
            'box_url': int(),
            'memory': str(),
            'cpus': str(),
            'provider_options': [],
            'provider_raw_config_args': [
                int(),
            ],
            'provision': str(),
        }]
    }


@pytest.mark.parametrize(
    '_config', ['_model_platforms_vagrant_errors_section_data'], indirect=True)
def test_platforms_vagrant_has_errors(_config):
    x = {
        'platforms': [{
            0: [{
                'box': ['must be of string type'],
                'box_version': ['must be of string type'],
                'config_options': ['must be of dict type'],
                'name': ['must be of string type'],
                'provider_raw_config_args': [{
                    0: ['must be of string type']
                }],
                'cpus': ['must be of integer type'],
                'box_url': ['must be of string type'],
                'instance_raw_config_args': [{
                    0: ['must be of string type']
                }],
                'memory': ['must be of integer type'],
                'provider_options': ['must be of dict type'],
                'provision': ['must be of boolean type']
            }]
        }]
    }

    assert x == schema_v2.validate(_config)


def test_platforms_driver_name_required(_config):
    del _config['platforms'][0]['name']
    x = {'platforms': [{0: [{'name': ['required field']}]}]}

    assert x == schema_v2.validate(_config)


@pytest.fixture
def _model_provisioner_section_data():
    return {
        'provisioner': {
            'name': 'ansible',
            'config_options': {
                'foo': 'bar',
            },
            'connection_options': {
                'foo': 'bar',
            },
            'options': {
                'foo': 'bar',
            },
            'env': {
                'FOO': 'foo',
                'FOO_BAR': 'foo_bar',
            },
            'inventory': {
                'host_vars': {
                    'foo': 'bar',
                },
                'group_vars': {
                    'foo': 'bar',
                },
                'links': {
                    'foo': 'bar',
                },
            },
            'children': {
                'foo': 'bar',
            },
            'playbooks': {
                'create': 'foo.yml',
                'converge': 'bar.yml',
                'destroy': 'baz.yml',
                'prepare': 'qux.yml',
                'side_effect': 'quux.yml',
                'foo': {
                    'foo': 'bar',
                },
            },
            'lint': {
                'name': 'ansible-lint',
                'enabled': True,
                'options': {
                    'foo': 'bar',
                },
                'env': {
                    'FOO': 'foo',
                    'FOO_BAR': 'foo_bar',
                },
            },
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_provisioner_section_data'], indirect=True)
def test_provisioner(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_provisioner_errors_section_data():
    return {
        'provisioner': {
            'name': int(),
            'config_options': [],
            'connection_options': [],
            'options': [],
            'env': {
                'foo': 'foo',
                'foo-bar': 'foo-bar',
            },
            'inventory': {
                'host_vars': [],
                'group_vars': [],
                'links': [],
            },
            'children': [],
            'playbooks': {
                'create': int(),
                'converge': int(),
                'destroy': int(),
                'prepare': int(),
                'side_effect': int(),
            },
            'lint': {
                'name': int(),
                'enabled': str(),
                'options': [],
                'env': {
                    'foo': 'foo',
                    'foo-bar': 'foo-bar',
                },
            },
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_provisioner_errors_section_data'], indirect=True)
def test_provisioner_has_errors(_config):
    x = {
        'provisioner': [{
            'config_options': ['must be of dict type'],
            'connection_options': ['must be of dict type'],
            'lint': [{
                'enabled': ['must be of boolean type'],
                'name': ['must be of string type'],
                'env': [{
                    'foo': ["value does not match regex '^[A-Z0-9_-]+$'"],
                    'foo-bar': ["value does not match regex '^[A-Z0-9_-]+$'"],
                }],
                'options': ['must be of dict type'],
            }],
            'playbooks': [{
                'destroy': ['must be of string type'],
                'create': ['must be of string type'],
                'side_effect': ['must be of string type'],
                'prepare': ['must be of string type'],
                'converge': ['must be of string type'],
            }],
            'children': ['must be of dict type'],
            'inventory': [{
                'group_vars': ['must be of dict type'],
                'host_vars': ['must be of dict type'],
                'links': ['must be of dict type'],
            }],
            'env': [{
                'foo': ["value does not match regex '^[A-Z0-9_-]+$'"],
                'foo-bar': ["value does not match regex '^[A-Z0-9_-]+$'"],
            }],
            'options': ['must be of dict type'],
            'name': ['must be of string type'],
        }]
    }

    assert x == schema_v2.validate(_config)


@pytest.fixture
def _model_provisioner_playbooks_side_effect_nullable_section_data():
    return {
        'provisioner': {
            'playbooks': {
                'side_effect': None,
            },
        }
    }


@pytest.mark.parametrize(
    '_config',
    ['_model_provisioner_playbooks_side_effect_nullable_section_data'],
    indirect=True)
def test_provisioner_playbooks_side_effect_nullable(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_provisioner_config_options_disallowed_section_data():
    return {
        'provisioner': {
            'config_options': {
                'defaults': {
                    'roles_path': 'foo',
                    'library': 'foo',
                    'filter_plugins': 'foo',
                    'foo': 'bar',
                },
                'foo': {
                    'foo': 'bar',
                },
                'privilege_escalation': {
                    'foo': 'bar'
                },
            },
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_provisioner_config_options_disallowed_section_data'],
    indirect=True)
def test_provisioner_config_options_disallowed_field(_config):
    x = {
        'provisioner': [{
            'config_options': [{
                'defaults': [{
                    'filter_plugins':
                    ['disallowed user provided config option'],
                    'library': ['disallowed user provided config option'],
                    'roles_path': ['disallowed user provided config option'],
                }],
                'privilege_escalation':
                ['disallowed user provided config option'],
            }]
        }]
    }

    assert x == schema_v2.validate(_config)


@pytest.fixture
def _model_provisioner_env_disallowed_section_data():
    return {
        'provisioner': {
            'env': {
                'ANSIBLE_BECOME': str(),
                'ANSIBLE_BECOME_METHOD': str(),
                'ANSIBLE_BECOME_USER': str(),
            },
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_provisioner_env_disallowed_section_data'],
    indirect=True)
def test_provisioner_config_env_disallowed_field(_config):
    x = {
        'provisioner': [{
            'env': [{
                'ANSIBLE_BECOME_METHOD':
                ['disallowed user provided config option'],
                'ANSIBLE_BECOME': ['disallowed user provided config option'],
                'ANSIBLE_BECOME_USER':
                ['disallowed user provided config option'],
            }]
        }]
    }

    assert x == schema_v2.validate(_config)


@pytest.fixture
def _model_provisioner_allows_ansible_section_data():
    return {
        'provisioner': {
            'name': 'ansible',
            'lint': {
                'name': 'ansible-lint',
            },
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_provisioner_allows_ansible_section_data'],
    indirect=True)
def test_provisioner_allows_ansible_name(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_provisioner_errors_invalid_section_data():
    return {
        'provisioner': {
            'name': str(),
            'lint': {
                'name': str(),
            },
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_provisioner_errors_invalid_section_data'],
    indirect=True)
def test_provisioner_invalid_provisioner_name_has_errors(_config):
    x = {
        'provisioner': [{
            'lint': [{
                'name': ['unallowed value ']
            }],
            'name': ['unallowed value ']
        }]
    }

    assert x == schema_v2.validate(_config)


@pytest.fixture
def _model_scenario_section_data():
    return {
        'scenario': {
            'name': 'foo',
            'check_sequence': [
                'foo',
            ],
            'converge_sequence': [
                'foo',
            ],
            'create_sequence': [
                'foo',
            ],
            'destroy_sequence': [
                'foo',
            ],
            'test_sequence': [
                'foo',
            ],
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_scenario_section_data'], indirect=True)
def test_scenario(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_scenario_errors_section_data():
    return {
        'scenario': {
            'name': int(),
            'check_sequence': [
                int(),
            ],
            'converge_sequence': [
                int(),
            ],
            'create_sequence': [
                int(),
            ],
            'destroy_sequence': [
                int(),
            ],
            'test_sequence': [
                int(),
            ],
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_scenario_errors_section_data'], indirect=True)
def test_scenario_has_errors(_config):
    x = {
        'scenario': [{
            'converge_sequence': [{
                0: ['must be of string type'],
            }],
            'name': ['must be of string type'],
            'check_sequence': [{
                0: ['must be of string type'],
            }],
            'create_sequence': [{
                0: ['must be of string type'],
            }],
            'destroy_sequence': [{
                0: ['must be of string type'],
            }],
            'test_sequence': [{
                0: ['must be of string type'],
            }]
        }]
    }

    assert x == schema_v2.validate(_config)


@pytest.fixture
def _model_verifier_section_data():
    return {
        'verifier': {
            'name': 'testinfra',
            'enabled': True,
            'directory': 'foo',
            'options': {
                'foo': 'bar'
            },
            'env': {
                'FOO': 'foo',
                'FOO_BAR': 'foo_bar',
            },
            'additional_files_or_dirs': [
                'foo',
            ],
            'lint': {
                'name': 'flake8',
                'enabled': True,
                'options': {
                    'foo': 'bar',
                },
                'env': {
                    'FOO': 'foo',
                    'FOO_BAR': 'foo_bar',
                },
            },
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_verifier_section_data'], indirect=True)
def test_verifier(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_verifier_errors_section_data():
    return {
        'verifier': {
            'name': int(),
            'enabled': str(),
            'directory': int(),
            'options': [],
            'env': {
                'foo': 'foo',
                'foo-bar': 'foo-bar',
            },
            'additional_files_or_dirs': [
                int(),
            ],
            'lint': {
                'name': int(),
                'enabled': str(),
                'options': [],
                'env': {
                    'foo': 'foo',
                    'foo-bar': 'foo-bar',
                },
            },
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_verifier_errors_section_data'], indirect=True)
def test_verifier_has_errors(_config):
    x = {
        'verifier': [{
            'name': ['must be of string type'],
            'lint': [{
                'enabled': ['must be of boolean type'],
                'name': ['must be of string type'],
                'env': [{
                    'foo': ["value does not match regex '^[A-Z0-9_-]+$'"],
                    'foo-bar': ["value does not match regex '^[A-Z0-9_-]+$'"],
                }],
                'options': ['must be of dict type'],
            }],
            'enabled': ['must be of boolean type'],
            'env': [{
                'foo': ["value does not match regex '^[A-Z0-9_-]+$'"],
                'foo-bar': ["value does not match regex '^[A-Z0-9_-]+$'"],
            }],
            'directory': ['must be of string type'],
            'additional_files_or_dirs': [{
                0: ['must be of string type'],
            }],
            'options': ['must be of dict type'],
        }]
    }

    assert x == schema_v2.validate(_config)


@pytest.fixture
def _model_verifier_allows_ansible_lint_section_data():
    return {
        'verifier': {
            'name': 'testinfra',
            'lint': {
                'name': 'flake8',
            },
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_verifier_allows_ansible_lint_section_data'],
    indirect=True)
def test_verifier_allows_ansible_lint_name(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_verifier_allows_goss_section_data():
    return {
        'verifier': {
            'name': 'goss',
            'lint': {
                'name': 'flake8',
            },
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_verifier_allows_goss_section_data'], indirect=True)
def test_verifier_allows_goss_name(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_verifier_errors_invalid_section_data():
    return {
        'verifier': {
            'name': str(),
            'lint': {
                'name': str(),
            },
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_verifier_errors_invalid_section_data'], indirect=True)
def test_verifier_invalid_verifier_name_has_errors(_config):
    x = {
        'verifier': [{
            'lint': [{
                'name': ['unallowed value ']
            }],
            'name': ['unallowed value ']
        }]
    }

    assert x == schema_v2.validate(_config)

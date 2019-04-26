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

from molecule.model import schema_v2


@pytest.fixture
def _model_platforms_docker_section_data():
    return {
        'driver': {
            'name': 'docker',
        },
        'platforms': [{
            'name':
            'instance',
            'hostname':
            'instance',
            'image':
            'image_name:tag',
            'pull':
            True,
            'pre_build_image':
            False,
            'registry': {
                'url': 'registry.example.com',
                'credentials': {
                    'username': 'username',
                    'password': '$PASSWORD',
                    'email': 'user@example.com',
                },
            },
            'override_command':
            False,
            'command':
            'sleep infinity',
            'tty':
            True,
            'pid_mode':
            'host',
            'privileged':
            True,
            'security_opts': [
                'seccomp=unconfined',
            ],
            'volumes': [
                '/sys/fs/cgroup:/sys/fs/cgroup:ro',
            ],
            'tmpfs': [
                '/tmp',
                '/run ',
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
            'env': {
                'FOO': 'bar',
                'foo': 'bar',
            },
            'restart_policy':
            'on-failure',
            'restart_retries':
            1,
            'networks': [
                {
                    'name': 'foo',
                },
                {
                    'name': 'bar',
                },
            ],
            'network_mode':
            'mode',
            'purge_networks':
            True,
            'foo':
            'bar'
        }]
    }


@pytest.mark.parametrize(
    '_config', ['_model_platforms_docker_section_data'], indirect=True)
def test_platforms_docker(_config):
    assert {} == schema_v2.validate(_config)


@pytest.mark.parametrize(
    '_config', ['_model_platforms_docker_section_data'], indirect=True)
def test_platforms_unique_names(_config):
    instance_name = _config['platforms'][0]['name']
    _config['platforms'] += [{
        'name': instance_name  # duplicate platform name
    }]

    expected_validation_errors = {
        'platforms': [{
            0: [{
                'name': ["'{}' is not unique".format(instance_name)]
            }],
            1: [{
                'name': ["'{}' is not unique".format(instance_name)]
            }]
        }]
    }

    assert expected_validation_errors == schema_v2.validate(_config)


@pytest.mark.parametrize(
    '_config', ['_model_platforms_docker_section_data'], indirect=True)
def test_platforms_docker_exposed_ports_coerced(_config):
    _config['platforms'][0]['exposed_ports'] = [9904]
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_platforms_docker_errors_section_data():
    return {
        'platforms': [{
            'name': int(),
            'hostname': int(),
            'image': int(),
            'pull': int(),
            'dockerfile': bool(),
            'pre_build_image': int(),
            'registry': {
                'url': int(),
                'credentials': {
                    'username': int(),
                    'password': int(),
                    'email': int(),
                },
            },
            'override_command': int(),
            'command': int(),
            'tty': str(),
            'pid_mode': int(),
            'privileged': str(),
            'security_opts': [
                int(),
            ],
            'volumes': [
                int(),
            ],
            'tmpfs': [
                int(),
            ],
            'capabilities': [
                int(),
            ],
            'exposed_ports': [
                bool(),
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
            'env': str(),
            'restart_policy': int(),
            'restart_retries': str(),
            'networks': [
                {
                    'name': int(),
                },
            ],
            'network_mode': int(),
            'purge_networks': int(),
        }]
    }


@pytest.mark.parametrize(
    '_config', ['_model_platforms_docker_errors_section_data'], indirect=True)
def test_platforms_docker_has_errors(_config):
    x = {
        'platforms': [{
            0: [{
                'exposed_ports': [{
                    0: ['must be of string type']
                }],
                'dns_servers': [{
                    0: ['must be of string type']
                }],
                'name': ['must be of string type'],
                'capabilities': [{
                    0: ['must be of string type']
                }],
                'image': ['must be of string type'],
                'pull': ['must be of boolean type'],
                'dockerfile': ['must be of string type'],
                'pre_build_image': ['must be of boolean type'],
                'hostname': ['must be of string type'],
                'security_opts': [{
                    0: ['must be of string type']
                }],
                'pid_mode': ['must be of string type'],
                'privileged': ['must be of boolean type'],
                'override_command': ['must be of boolean type'],
                'command': ['must be of string type'],
                'tty': ['must be of boolean type'],
                'registry': [{
                    'url': ['must be of string type'],
                    'credentials': [{
                        'username': ['must be of string type'],
                        'password': ['must be of string type'],
                        'email': ['must be of string type']
                    }]
                }],
                'volumes': [{
                    0: ['must be of string type']
                }],
                'published_ports': [{
                    0: ['must be of string type']
                }],
                'tmpfs': [{
                    0: ['must be of string type']
                }],
                'networks': [{
                    0: [{
                        'name': ['must be of string type']
                    }]
                }],
                'network_mode': ['must be of string type'],
                'purge_networks': ['must be of boolean type'],
                'ulimits': [{
                    0: ['must be of string type']
                }],
                'env': ['must be of dict type'],
                'restart_policy': ['must be of string type'],
                'restart_retries': ['must be of integer type'],
            }]
        }]
    }

    assert x == schema_v2.validate(_config)


@pytest.fixture
def _model_platforms_vagrant_section_data():
    return {
        'driver': {
            'name': 'vagrant',
        },
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
        'driver': {
            'name': 'vagrant',
        },
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


@pytest.fixture
def _model_platforms_lxd_section_data():
    return {
        'driver': {
            'name': 'lxd',
        },
        'platforms': [{
            'name': 'instance',
            'url': 'https://127.0.0.1:8443',
            'cert_file': '/root/.config/lxc/client.crt',
            'key_file': '/root/.config/lxc/client.key',
            'trust_password': 'password',
            'source': {
                'type': 'image',
                'mode': 'pull',
                'protocol': 'lxd',
                'server': 'https://images.linuxcontainers.org',
                'alias': 'ubuntu/xenial/amd64',
            },
            'architecture': 'x86_64',
            'config': {
                'limits.cpu': '2',
            },
            'devices': {
                'kvm': {
                    'path': '/dev/kvm',
                    'type': 'unix-char',
                }
            },
            'profiles': [
                'default',
            ],
            'force_stop': True,
        }]
    }


@pytest.mark.parametrize(
    '_config', ['_model_platforms_lxd_section_data'], indirect=True)
def test_platforms_lxd(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_platforms_lxd_errors_section_data():
    return {
        'driver': {
            'name': 'lxd',
        },
        'platforms': [{
            'name': int(),
            'url': int(),
            'cert_file': int(),
            'key_file': int(),
            'trust_password': int(),
            'source': {
                'type': int(),
                'mode': 'set for mode',
                'server': int(),
                'protocol': 'set for protocol',
                'alias': int(),
            },
            'architecture': 'set for architecture',
            'config': int(),
            'devices': int(),
            'profiles': [
                int(),
            ],
            'force_stop': int()
        }]
    }


@pytest.mark.parametrize(
    '_config', ['_model_platforms_lxd_errors_section_data'], indirect=True)
def test_platforms_lxd_has_errors(_config):
    x = {
        'platforms': [{
            0: [{
                'name': ['must be of string type'],
                'url': ['must be of string type'],
                'cert_file': ['must be of string type'],
                'key_file': ['must be of string type'],
                'trust_password': ['must be of string type'],
                'source': [{
                    'alias': ['must be of string type'],
                    'mode': ['unallowed value set for mode'],
                    'protocol': ['unallowed value set for protocol'],
                    'server': ['must be of string type'],
                    'type': ['must be of string type']
                }],
                'architecture': ['unallowed value set for architecture'],
                'config': ['must be of dict type'],
                'devices': ['must be of dict type'],
                'profiles': [{
                    0: ['must be of string type']
                }],
                'force_stop': ['must be of boolean type']
            }]
        }]
    }

    assert x == schema_v2.validate(_config)


def test_platforms_driver_name_required(_config):
    del _config['platforms'][0]['name']
    x = {'platforms': [{0: [{'name': ['required field']}]}]}

    assert x == schema_v2.validate(_config)


@pytest.fixture
def _model_platform_linode_section_data():
    return {
        'driver': {
            'name': 'linode',
        },
        'platforms': [{
            'name': '',
            'plan': 0,
            'datacenter': 0,
            'distribution': 0,
        }]
    }


@pytest.mark.parametrize(
    '_config', ['_model_platform_linode_section_data'], indirect=True)
def test_platforms_linode(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_platforms_linode_errors_section_data():
    return {
        'driver': {
            'name': 'linode',
        },
        'platforms': [{
            'name': 0,
            'plan': '',
            'datacenter': '',
            'distribution': '',
        }]
    }


@pytest.mark.parametrize(
    '_config', ['_model_platforms_linode_errors_section_data'], indirect=True)
def test_platforms_linode_has_errors(_config):
    expected_config = {
        'platforms': [{
            0: [{
                'name': ['must be of string type'],
                'plan': ['must be of integer type'],
                'datacenter': ['must be of integer type'],
                'distribution': ['must be of integer type'],
            }],
        }],
    }

    assert expected_config == schema_v2.validate(_config)


@pytest.mark.parametrize(
    '_config', ['_model_platform_linode_section_data'], indirect=True)
@pytest.mark.parametrize('_required_field', (
    'distribution',
    'plan',
    'datacenter',
    'distribution',
))
def test_platforms_linode_fields_required(_config, _required_field):
    del _config['platforms'][0][_required_field]
    expected_config = {
        'platforms': [{
            0: [{
                _required_field: ['required field']
            }]
        }]
    }
    assert expected_config == schema_v2.validate(_config)

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

import pytest

from molecule.model import schema_v2


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

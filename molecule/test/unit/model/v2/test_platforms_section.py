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
def _model_platforms_docker_section_data():
    return {
        "driver": {"name": "docker"},
        "platforms": [
            {
                "name": "instance",
                "hostname": "instance",
                "image": "image_name:tag",
                "pull": True,
                "pre_build_image": False,
                "registry": {
                    "url": "registry.example.com",
                    "credentials": {
                        "username": "username",
                        "password": "$PASSWORD",
                        "email": "user@example.com",
                    },
                },
                "override_command": False,
                "command": "sleep infinity",
                "tty": True,
                "pid_mode": "host",
                "privileged": True,
                "security_opts": ["seccomp=unconfined"],
                "volumes": ["/sys/fs/cgroup:/sys/fs/cgroup:ro"],
                "keep_volumes": True,
                "tmpfs": ["/tmp", "/run "],
                "capabilities": ["SYS_ADMIN"],
                "sysctls": {
                    "net.core.somaxconn": "1024",
                    "net.ipv4.tcp_syncookies": "0",
                },
                "exposed_ports": ["53/udp", "53/tcp"],
                "published_ports": ["0.0.0.0:8053:53/udp", "0.0.0.0:8053:53/tcp"],
                "ulimits": ["nofile:262144:262144"],
                "user": "root",
                "dns_servers": ["8.8.8.8"],
                "etc_hosts": "{'host1.example.com': '10.3.1.5'}",
                "env": {"FOO": "bar", "foo-baz": "bar", "foo.baz": "bar"},
                "restart_policy": "on-failure",
                "restart_retries": 1,
                "networks": [{"name": "foo"}, {"name": "bar"}],
                "network_mode": "mode",
                "purge_networks": True,
                "foo": "bar",
                "docker_host": "tcp://localhost:12376",
                "cacert_path": "/foo/bar/ca.pem",
                "cert_path": "/foo/bar/cert.pem",
                "key_path": "/foo/bar/key.pem",
                "tls_verify": True,
            }
        ],
    }


@pytest.mark.parametrize(
    "_config", ["_model_platforms_docker_section_data"], indirect=True
)
def test_platforms_docker(_config):
    assert {} == schema_v3.validate(_config)


@pytest.mark.parametrize(
    "_config", ["_model_platforms_docker_section_data"], indirect=True
)
def test_platforms_unique_names(_config):
    instance_name = _config["platforms"][0]["name"]
    _config["platforms"] += [{"name": instance_name}]  # duplicate platform name

    expected_validation_errors = {
        "platforms": [
            {
                0: [{"name": ["'{}' is not unique".format(instance_name)]}],
                1: [{"name": ["'{}' is not unique".format(instance_name)]}],
            }
        ]
    }

    assert expected_validation_errors == schema_v3.validate(_config)


@pytest.mark.parametrize(
    "_config", ["_model_platforms_docker_section_data"], indirect=True
)
def test_platforms_docker_exposed_ports_coerced(_config):
    _config["platforms"][0]["exposed_ports"] = [9904]
    assert {} == schema_v3.validate(_config)


@pytest.fixture
def _model_platforms_docker_errors_section_data():
    return {
        "platforms": [
            {
                "name": int(),
                "hostname": int(),
                "image": int(),
                "pull": int(),
                "dockerfile": bool(),
                "pre_build_image": int(),
                "registry": {
                    "url": int(),
                    "credentials": {
                        "username": int(),
                        "password": int(),
                        "email": int(),
                    },
                },
                "override_command": int(),
                "command": int(),
                "tty": str(),
                "pid_mode": int(),
                "privileged": str(),
                "security_opts": [int()],
                "volumes": [int()],
                "keep_volumes": [int()],
                "tmpfs": [int()],
                "capabilities": [int()],
                "sysctls": str(),
                "exposed_ports": [bool()],
                "published_ports": [int()],
                "ulimits": [int()],
                "user": str(),
                "dns_servers": [int()],
                "etc_hosts": int(),
                "env": str(),
                "restart_policy": int(),
                "restart_retries": str(),
                "networks": [{"name": int()}],
                "network_mode": int(),
                "purge_networks": int(),
                "docker_host": int(),
                "cacert_path": int(),
                "cert_path": int(),
                "key_path": int(),
                "tls_verify": str(),
            }
        ]
    }


@pytest.mark.parametrize(
    "_config", ["_model_platforms_docker_errors_section_data"], indirect=True
)
def test_platforms_docker_has_errors(_config):
    x = {
        "platforms": [
            {
                0: [
                    {
                        "name": ["must be of string type"],
                        "hostname": ["must be of string type"],
                        "image": ["must be of string type"],
                        "pull": ["must be of boolean type"],
                        "dockerfile": ["must be of string type"],
                        "pre_build_image": ["must be of boolean type"],
                        "registry": [
                            {
                                "url": ["must be of string type"],
                                "credentials": [
                                    {
                                        "username": ["must be of string type"],
                                        "password": ["must be of string type"],
                                        "email": ["must be of string type"],
                                    }
                                ],
                            }
                        ],
                        "override_command": ["must be of boolean type"],
                        "command": ["must be of string type"],
                        "tty": ["must be of boolean type"],
                        "pid_mode": ["must be of string type"],
                        "privileged": ["must be of boolean type"],
                        "security_opts": [{0: ["must be of string type"]}],
                        "volumes": [{0: ["must be of string type"]}],
                        "keep_volumes": ["must be of boolean type"],
                        "tmpfs": [{0: ["must be of string type"]}],
                        "capabilities": [{0: ["must be of string type"]}],
                        "sysctls": ["must be of dict type"],
                        "exposed_ports": [{0: ["must be of string type"]}],
                        "published_ports": [{0: ["must be of string type"]}],
                        "ulimits": [{0: ["must be of string type"]}],
                        "dns_servers": [{0: ["must be of string type"]}],
                        "etc_hosts": ["must be of ['string', 'dict'] type"],
                        "env": ["must be of dict type"],
                        "restart_policy": ["must be of string type"],
                        "restart_retries": ["must be of integer type"],
                        "networks": [{0: [{"name": ["must be of string type"]}]}],
                        "network_mode": ["must be of string type"],
                        "purge_networks": ["must be of boolean type"],
                        "docker_host": ["must be of string type"],
                        "cacert_path": ["must be of string type"],
                        "cert_path": ["must be of string type"],
                        "key_path": ["must be of string type"],
                        "tls_verify": ["must be of boolean type"],
                    }
                ]
            }
        ]
    }

    assert x == schema_v3.validate(_config)


def test_platforms_driver_name_required(_config):
    del _config["platforms"][0]["name"]
    x = {"platforms": [{0: [{"name": ["required field"]}]}]}

    assert x == schema_v3.validate(_config)


@pytest.mark.parametrize(
    "_config", ["_model_platforms_docker_section_data"], indirect=True
)
def test_platforms_env_should_refuse_keys_with_special_char(_config):
    _config["platforms"][0]["env"] = {"FOO#BAR": "bar", "foo/baz": "bar"}
    x = {
        "platforms": [
            {
                0: [
                    {
                        "env": [
                            {
                                "FOO#BAR": [
                                    "value does not match regex " "'^[a-zA-Z0-9._-]+$'"
                                ],
                                "foo/baz": [
                                    "value does not match regex " "'^[a-zA-Z0-9._-]+$'"
                                ],
                            }
                        ]
                    }
                ]
            }
        ]
    }

    assert x == schema_v3.validate(_config)

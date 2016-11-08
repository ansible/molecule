#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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

from molecule import ansible_playbook
from molecule.driver import dockerdriver

pytestmark = pytest.helpers.supports_docker()


@pytest.fixture()
def docker_instance(docker_molecule_instance, request):
    d = dockerdriver.DockerDriver(docker_molecule_instance)

    def cleanup():
        d.destroy()

    request.addfinalizer(cleanup)

    return d


def test_name(docker_instance):
    assert 'docker' == docker_instance.name


def test_instances(docker_instance):
    assert 'test1' == docker_instance.instances[0]['name']
    assert 'test2' == docker_instance.instances[1]['name']


def test_default_provider(docker_instance):
    assert 'docker' == docker_instance.default_provider


def test_default_platform(docker_instance):
    assert 'docker' == docker_instance.default_platform


def test_provider(docker_instance):
    assert 'docker' == docker_instance.provider


def test_platform(docker_instance):
    assert 'docker' == docker_instance.platform


def test_platform_setter(docker_instance):
    docker_instance.platform = 'foo_platform'

    assert 'foo_platform' == docker_instance.platform


def test_valid_providers(docker_instance):
    assert [{'name': 'docker'}] == docker_instance.valid_providers


def test_valid_platforms(docker_instance):
    assert [{'name': 'docker'}] == docker_instance.valid_platforms


def test_ssh_config_file(docker_instance):
    assert docker_instance.ssh_config_file is None


def test_ansible_connection_params(docker_instance):
    d = docker_instance.ansible_connection_params

    assert 'root' == d['user']
    assert 'docker' == d['connection']


def test_serverspec_args(docker_instance):
    assert {} == docker_instance.serverspec_args


def test_up(docker_instance):
    docker_instance.up()


def test_status(docker_instance):
    docker_instance.up()

    assert 'test1' == docker_instance.status()[0].name
    assert 'test2' == docker_instance.status()[1].name

    assert 'Up' in docker_instance.status()[0].state
    assert 'Up' in docker_instance.status()[1].state

    assert 'docker' in docker_instance.status()[0].provider
    assert 'docker' in docker_instance.status()[1].provider


def test_status_dirty_shutdown(docker_instance):
    docker_instance.up()
    docker_instance._docker.stop('test1', timeout=0)

    assert 'not_created' in docker_instance.status()[0].state
    assert 'Up' in docker_instance.status()[1].state


def test_port_bindings(docker_instance):
    docker_instance.up()
    ports = sorted(
        docker_instance.status()[0].ports, key=lambda k: k['PublicPort'])
    expected = [{
        'PublicPort': 80,
        'PrivatePort': 80,
        'IP': '0.0.0.0',
        'Type': 'tcp'
    }, {
        'PublicPort': 443,
        'PrivatePort': 443,
        'IP': '0.0.0.0',
        'Type': 'tcp'
    }]

    assert expected == ports
    assert docker_instance.status()[1].ports == []


def test_start_command(docker_instance):
    docker_instance.up()

    assert "/bin/sh" in docker_instance._docker.inspect_container('test2')[
        'Config']['Cmd']
    assert "/bin/bash" in docker_instance._docker.inspect_container('test1')[
        'Config']['Cmd']


def test_volume_mounts(docker_instance):
    docker_instance.up()

    assert "/tmp/test1" in docker_instance._docker.inspect_container('test1')[
        'Mounts'][0]['Source']
    assert "/inside" in docker_instance._docker.inspect_container('test1')[
        'Mounts'][0]['Destination']


def test_cap_add(docker_instance):
    docker_instance.up()

    assert "SYS_ADMIN" in docker_instance._docker.inspect_container('test1')[
        'HostConfig']['CapAdd']
    assert "SETPCAP" in docker_instance._docker.inspect_container('test1')[
        'HostConfig']['CapAdd']


def test_cap_drop(docker_instance):
    docker_instance.up()

    assert "MKNOD" in docker_instance._docker.inspect_container('test1')[
        'HostConfig']['CapDrop']


def test_destroy(docker_instance):
    docker_instance.up()

    assert 'test1' == docker_instance.status()[0].name
    assert 'test2' == docker_instance.status()[1].name

    assert 'Up' in docker_instance.status()[0].state
    assert 'Up' in docker_instance.status()[1].state

    docker_instance.destroy()

    assert 'not_created' in docker_instance.status()[0].state
    assert 'not_created' in docker_instance.status()[1].state


def test_provision(docker_molecule_instance, docker_instance):
    docker_molecule_instance.driver = docker_instance
    docker_molecule_instance.config.config['ansible'].update({
        'inventory': 'test1,test2,'
    })
    docker_instance.up()
    ansible = ansible_playbook.AnsiblePlaybook(
        docker_molecule_instance.config.config['ansible'],
        docker_molecule_instance.driver.ansible_connection_params)

    assert (None, '') == ansible.execute()


def test_inventory_generation(docker_molecule_instance, docker_instance):
    docker_molecule_instance.driver = docker_instance
    docker_molecule_instance.config.config['ansible'].update({
        'inventory': 'test1,test2,'
    })
    docker_molecule_instance.driver.up()
    docker_molecule_instance.create_inventory_file()
    ansible = ansible_playbook.AnsiblePlaybook(
        docker_molecule_instance.config.config['ansible'],
        docker_molecule_instance.driver.ansible_connection_params)

    for instance in docker_molecule_instance.driver.instances:
        expected = '{} ansible_connection=docker\n'.format(instance['name'])

        assert expected == docker_molecule_instance.driver.inventory_entry(
            instance)

    assert (None, '') == ansible.execute()


def test_environment(docker_instance):
    docker_instance.up()
    d1 = docker_instance._docker.inspect_container('test1')['Config']['Env']
    assert 'FOO=BAR' in d1
    assert 'BAZ=QUX' in d1

    d2 = docker_instance._docker.inspect_container('test2')['Config']['Env']
    assert 'FOO=BAR' not in d2
    assert 'BAZ=QUX' not in d2

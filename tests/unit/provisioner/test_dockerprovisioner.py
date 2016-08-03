#  Copyright (c) 2015-2016 Cisco Systems
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

import distutils.spawn
import distutils.version
import pytest

import ansible

from molecule import ansible_playbook
from molecule import config
from molecule import core
from molecule.provisioners import dockerprovisioner


def ansible_v1():
    d = distutils.version
    return (d.LooseVersion(ansible.__version__) < d.LooseVersion('2.0'))


def get_docker_executable():
    return distutils.spawn.find_executable('docker')


if not get_docker_executable():
    pytestmark = pytest.mark.skip(
        'No docker executable found - skipping docker tests')
elif ansible_v1():
    pytestmark = pytest.mark.skip(
        'No Ansible v2 executable found - skipping docker tests')


@pytest.fixture()
def molecule_instance(temp_files):
    c = temp_files(fixtures=['molecule_docker_config'])
    m = core.Molecule(dict())
    m.config = config.Config(configs=c)

    return m


@pytest.fixture()
def docker_instance(molecule_instance, request):
    d = dockerprovisioner.DockerProvisioner(molecule_instance)

    def cleanup():
        d.destroy()

    request.addfinalizer(cleanup)

    return d


def test_name(docker_instance):
    # false values don't exist in arg dict at all
    assert 'docker' == docker_instance.name


def test_get_provisioner(molecule_instance):
    assert 'docker' == molecule_instance.get_provisioner().name


def test_up(docker_instance):
    docker_instance.up()


def test_instances(docker_instance):
    assert 'test1' == docker_instance.instances[0]['name']
    assert 'test2' == docker_instance.instances[1]['name']


def test_status(docker_instance):
    docker_instance.up()

    assert 'test1' == docker_instance.status()[1].name
    assert 'test2' == docker_instance.status()[0].name

    assert 'Up' in docker_instance.status()[1].state
    assert 'Up' in docker_instance.status()[0].state

    assert 'docker' in docker_instance.status()[0].provider
    assert 'docker' in docker_instance.status()[1].provider


def test_port_bindings(docker_instance):
    docker_instance.up()

    assert docker_instance.status()[0].ports == []
    assert docker_instance.status()[1].ports == [
        {
            'PublicPort': 443,
            'PrivatePort': 443,
            'IP': '0.0.0.0',
            'Type': 'tcp'
        }, {
            'PublicPort': 80,
            'PrivatePort': 80,
            'IP': '0.0.0.0',
            'Type': 'tcp'
        }
    ]


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


def test_destroy(docker_instance):
    docker_instance.up()

    assert 'test1' == docker_instance.status()[1].name
    assert 'test2' == docker_instance.status()[0].name

    assert 'Up' in docker_instance.status()[1].state
    assert 'Up' in docker_instance.status()[0].state

    docker_instance.destroy()

    assert 'Not Created' in docker_instance.status()[1].state
    assert 'Not Created' in docker_instance.status()[0].state


def test_provision(docker_instance):
    docker_instance.up()
    pb = docker_instance.ansible_connection_params
    pb['playbook'] = 'playbook.yml'
    pb['inventory'] = 'test1,test2,'
    ansible = ansible_playbook.AnsiblePlaybook(pb)

    # TODO(retr0h): Understand why provisioner is None
    assert (None, '') == ansible.execute()


def test_inventory_generation(molecule_instance, docker_instance):
    molecule_instance._provisioner = docker_instance

    molecule_instance._provisioner.up()
    molecule_instance._create_inventory_file()

    pb = molecule_instance._provisioner.ansible_connection_params
    pb['playbook'] = 'playbook.yml'
    pb['inventory'] = 'test1,test2,'
    ansible = ansible_playbook.AnsiblePlaybook(pb)

    # TODO(retr0h): Understand why provisioner is None
    assert (None, '') == ansible.execute()

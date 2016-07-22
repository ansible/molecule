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

import pytest

from molecule import config
from molecule import core
from molecule import ansible_playbook
from molecule.provisioners import dockerprovisioner

# TODO(retr0h): Implement finalizer (teardown).


@pytest.fixture()
def docker_data():
    return {
        'molecule': {
            'molecule_dir': '.test_molecule',
            'inventory_file': 'tests/support/ansible_inventory'
        },
        'docker': {
            'containers': [
                {'name': 'test1',
                 'image': 'ubuntu',
                 'image_version': 'latest',
                 'ansible_groups': ['group1']}, {'name': 'test2',
                                                 'image': 'ubuntu',
                                                 'image_version': 'latest',
                                                 'ansible_groups':
                                                 ['group2']}
            ]
        }
    }


@pytest.fixture()
def molecule_instance(temp_files, docker_data):
    c = temp_files(content=[docker_data])
    m = core.Molecule(dict())
    m._config = config.Config(configs=c)

    return m


@pytest.fixture()
def docker_instance(molecule_instance):
    d = dockerprovisioner.DockerProvisioner(molecule_instance)

    return d


def test_name(docker_instance):
    # false values don't exist in arg dict at all
    assert 'docker' == docker_instance.name


def test_get_provisioner(molecule_instance):
    assert 'docker' == molecule_instance.get_provisioner().name


def test_up(docker_instance):
    docker_instance.up()
    docker_instance.destroy()


def test_instances(docker_instance):
    assert 'test1' == docker_instance.instances[0]['name']
    assert 'test2' == docker_instance.instances[1]['name']

    docker_instance.destroy()


def test_status(docker_instance):
    docker_instance.up()

    assert 'test1' == docker_instance.status()[1].name
    assert 'test2' == docker_instance.status()[0].name

    assert 'Up' in docker_instance.status()[1].state
    assert 'Up' in docker_instance.status()[0].state

    assert 'docker' in docker_instance.status()[0].provider
    assert 'docker' in docker_instance.status()[1].provider

    docker_instance.destroy()


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
    pb['playbook'] = 'tests/support/playbook.yml'
    pb['inventory'] = 'test1,test2,'
    ansible = ansible_playbook.AnsiblePlaybook(pb)

    # TODO(retr0h): Understand why provisioner is None
    assert (None, '') == ansible.execute()

    docker_instance.destroy()


def test_inventory_generation(molecule_instance, docker_instance):
    molecule_instance._provisioner = docker_instance

    molecule_instance._provisioner.up()
    molecule_instance._create_inventory_file()

    pb = molecule_instance._provisioner.ansible_connection_params
    pb['playbook'] = 'tests/support/playbook.yml'
    pb['inventory'] = 'tests/support/ansible_inventory'
    ansible = ansible_playbook.AnsiblePlaybook(pb)

    assert (None, '') == ansible.execute()

    # TODO(retr0h): Understand why provisioner is None
    molecule_instance._provisioner.destroy()

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

import os

import pytest

from molecule import core
from molecule import ansible_playbook
from molecule.provisioners import dockerprovisioner

# TODO(retr0h): Implement finalizer (teardown).


@pytest.fixture()
def molecule_file(tmpdir, request):
    d = tmpdir.mkdir('molecule')
    c = d.join(os.extsep.join(('molecule', 'yml')))
    data = {
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
        },
        'ansible': {
            'config_file': 'test_config',
            'inventory_file': 'test_inventory'
        }
    }
    c.write(data)

    def cleanup():
        os.remove(c.strpath)
        os.rmdir(d.strpath)

    request.addfinalizer(cleanup)

    return c.strpath


@pytest.fixture()
def molecule(molecule_file):
    m = core.Molecule(dict())
    m._config.load_defaults_file(defaults_file=molecule_file)
    m._state = dict()

    return m


def test_name(molecule):
    docker_provisioner = dockerprovisioner.DockerProvisioner(molecule)

    # false values don't exist in arg dict at all
    assert 'docker' == docker_provisioner.name


def test_get_provisioner(molecule):
    assert 'docker' == molecule.get_provisioner().name


def test_up(molecule):
    docker_provisioner = dockerprovisioner.DockerProvisioner(molecule)
    docker_provisioner.up()
    docker_provisioner.destroy()


def test_instances(molecule):
    docker_provisioner = dockerprovisioner.DockerProvisioner(molecule)

    assert 'test1' == docker_provisioner.instances[0]['name']
    assert 'test2' == docker_provisioner.instances[1]['name']

    docker_provisioner.destroy()


def test_status(molecule):
    docker_provisioner = dockerprovisioner.DockerProvisioner(molecule)

    docker_provisioner.up()

    assert 'test1' == docker_provisioner.status()[1].name
    assert 'test2' == docker_provisioner.status()[0].name

    assert 'Up' in docker_provisioner.status()[1].state
    assert 'Up' in docker_provisioner.status()[0].state

    assert 'docker' in docker_provisioner.status()[0].provider
    assert 'docker' in docker_provisioner.status()[1].provider

    docker_provisioner.destroy()


def test_destroy(molecule):
    docker_provisioner = dockerprovisioner.DockerProvisioner(molecule)

    docker_provisioner.up()

    assert 'test1' == docker_provisioner.status()[1].name
    assert 'test2' == docker_provisioner.status()[0].name

    assert 'Up' in docker_provisioner.status()[1].state
    assert 'Up' in docker_provisioner.status()[0].state

    docker_provisioner.destroy()

    assert 'Not Created' in docker_provisioner.status()[1].state
    assert 'Not Created' in docker_provisioner.status()[0].state


def test_provision(molecule):
    docker_provisioner = dockerprovisioner.DockerProvisioner(molecule)

    docker_provisioner.destroy()
    docker_provisioner.up()

    pb = docker_provisioner.ansible_connection_params
    pb['playbook'] = 'tests/support/playbook.yml'
    pb['inventory'] = 'test1,test2,'
    ansible = ansible_playbook.AnsiblePlaybook(pb)

    # TODO(retr0h): Understand why provisioner is None
    assert (None, '') == ansible.execute()

    docker_provisioner.destroy()


def test_inventory_generation(molecule):
    molecule._provisioner = dockerprovisioner.DockerProvisioner(molecule)

    molecule._provisioner.up()
    molecule._create_inventory_file()

    pb = molecule._provisioner.ansible_connection_params
    pb['playbook'] = 'tests/support/playbook.yml'
    pb['inventory'] = 'tests/support/ansible_inventory'
    ansible = ansible_playbook.AnsiblePlaybook(pb)

    assert (None, '') == ansible.execute()

    # TODO(retr0h): Understand why provisioner is None
    molecule._provisioner.destroy()

#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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

import logging
import os
import os.path
import random
import shutil
import string

import pytest

from molecule import config
from molecule import core
from molecule import state

logging.getLogger("sh").setLevel(logging.WARNING)

pytest_plugins = ['helpers_namespace']


def random_string(l=5):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(l))


@pytest.helpers.register
def os_split(s):
    rest, tail = os.path.split(s)
    if rest in ('', os.path.sep):
        return tail,
    return os_split(rest) + (tail, )


@pytest.fixture()
def temp_dir(tmpdir, request):
    d = tmpdir.mkdir(random_string())
    os.chdir(d.strpath)

    def cleanup():
        shutil.rmtree(d.strpath)

    request.addfinalizer(cleanup)

    return d.strpath


@pytest.fixture()
def temp_files(tmpdir, request):
    def wrapper(fixtures=[]):
        d = tmpdir.mkdir(random_string())
        confs = []
        for index, fixture in enumerate(fixtures):
            c = d.join(os.extsep.join((fixture, 'yml')))
            c.write(request.getfuncargvalue(fixtures[index]))
            confs.append(c.strpath)

        def cleanup():
            shutil.rmtree(d.strpath)

        request.addfinalizer(cleanup)

        return confs

    return wrapper


@pytest.fixture()
def molecule_instance(temp_dir, temp_files, state_path_without_data):
    c = temp_files(fixtures=['molecule_vagrant_config'])
    m = core.Molecule({})
    m.config = config.Config(configs=c)
    m.state = state.State(state_file=state_path_without_data)
    m.main()

    return m


@pytest.fixture()
def molecule_vagrant_config(molecule_section_data, vagrant_section_data,
                            ansible_section_data):
    return reduce(
        lambda x, y: config.merge_dicts(x, y),
        [molecule_section_data, vagrant_section_data, ansible_section_data])


@pytest.fixture()
def molecule_docker_config(molecule_section_data, docker_section_data,
                           ansible_section_data):
    return reduce(
        lambda x, y: config.merge_dicts(x, y),
        [molecule_section_data, docker_section_data, ansible_section_data])


@pytest.fixture()
def molecule_openstack_config(molecule_section_data, openstack_section_data,
                              ansible_section_data):
    return reduce(
        lambda x, y: config.merge_dicts(x, y),
        [molecule_section_data, openstack_section_data, ansible_section_data])


@pytest.fixture()
def molecule_section_data(state_path_without_data):
    return {
        'molecule': {
            'ignore_paths': [
                '.git', '.vagrant', '.molecule'
            ],
            'serverspec_dir': 'spec',
            'testinfra_dir': 'tests',
            'goss_dir': 'tests',
            'goss_playbook': 'test_default.yml',
            'molecule_dir': 'test',
            'state_file': state_path_without_data,
            'vagrantfile_file': 'vagrantfile_file',
            'rakefile_file': 'rakefile_file',
            'vagrantfile_template': 'vagrantfile.j2',
            'raw_ssh_args': [
                '-o StrictHostKeyChecking=no',
                '-o UserKnownHostsFile=/dev/null'
            ],
            'test': {
                'sequence': [
                    'destroy', 'syntax', 'create', 'converge', 'idempotence',
                    'verify'
                ]
            }
        }
    }


@pytest.fixture()
def vagrant_section_data():
    return {
        'vagrant': {
            'platforms': [
                {'name': 'ubuntu',
                 'box': 'ubuntu/trusty64'}
            ],
            'providers': [
                {'name': 'virtualbox',
                 'type': 'virtualbox'}
            ],
            'instances': [
                {'name': 'aio-01',
                 'ansible_groups': ['example', 'example1'],
                 'options': {'append_platform_to_hostname': True}}
            ]
        }
    }


@pytest.fixture()
def docker_section_data():
    return {
        'docker': {
            'containers': [
                {'name': 'test1',
                 'image': 'ubuntu',
                 'image_version': 'latest',
                 'port_bindings': {
                     80: 80,
                     443: 443
                 },
                 'options': {'append_platform_to_hostname': True},
                 'volume_mounts': ['/tmp/test1:/inside:rw'],
                 'cap_add': ['SYS_ADMIN', 'SETPCAP'],
                 'cap_drop': ['MKNOD'],
                 'ansible_groups': ['group1']}, {
                     'name': 'test2',
                     'image': 'ubuntu',
                     'image_version': 'latest',
                     'ansible_groups': ['group2'],
                     'command': '/bin/sh',
                     'options': {'append_platform_to_hostname': True},
                 }
            ]
        }
    }


@pytest.fixture()
def openstack_section_data():
    return {'openstack': {
        'instances': [
            {'name': 'aio-01',
             'ansible_groups': ['example', 'example1'],
             'options': {'append_platform_to_hostname': True}}
        ]
    }}


@pytest.fixture()
def ansible_section_data(playbook):
    return {
        'ansible': {
            'timeout': 30,
            'sudo': True,
            'sudo_user': False,
            'ask_sudo_pass': False,
            'ask_vault_pass': False,
            'vault_password_file': False,
            'limit': 'all',
            'verbose': True,
            'diff': True,
            'tags': False,
            'host_key_checking': False,
            'raw_ssh_args': [
                '-o UserKnownHostsFile=/dev/null', '-o IdentitiesOnly=yes',
                '-o ControlMaster=auto', '-o ControlPersist=60s'
            ],
            'galaxy': {},
            'config_file': 'config_file',
            'inventory_file': 'inventory_file',
            'playbook': playbook,
            'raw_env_vars': {
                'FOO': 'bar'
            }
        },
        'verifier': {
            'name': 'testinfra',
            'options': {}
        }
    }


@pytest.fixture()
def state_data():
    return {
        'converged': None,
        'created': True,
        'default_platform': None,
        'default_provider': None,
        'driver': None,
        'hosts': {},
        'multiple_platforms': None
    }


@pytest.fixture()
def state_path_with_data(temp_files):
    return temp_files(fixtures=['state_data'])[0]


@pytest.fixture()
def state_path_without_data(tmpdir, request):
    d = tmpdir.mkdir(random_string())
    c = d.join(os.extsep.join(('state', 'yml')))

    def cleanup():
        shutil.rmtree(d.strpath)

    request.addfinalizer(cleanup)

    return c.strpath


@pytest.fixture()
def playbook_data():
    return [{'hosts': 'all', 'tasks': [{'command': 'echo'}]}]


@pytest.fixture()
def playbook(temp_files):
    return temp_files(fixtures=['playbook_data'])[0]


@pytest.fixture()
def patched_ansible_playbook(mocker):
    return mocker.patch('molecule.ansible_playbook.AnsiblePlaybook.execute')


@pytest.fixture()
def patched_ansible_galaxy(mocker):
    return mocker.patch('molecule.ansible_galaxy.AnsibleGalaxy.execute')

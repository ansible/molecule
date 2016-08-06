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

import logging
import os
import os.path
import random
import shutil
import string

import pytest

from molecule import utilities

logging.getLogger("sh").setLevel(logging.WARNING)


def random_string(l=5):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(l))


@pytest.fixture()
def temp_files(tmpdir, request):
    def wrapper(fixtures=[]):
        d = tmpdir.mkdir(random_string())
        confs = []
        for index, fixture in enumerate(fixtures):
            c = d.join(os.extsep.join((fixture, 'yml')))
            c.write(request.getfuncargvalue(fixtures[index]))
            confs.append(c.strpath)

        # TODO(retr0h): Remove - belongs elsewhere
        pbook = d.join(os.extsep.join(('playbook', 'yml')))
        data = [{'hosts': 'all', 'tasks': [{'command': 'echo'}]}]
        pbook.write(data)
        os.chdir(d.strpath)

        # TODO(retr0h): Remove - belongs elsewhere

        def cleanup():
            shutil.rmtree(d.strpath)

        request.addfinalizer(cleanup)

        return confs

    return wrapper


@pytest.fixture()
def molecule_vagrant_config(molecule_section_data, vagrant_section_data,
                            ansible_section_data):
    return reduce(
        lambda x, y: utilities.merge_dicts(x, y),
        [molecule_section_data, vagrant_section_data, ansible_section_data])


@pytest.fixture()
def molecule_docker_config(molecule_section_data, docker_section_data,
                           ansible_section_data):
    return reduce(
        lambda x, y: utilities.merge_dicts(x, y),
        [molecule_section_data, docker_section_data, ansible_section_data])


@pytest.fixture()
def molecule_section_data(state_path):
    return {
        'molecule': {
            'ignore_paths': [
                '.git', '.vagrant', '.molecule'
            ],
            'serverspec_dir': 'spec',
            'testinfra_dir': 'tests',
            'molecule_dir': 'test',
            'state_file': state_path,
            'vagrantfile_file': 'vagrantfile_file',
            'rakefile_file': 'rakefile_file',
            'vagrantfile_template': 'vagrantfile.j2',
            'ansible_config_template': 'ansible.cfg.j2',
            'rakefile_template': 'rakefile.j2',
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
                 'volume_mounts': ['/tmp/test1:/inside:rw'],
                 'ansible_groups': ['group1']}, {'name': 'test2',
                                                 'image': 'ubuntu',
                                                 'image_version': 'latest',
                                                 'ansible_groups':
                                                 ['group2'],
                                                 'command': '/bin/sh'}
            ]
        }
    }


@pytest.fixture()
def ansible_section_data():
    return {
        'ansible': {
            'timeout': 30,
            'sudo': True,
            'sudo_user': False,
            'ask_sudo_pass': False,
            'ask_vault_pass': False,
            'vault_password_file': False,
            'limit': 'all',
            'verbose': False,
            'diff': True,
            'tags': False,
            'host_key_checking': False,
            'raw_ssh_args': [
                '-o UserKnownHostsFile=/dev/null', '-o IdentitiesOnly=yes',
                '-o ControlMaster=auto', '-o ControlPersist=60s'
            ],
            'config_file': 'config_file',
            'inventory_file': 'inventory_file',
            'playbook': 'playbook.yml'
        }
    }


@pytest.fixture()
def state_data():
    return {}


@pytest.fixture()
def state_path(temp_files):
    return temp_files(fixtures=['state_data'])[0]

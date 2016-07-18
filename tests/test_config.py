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

from molecule import config


@pytest.fixture()
def molecule_file(tmpdir, request):
    d = tmpdir.mkdir('molecule')
    c = d.join(os.extsep.join(('molecule', 'yml')))
    data = {
        'molecule': {
            'molecule_dir': '.test_molecule'
        },
        'vagrant': {
            'instances': [
                {'name': 'aio-01',
                 'options': {'append_platform_to_hostname': True}}
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


def test_load_defaults_file():
    c = config.Config()
    c.load_defaults_file()

    assert '.molecule' == c.config['molecule']['molecule_dir']


def test_load_defaults_external_file(molecule_file):
    c = config.Config()
    c.load_defaults_file(defaults_file=molecule_file)

    assert '.test_molecule' == c.config['molecule']['molecule_dir']


def test_merge_molecule_config_files(molecule_file):
    c = config.Config()
    c.load_defaults_file()
    c.merge_molecule_config_files(paths=[molecule_file])

    assert '.test_molecule' == c.config['molecule']['molecule_dir']


def test_merge_molecule_file(molecule_file):
    c = config.Config()
    c.load_defaults_file()
    c.merge_molecule_file(molecule_file=molecule_file)

    assert '.test_molecule' == c.config['molecule']['molecule_dir']


def test_build_easy_paths():
    c = config.Config()
    c.load_defaults_file()
    c.build_easy_paths()

    assert '.molecule/state' == c.config['molecule']['state_file']
    assert '.molecule/vagrantfile' == c.config['molecule']['vagrantfile_file']
    assert '.molecule/rakefile' == c.config['molecule']['rakefile_file']
    assert '.molecule/ansible.cfg' == c.config['molecule']['config_file']
    assert '.molecule/ansible_inventory' == c.config['molecule'][
        'inventory_file']


def test_update_ansible_defaults(molecule_file):
    c = config.Config()
    c.load_defaults_file()
    c.merge_molecule_file(molecule_file=molecule_file)

    assert 'test_inventory' == c.config['ansible']['inventory_file']
    assert 'test_config' == c.config['ansible']['config_file']


def test_populate_instance_names(molecule_file):
    c = config.Config()
    c.load_defaults_file()
    c.merge_molecule_file(molecule_file=molecule_file)
    c.populate_instance_names('rhel-7')

    assert 'aio-01-rhel-7' == c.config['vagrant']['instances'][0]['vm_name']

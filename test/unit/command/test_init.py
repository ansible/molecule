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

import os

import pytest

from molecule.command import init


@pytest.fixture()
def molecule_dir(tmpdir):
    d = tmpdir.mkdir('test_molecule')
    os.chdir(d.strpath)

    return d.strpath


def test_create_role(molecule_dir):
    i = init.Init('unit_test1', dict())
    with pytest.raises(SystemExit):
        i.execute()

    assert os.path.isdir(os.path.join(molecule_dir, 'unit_test1'))
    assert os.path.isfile(os.path.join(molecule_dir, 'unit_test1',
                                       'molecule.yml'))


def test_create_role_in_existing_directory(molecule_dir):
    i = init.Init(dict(), dict())
    with pytest.raises(SystemExit):
        i.execute()

    assert os.path.isdir(os.path.join(molecule_dir))


def test_create_role_docker_flag(molecule_dir):
    i = init.Init(['docker_test', '--docker'], dict())
    with pytest.raises(SystemExit):
        i.execute()

    os.chdir(os.path.join(molecule_dir, 'docker_test'))

    with open('molecule.yml') as f:
        assert 'docker' in f.read()


def test_create_role_offline_flag():
    i = init.Init(['offline_test', '--offline'], dict())
    with pytest.raises(SystemExit):
        i.execute()

    os.chdir('offline_test')

    assert os.path.isdir('tests')
    assert os.path.isdir('tasks')
    assert os.path.isfile('molecule.yml')


def test_create_role_openstack_flag(molecule_dir):
    i = init.Init(['docker_test', '--openstack'], dict())
    with pytest.raises(SystemExit):
        i.execute()

    os.chdir(os.path.join(molecule_dir, 'docker_test'))

    with open('molecule.yml') as f:
        assert 'openstack' in f.read()


def test_create_role_existing_dir_error():
    os.mkdir('test1')
    i = init.Init(['test1'], dict())
    with pytest.raises(SystemExit) as f:
        i.execute()
        assert 'Cannot create new role.' in f

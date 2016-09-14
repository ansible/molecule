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


@pytest.fixture
def init_command_args():
    return {'role': 'docker_test',
            'driver': 'vagrant',
            'verifier': 'testinfra'}


def test_create_role(temp_dir, init_command_args):
    init_command_args.update({'role': 'unit_test1'})
    i = init.Init({}, init_command_args)
    with pytest.raises(SystemExit):
        i.execute()

    assert os.path.isdir(os.path.join(temp_dir, 'unit_test1'))
    assert os.path.isfile(os.path.join(temp_dir, 'unit_test1', 'molecule.yml'))


def test_create_role_in_existing_directory(temp_dir, init_command_args):
    del init_command_args['role']
    i = init.Init({}, init_command_args)
    with pytest.raises(SystemExit):
        i.execute()

    assert os.path.isdir(os.path.join(temp_dir))


def test_create_role_existing_dir_error(temp_dir, init_command_args):
    os.mkdir('test1')
    init_command_args.update({'role': 'test1'})
    i = init.Init({}, init_command_args)
    with pytest.raises(SystemExit) as f:
        i.execute()
        assert 'Cannot create new role.' in f


@pytest.mark.parametrize('driver', ['vagrant', 'docker', 'openstack'])
def test_create_role_with_driver_flag(driver, temp_dir, init_command_args):
    init_command_args.update({'driver': driver})
    i = init.Init({}, init_command_args)
    with pytest.raises(SystemExit):
        i.execute()

    os.chdir(os.path.join(temp_dir, 'docker_test'))

    with open('molecule.yml') as f:
        assert driver in f.read()


@pytest.mark.parametrize('verifier', ['testinfra', 'serverspec', 'goss'])
def test_create_role_with_verifier_flag(verifier, temp_dir, init_command_args):
    init_command_args.update({'verifier': verifier})
    i = init.Init({}, init_command_args)
    with pytest.raises(SystemExit):
        i.execute()

    os.chdir(os.path.join(temp_dir, 'docker_test'))

    with open('molecule.yml') as f:
        assert verifier in f.read()

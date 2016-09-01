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
import re

from molecule import config
from molecule import core
from molecule import state
from molecule.driver import openstackdriver

# TODO(retr0h): Test instance create/delete through the openstack instance.


@pytest.fixture()
def molecule_instance(temp_files, state_path):
    c = temp_files(fixtures=['molecule_openstack_config'])
    m = core.Molecule(dict())
    m.config = config.Config(configs=c)
    m.state = state.State(state_file=state_path)

    return m


@pytest.fixture()
def openstack_instance(molecule_instance, request):
    return openstackdriver.OpenstackDriver(molecule_instance)


def test_name(openstack_instance):
    assert 'openstack' == openstack_instance.name


def test_instances(openstack_instance):
    assert 'aio-01' == openstack_instance.instances[0]['name']


def test_default_provider(openstack_instance):
    assert 'openstack' == openstack_instance.default_provider


def test_default_platform(openstack_instance):
    assert 'openstack' == openstack_instance.default_platform


def test_provider(openstack_instance):
    assert 'openstack' == openstack_instance.provider


def test_platform(openstack_instance):
    assert 'openstack' == openstack_instance.platform


def test_platform_setter(openstack_instance):
    openstack_instance.platform = 'foo_platform'

    assert 'foo_platform' == openstack_instance.platform


def test_valid_providers(openstack_instance):
    assert [{'name': 'openstack'}] == openstack_instance.valid_providers


def test_valid_platforms(openstack_instance):
    assert [{'name': 'openstack'}] == openstack_instance.valid_platforms


def test_ssh_config_file(openstack_instance):
    assert openstack_instance.ssh_config_file is None


def test_ansible_connection_params(openstack_instance):
    d = openstack_instance.ansible_connection_params

    assert 'ssh' == d['connection']


def test_serverspec_args(openstack_instance):
    assert {} == openstack_instance.serverspec_args


def test_reset_known_hosts(openstack_instance, mocker):
    mocked = mocker.patch('os.system')
    openstack_instance._reset_known_host_key('test')

    mocked.assert_called_once_with('ssh-keygen -R test')


def test_generate_temp_ssh_key(openstack_instance):
    fileloc = openstack_instance._generated_ssh_key_location()

    openstack_instance._generate_temp_ssh_key()
    assert os.path.isfile(fileloc)
    assert os.path.isfile(fileloc + '.pub')


def test_delete_temp_ssh_key(openstack_instance):
    fileloc = openstack_instance._generated_ssh_key_location()

    openstack_instance._remove_temp_ssh_key()
    assert not os.path.isfile(fileloc)
    assert not os.path.isfile(fileloc + '.pub')


def test_generate_random_keypair_name(openstack_instance):
    result_keypair = openstack_instance._generate_random_keypair_name(
        'molecule', 10)
    assert re.match(r'molecule_[0-9a-fA-F]+', result_keypair)

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

import os
import pytest
import re

from molecule.driver import openstackdriver

# TODO(retr0h): Test instance create/delete through the openstack instance.


@pytest.fixture()
def openstack_instance(openstack_molecule_instance, request):
    return openstackdriver.OpenstackDriver(openstack_molecule_instance)


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


def test_testinfra_args(openstack_instance):
    d = openstack_instance.testinfra_args

    # TODO: Test ansible_inventory key
    assert 'ansible' == d['connection']


def test_serverspec_args(openstack_instance):
    assert {} == openstack_instance.serverspec_args


def test_login_cmd(openstack_instance):
    assert 'ssh {} -l {} -i {}' == openstack_instance.login_cmd('aio-01')


def test_login_args(openstack_instance):
    login_args = openstack_instance.login_args('aio-01')

    assert login_args[0] is None
    assert 'root' == login_args[1]
    assert re.match(r'.*\.ssh/molecule_[0-9a-fA-F]+$', login_args[2])


def test_reset_known_hosts(openstack_instance, mocker):
    patched_os = mocker.patch('os.system')
    openstack_instance._reset_known_host_key('test')

    patched_os.assert_called_once_with('ssh-keygen -R test')


def test_get_temp_keyfile(openstack_instance):
    fileloc = openstack_instance._get_temp_keyfile()

    assert os.path.isfile(fileloc)
    assert os.path.isfile(fileloc + '.pub')


def test_cleanup_temp_keyfile(openstack_instance):
    fileloc = openstack_instance._get_temp_keyfile()
    openstack_instance._cleanup_temp_keyfile()

    assert not os.path.isfile(fileloc)
    assert not os.path.isfile(fileloc + '.pub')


def test_get_temp_keyname(openstack_instance):
    result_keypair = openstack_instance._get_temp_keyname()

    assert re.match(r'molecule_[0-9a-fA-F]+', result_keypair)

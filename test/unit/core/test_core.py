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

import pytest

from molecule.driver import basedriver
from molecule.driver import vagrantdriver


def test_driver(molecule_instance):
    assert isinstance(molecule_instance.driver, vagrantdriver.VagrantDriver)


def test_driver_setter(molecule_instance):
    molecule_instance.driver = 'foo'

    assert 'foo' == molecule_instance.driver


def test_get_driver_name_from_cli(molecule_instance):
    molecule_instance.args.update({'driver': 'foo'})

    assert 'foo' == molecule_instance._get_driver_name()


def test_get_driver_name_from_state(molecule_instance):
    m = molecule_instance
    m.state.change_state('driver', 'foo')

    assert 'foo' == molecule_instance._get_driver_name()


def test_get_driver_name_from_config(molecule_instance):
    m = molecule_instance
    m.config.config['driver'] = {'name': 'foo'}

    assert 'foo' == molecule_instance._get_driver_name()


def test_driver_precedence(molecule_instance):
    m = molecule_instance
    m.config.config = {}

    m.config.config['openstack'] = 'foo'
    assert 'openstack' == molecule_instance._get_driver_name()

    m.config.config['docker'] = 'foo'
    assert 'docker' == molecule_instance._get_driver_name()

    m.config.config['vagrant'] = 'foo'
    assert 'vagrant' == molecule_instance._get_driver_name()

    m.config.config['driver'] = {'name': 'foo'}
    assert 'foo' == molecule_instance._get_driver_name()

    m.state.change_state('driver', 'bar')
    assert 'bar' == molecule_instance._get_driver_name()

    m.args.update({'driver': 'foobar'})
    assert 'foobar' ==  molecule_instance._get_driver_name()


def test_get_driver_invalid_instance(molecule_instance):
    del molecule_instance.config.config['vagrant']

    with pytest.raises(basedriver.InvalidDriverSpecified):
        molecule_instance._get_driver()


def test_verifier_setter(molecule_instance):
    molecule_instance.verifier = 'foo'

    assert 'foo' == molecule_instance.verifier


def test_verifier(molecule_instance):
    assert 'testinfra' == molecule_instance.verifier


def test_verifier_backward_compatible(molecule_instance):
    m = molecule_instance
    m.config.config['testinfra'] = {}

    assert 'testinfra' == m.verifier


def test_verifier_disabled_setter(molecule_instance):
    molecule_instance.disabled = 'foo'

    assert 'foo' == molecule_instance.disabled


def test_verifier_disabled(molecule_instance):
    assert [] == molecule_instance.disabled


def test_dependency_setter(molecule_instance):
    molecule_instance.dependency = 'foo'

    assert 'foo' == molecule_instance.dependency


def test_dependency(molecule_instance):
    assert 'galaxy' == molecule_instance.dependency


def test_envvar_expansion_dictkey(molecule_instance_with_env_expansion):
    assert 'vagrant' == molecule_instance_with_env_expansion._get_driver_name()


def test_envvar_expansion_multiple_vars(molecule_instance_with_env_expansion):
    m = molecule_instance_with_env_expansion
    assert 'ubuntu/trusty64' == m.config.config['vagrant']['platforms'][0][
        'box']


def test_envvar_expansion_in_list(molecule_instance_with_env_expansion):
    m = molecule_instance_with_env_expansion
    assert 'example1' == m.config.config['vagrant']['instances'][0][
        'ansible_groups'][1]


def test_envvar_expansion_deeply_nested(molecule_instance_with_env_expansion):
    m = molecule_instance_with_env_expansion
    assert 'append_platform_to_hostname' in m.config.config['vagrant'][
        'instances'][0]['options']


@pytest.mark.skip(reason='TODO(retr0h): Determine best way to test this')
def test_remove_templates():
    pass


@pytest.mark.skip(reason='TODO(retr0h): Determine best way to test this')
def test_create_templates():
    pass


@pytest.mark.skip(reason='TODO(retr0h): Determine best way to test this')
def test_write_instances_state():
    pass


@pytest.mark.skip(reason='TODO(retr0h): Determine best way to test this')
def test_create_inventory_file():
    pass


@pytest.mark.skip(reason='TODO(retr0h): Determine best way to test this')
def test_remove_inventory_file():
    pass


@pytest.mark.skip(reason='TODO(retr0h): Determine best way to test this')
def test_add_or_update_vars():
    pass


@pytest.mark.skip(reason='TODO(retr0h): Determine best way to test this')
def test_symlink_vars():
    pass


@pytest.mark.skip(reason='TODO(retr0h): Determine best way to test this')
def test_display_tabluate_data():
    pass

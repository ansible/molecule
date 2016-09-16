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


def test_driver(molecule_default_provider_instance):
    assert isinstance(molecule_default_provider_instance.driver,
                      vagrantdriver.VagrantDriver)


def test_driver_setter(molecule_default_provider_instance):
    molecule_default_provider_instance.driver = 'foo'

    assert 'foo' == molecule_default_provider_instance.driver


def test_get_driver_name_from_cli(molecule_default_provider_instance):
    molecule_default_provider_instance.args.update({'driver': 'foo'})

    assert 'foo' == molecule_default_provider_instance._get_driver_name()


def test_get_driver_name_from_config(molecule_default_provider_instance):
    m = molecule_default_provider_instance
    m.config.config['driver'] = {'name': 'foo'}

    assert 'foo' == molecule_default_provider_instance._get_driver_name()


def test_get_driver_invalid_instance(molecule_default_provider_instance):
    del molecule_default_provider_instance.config.config['vagrant']

    with pytest.raises(basedriver.InvalidDriverSpecified):
        molecule_default_provider_instance._get_driver()


def test_verifier_setter(molecule_default_provider_instance):
    molecule_default_provider_instance.verifier = 'foo'

    assert 'foo' == molecule_default_provider_instance.verifier


def test_verifier(molecule_default_provider_instance):
    assert 'testinfra' == molecule_default_provider_instance.verifier


def test_verifier_backward_compatible(molecule_default_provider_instance):
    m = molecule_default_provider_instance
    m.config.config['testinfra'] = {}

    assert 'testinfra' == m.verifier


def test_verifier_options_setter(molecule_default_provider_instance):
    molecule_default_provider_instance.verifier_options = 'foo'

    assert 'foo' == molecule_default_provider_instance.verifier_options


def test_verifier_options(molecule_default_provider_instance):
    assert {} == molecule_default_provider_instance.verifier_options


def test_verifier_options_backward_compatible(
        molecule_default_provider_instance):
    m = molecule_default_provider_instance
    m.config.config['testinfra'] = {'foo': 'bar'}
    m.verifier_options = m._get_verifier_options()

    assert {'foo': 'bar'} == m.verifier_options


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

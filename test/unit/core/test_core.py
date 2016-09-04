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

import pytest

from molecule.driver import vagrantdriver


def test_driver(molecule_default_provider_instance):
    assert isinstance(molecule_default_provider_instance.driver,
                      vagrantdriver.VagrantDriver)


def test_driver_setter(molecule_default_provider_instance):
    molecule_default_provider_instance.driver = 'foo'

    assert 'foo' == molecule_default_provider_instance.driver


def test_get_driver_invalid_instance(molecule_default_provider_instance):
    del molecule_default_provider_instance.config.config['vagrant']

    assert molecule_default_provider_instance._get_driver() is None


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

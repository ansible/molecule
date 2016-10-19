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

from molecule.driver import openstackdriver


def test_get_driver_name(openstack_molecule_instance):
    assert 'openstack' == openstack_molecule_instance._get_driver_name()


def test_get_driver(openstack_molecule_instance):
    assert isinstance(openstack_molecule_instance._get_driver(),
                      openstackdriver.OpenstackDriver)


def test_get_ssh_config(openstack_molecule_instance):
    assert openstack_molecule_instance._get_ssh_config() is None


def test_write_ssh_config(mocker, openstack_molecule_instance):
    patched_write_file = mocker.patch('molecule.util.write_file')
    openstack_molecule_instance.write_ssh_config()

    assert not patched_write_file.called


def test_print_valid_platforms(capsys, openstack_molecule_instance):
    openstack_molecule_instance.print_valid_platforms()
    out, _ = capsys.readouterr()

    assert 'openstack  (default)\n' == out


def test_print_valid_platforms_with_porcelain(capsys,
                                              openstack_molecule_instance):
    openstack_molecule_instance.print_valid_platforms(porcelain=True)
    out, _ = capsys.readouterr()

    assert 'openstack  d\n' == out


def test_print_valid_providers(capsys, openstack_molecule_instance):
    openstack_molecule_instance.print_valid_providers()
    out, _ = capsys.readouterr()

    assert 'openstack  (default)\n' == out


def test_print_valid_providers_with_porcelain(capsys,
                                              openstack_molecule_instance):
    openstack_molecule_instance.print_valid_providers(porcelain=True)
    out, _ = capsys.readouterr()

    assert 'openstack  d\n' == out


def test_instances_state(openstack_molecule_instance):
    expected = {'aio-01-openstack': {'groups': ['example', 'example1']}}

    assert expected == openstack_molecule_instance._instances_state()

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

from molecule import config
from molecule import core
from molecule.driver import vagrantdriver


@pytest.fixture()
def molecule_instance(temp_files, molecule_args):
    c = temp_files(fixtures=['molecule_vagrant_config'])
    m = core.Molecule(molecule_args)
    m.config = config.Config(configs=c)
    m.main()

    return m


def test_get_driver(molecule_instance):
    assert isinstance(molecule_instance._get_driver(),
                      vagrantdriver.VagrantDriver)


def test_get_ssh_config(molecule_instance):
    assert '.vagrant/ssh-config' == molecule_instance._get_ssh_config()


def test_write_ssh_config(mocker, molecule_instance):
    mocked_out = mocker.patch(
        'molecule.driver.vagrantdriver.VagrantDriver.conf')
    mocked_out.return_value = 'mocked_out'
    mocked_write = mocker.patch('molecule.util.write_file')
    molecule_instance._write_ssh_config()

    mocked_write.assert_called_once_with('.vagrant/ssh-config', 'mocked_out')


def test_print_valid_platforms(capsys, molecule_instance):
    molecule_instance.print_valid_platforms()
    out, _ = capsys.readouterr()

    assert 'ubuntu  (default)\n' == out


def test_print_valid_platforms_with_porcelain(capsys, molecule_instance):
    molecule_instance.print_valid_platforms(porcelain=True)
    out, _ = capsys.readouterr()

    assert 'ubuntu  d\n' == out


def test_print_valid_providers(capsys, molecule_instance):
    molecule_instance._print_valid_providers()
    out, _ = capsys.readouterr()

    assert 'virtualbox  (default)\n' == out


def test_print_valid_providers_with_porcelain(capsys, molecule_instance):
    molecule_instance._print_valid_providers(porcelain=True)
    out, _ = capsys.readouterr()

    assert 'virtualbox  d\n' == out


def test_instances_state(molecule_instance):
    expected = {'aio-01-ubuntu': {'groups': ['example', 'example1']}}

    assert expected == molecule_instance._instances_state()

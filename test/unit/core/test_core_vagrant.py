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

from molecule.driver import vagrantdriver


def test_get_driver_name(vagrant_molecule_instance):
    assert 'vagrant' == vagrant_molecule_instance._get_driver_name()


def test_get_driver(vagrant_molecule_instance):
    assert isinstance(vagrant_molecule_instance._get_driver(),
                      vagrantdriver.VagrantDriver)


def test_get_ssh_config(vagrant_molecule_instance):
    assert '.vagrant/ssh-config' == vagrant_molecule_instance._get_ssh_config()


def test_write_ssh_config(mocker, vagrant_molecule_instance):
    patched_conf = mocker.patch(
        'molecule.driver.vagrantdriver.VagrantDriver.conf')
    patched_conf.return_value = 'patched'
    patched_write_file = mocker.patch('molecule.util.write_file')
    vagrant_molecule_instance.write_ssh_config()

    patched_write_file.assert_called_once_with('.vagrant/ssh-config',
                                               'patched')


def test_print_valid_platforms(capsys, vagrant_molecule_instance):
    vagrant_molecule_instance.print_valid_platforms()
    out, _ = capsys.readouterr()

    assert 'ubuntu   (default)' in out
    assert 'centos7' in out


def test_print_valid_platforms_with_porcelain(capsys,
                                              vagrant_molecule_instance):
    vagrant_molecule_instance.print_valid_platforms(porcelain=True)
    out, _ = capsys.readouterr()

    assert 'ubuntu   d' in out
    assert 'centos7' in out


def test_print_valid_providers(capsys, vagrant_molecule_instance):
    vagrant_molecule_instance.print_valid_providers()
    out, _ = capsys.readouterr()

    assert 'virtualbox  (default)\n' in out


def test_print_valid_providers_with_porcelain(capsys,
                                              vagrant_molecule_instance):
    vagrant_molecule_instance.print_valid_providers(porcelain=True)
    out, _ = capsys.readouterr()

    assert 'virtualbox  d\n' == out


def test_instances_state(vagrant_molecule_instance):
    expected = {
        'aio-01-ubuntu': {
            'groups': ['example', 'example1']
        },
        'aio-02-ubuntu': {
            'groups': ['example', 'example1']
        }
    }

    assert expected == vagrant_molecule_instance._instances_state()

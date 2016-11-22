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

from molecule.command import dependency


def test_execute(patched_ansible_galaxy, molecule_instance):
    molecule_instance.config.config['dependencies']['requirements_file'] = True

    d = dependency.Dependency({}, {}, molecule_instance)
    d.execute()

    patched_ansible_galaxy.assert_called_once()
    assert molecule_instance.state.installed_deps


def test_execute_does_not_install_when_installed(patched_ansible_galaxy,
                                                 molecule_instance):
    molecule_instance.config.config['dependencies']['requirements_file'] = True
    molecule_instance.state.change_state('installed_deps', True)

    d = dependency.Dependency({}, {}, molecule_instance)
    d.execute()

    assert not patched_ansible_galaxy.called


def test_execute_shell(patched_shell, molecule_instance):
    molecule_instance.dependencies = 'shell'
    molecule_instance.config.config['dependencies']['command'] = True

    d = dependency.Dependency({}, {}, molecule_instance)
    d.execute()

    patched_shell.assert_called_once()
    assert molecule_instance.state.installed_deps


def test_execute_shell_does_not_install_when_installed(patched_shell,
                                                       molecule_instance):
    molecule_instance.dependencies = 'shell'
    molecule_instance.config.config['dependencies']['command'] = True
    molecule_instance.state.change_state('installed_deps', True)

    d = dependency.Dependency({}, {}, molecule_instance)
    d.execute()

    assert not patched_shell.called

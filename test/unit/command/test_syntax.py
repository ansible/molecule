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

from molecule.command import syntax


def test_execute(mocker, patched_ansible_playbook, patched_print_info,
                 molecule_instance):
    patched_ansible_playbook.return_value = 'returned'

    s = syntax.Syntax({}, {}, molecule_instance)
    result = s.execute()

    msg = "Checking playbook's syntax ..."
    patched_print_info.assert_called_once_with(msg)
    patched_ansible_playbook.assert_called_once_with(hide_errors=True)
    assert 'returned' == result


def test_execute_installs_dependencies(patched_ansible_playbook,
                                       patched_dependency, patched_print_info,
                                       molecule_instance):
    molecule_instance.config.config['dependencies']['requirements_file'] = str(
    )

    s = syntax.Syntax({}, {}, molecule_instance)
    s.execute()

    patched_dependency.assert_called_once()
    patched_ansible_playbook.assert_called_once_with(hide_errors=True)

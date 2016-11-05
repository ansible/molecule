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
import sh

from molecule.verifier import ansible_lint


@pytest.fixture()
def ansible_lint_instance(molecule_instance):
    return ansible_lint.AnsibleLint(molecule_instance)


def test_execute(monkeypatch, patched_run_command, ansible_lint_instance):
    monkeypatch.setenv('HOME', '/foo/bar')
    ansible_lint_instance.execute()

    parts = pytest.helpers.os_split(ansible_lint_instance._playbook)
    assert 'playbook_data.yml' == parts[-1]

    x = sh.ansible_lint.bake(ansible_lint_instance._playbook, '--exclude .git',
                             '--exclude .vagrant', '--exclude .molecule')
    patched_run_command.assert_called_once_with(x, debug=None)

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

from molecule.verifier import ansible_lint


@pytest.fixture()
def ansible_lint_instance(molecule_instance):
    return ansible_lint.AnsibleLint(molecule_instance)


def test_execute(monkeypatch, mocker, ansible_lint_instance):
    monkeypatch.setenv('HOME', '/foo/bar')
    patched_ansible_lint = mocker.patch('sh.ansible_lint')
    ansible_lint_instance.execute()

    parts = pytest.helpers.os_split(ansible_lint_instance._playbook)
    assert 'playbook_data.yml' == parts[-1]

    patched_ansible_lint.assert_called_once_with(
        ansible_lint_instance._playbook,
        _env={'ANSIBLE_CONFIG': 'test/config_file',
              'HOME': '/foo/bar'},
        _out=ansible_lint.LOG.info,
        _err=ansible_lint.LOG.error)

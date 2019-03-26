#  Copyright (c) 2019 Red Hat, Inc.
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

from molecule import shell


@pytest.fixture
def _patched_get_ansible_version(mocker):
    target = 'molecule.shell._get_ansible_version'
    return mocker.patch(target)


@pytest.fixture
def _patched_supported_python_version(mocker):
    target = 'molecule.shell._supported_python_version'
    return mocker.patch(target)


def test_shell():
    with pytest.raises(SystemExit):
        shell.main()


@pytest.mark.parametrize('_version', ['2.5', '2.6', '2.7'])
def test_supported_ansible_does_not_raise(_version,
                                          _patched_get_ansible_version,
                                          _patched_supported_python_version):
    _patched_supported_python_version.return_value = True
    _patched_get_ansible_version.return_value = _version
    assert shell._supported_ansible_and_python_version() is None


@pytest.mark.parametrize('_version', ['2.2', '2.3', '2.4'])
def test_unsupported_ansible_does_raise(_version, _patched_get_ansible_version,
                                        _patched_supported_python_version):
    _patched_supported_python_version.return_value = True
    _patched_get_ansible_version.return_value = _version
    with pytest.raises(SystemExit):
        shell._supported_ansible_and_python_version()


def test_unsupported_python_does_raise(_patched_get_ansible_version,
                                       _patched_supported_python_version):
    _patched_get_ansible_version.return_value = '2.7'
    _patched_supported_python_version.return_value = False
    with pytest.raises(SystemExit):
        shell._supported_ansible_and_python_version()

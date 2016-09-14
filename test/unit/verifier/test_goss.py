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

from molecule.verifier import goss


@pytest.fixture()
def goss_instance(molecule_instance):
    return goss.Goss(molecule_instance)


@pytest.fixture
def patched_test_verifier(mocker):
    return mocker.patch('molecule.verifier.goss.Goss._goss')


@pytest.fixture
def patched_get_tests(mocker):
    return mocker.patch('molecule.verifier.goss.Goss._get_tests')


def test_execute(patched_test_verifier, patched_get_tests, goss_instance):
    patched_get_tests.return_value = True
    goss_instance.execute()

    patched_test_verifier.assert_called_once()


def test_execute_no_tests(patched_test_verifier, patched_get_tests,
                          goss_instance):
    patched_get_tests.return_value = False
    goss_instance.execute()

    assert not patched_test_verifier.called


def test_goss(patched_ansible_playbook, goss_instance):
    goss_instance._goss()

    patched_ansible_playbook.assert_called_once()


def test_get_tests(goss_instance):
    assert not goss_instance._get_tests()


def test_goss_path(goss_instance):
    path = goss_instance._get_library_path()
    parts = pytest.helpers.os_split(path)

    assert ('verifier', '..', '..', 'molecule', 'verifier', 'ansible',
            'library') == parts[-7:]

#  Copyright (c) 2015-2016 Cisco Systems
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

from molecule.verifier import testinfra


@pytest.fixture()
def testinfra_instance(molecule_instance):
    return testinfra.Testinfra(molecule_instance)


@pytest.fixture
def mocked_test_verifier(mocker):
    return mocker.patch('molecule.verifier.testinfra.Testinfra._testinfra')


@pytest.fixture
def mocked_get_tests(mocker):
    return mocker.patch('molecule.verifier.testinfra.Testinfra._get_tests')


def test_execute(mocked_test_verifier, mocked_get_tests, testinfra_instance):
    mocked_get_tests.return_value = ['/test/1', '/test/2']
    testinfra_instance.execute()

    assert (['/test/1', '/test/2'], ) == mocked_test_verifier.call_args[0]

    ca = mocked_test_verifier.call_args[1]
    assert not ca['debug']
    assert not ca['sudo']
    assert 'ansible' == ca['connection']
    assert 'test/inventory_file' == ca['ansible-inventory']
    assert 'env' in ca


def test_execute_no_tests(mocked_test_verifier, mocked_get_tests,
                          testinfra_instance):
    mocked_get_tests.return_value = []
    testinfra_instance.execute()

    assert not mocked_test_verifier.called


def test_testinfra(mocked_test_verifier, mocked_get_tests, testinfra_instance):
    args = ['/tmp/ansible-inventory']
    kwargs = {'debug': True, 'out': None, 'err': None}
    testinfra_instance._testinfra(*args, **kwargs)

    mocked_test_verifier.assert_called_once_with(*args, **kwargs)

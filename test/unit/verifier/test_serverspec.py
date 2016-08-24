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

from molecule.verifier import serverspec


@pytest.fixture()
def serverspec_instance(molecule_instance):
    return serverspec.Serverspec(molecule_instance)


@pytest.fixture
def mocked_code_verifier(mocker):
    return mocker.patch('molecule.verifier.serverspec.Serverspec._rubocop')


@pytest.fixture
def mocked_test_verifier(mocker):
    return mocker.patch('molecule.verifier.serverspec.Serverspec._rake')


@pytest.fixture
def mocked_get_tests(mocker):
    return mocker.patch('molecule.verifier.serverspec.Serverspec._get_tests')


def test_execute(mocked_code_verifier, mocked_test_verifier, mocked_get_tests,
                 serverspec_instance):
    mocked_get_tests.return_value = True
    serverspec_instance.execute()

    kwargs = {'debug': False}
    mocked_code_verifier.assert_called_once_with('spec', **kwargs)
    mocked_test_verifier.assert_called_once_with('test/rakefile_file',
                                                 **kwargs)


def test_execute_no_tests(mocked_code_verifier, mocked_test_verifier,
                          mocked_get_tests, serverspec_instance):
    mocked_get_tests.return_value = False
    serverspec_instance.execute()

    assert not mocked_code_verifier.called
    assert not mocked_test_verifier.called


def test_rake(mocker, serverspec_instance):
    mocked = mocker.patch('sh.rake')
    kwargs = {'debug': True, 'out': None, 'err': '/dev/null'}
    serverspec_instance._rake('/tmp/rakefile', **kwargs)

    ca = mocked.call_args[1]
    assert '/tmp/rakefile' == ca.get('rakefile')
    assert ca.get('trace')


def test_rubocop(mocker, serverspec_instance):
    mocked = mocker.patch('sh.rubocop')
    kwargs = {'pattern': '**/**/**/*',
              'debug': True,
              'out': '/dev/null',
              'err': None}
    serverspec_instance._rubocop('spec', **kwargs)

    assert ('spec**/**/**/*', ) == mocked.call_args[0]

    ca = mocked.call_args[1]
    assert ca.get('debug')


def test_get_tests(serverspec_instance):
    assert not serverspec_instance._get_tests()

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


def test_execute(mocker, serverspec_instance):
    mocked_test_stat = mocker.patch(
        'molecule.verifier.serverspec.Serverspec._get_tests')
    mocked_rake = mocker.patch('molecule.verifier.serverspec.Serverspec._rake')
    mocked_test_stat.return_value = True
    serverspec_instance.execute()

    args = ['test/rakefile_file']
    kwargs = {'debug': False}
    mocked_rake.assert_called_once_with(*args, **kwargs)


def test_execute_no_tests(mocker, serverspec_instance):
    mocked_test_stat = mocker.patch(
        'molecule.verifier.serverspec.Serverspec._get_tests')
    mocked_rake = mocker.patch('molecule.verifier.serverspec.Serverspec._rake')
    mocked_test_stat.return_value = False
    serverspec_instance.execute()

    assert not mocked_rake.called


def test_rake(mocker, serverspec_instance):
    mocked = mocker.patch('molecule.verifier.serverspec.Serverspec._rake')

    args = ['/tmp/rakefile']
    kwargs = {'debug': True, 'out': None, 'err': '/dev/null'}
    serverspec_instance._rake(*args, **kwargs)

    mocked.assert_called_once_with(*args, **kwargs)


def test_rubocop(mocker, serverspec_instance):
    mocked = mocker.patch('molecule.verifier.serverspec.Serverspec._rubocop')

    args = ['/tmp']
    kwargs = {'pattern': '**/**/**/*', 'out': '/dev/null', 'err': None}
    serverspec_instance._rubocop(*args, **kwargs)

    mocked.assert_called_once_with(*args, **kwargs)

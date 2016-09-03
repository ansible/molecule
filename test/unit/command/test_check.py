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

from molecule.command import check


@pytest.fixture
def mocked_main(mocker):
    return mocker.patch('molecule.command.check.Check.main')


def test_raises_when_instance_not_created(mocked_main, molecule_instance):
    c = check.Check([], dict(), molecule_instance)

    with pytest.raises(SystemExit) as e:
        c.execute()
        assert ('ERROR: Instance(s) not created, `check` '
                'should be run against created instance(s)') in e


def test_raises_when_instance_created_and_not_converged(mocked_main,
                                                        molecule_instance):
    molecule_instance.state.change_state('created', True)
    molecule_instance.state.change_state('converged', False)
    c = check.Check([], dict(), molecule_instance)

    with pytest.raises(SystemExit) as e:
        c.execute()
        assert ('ERROR: Instance(s) already converged, `check` '
                'should be run against unconverged instance(s)') in e


def test_execute(mocker, mocked_main, molecule_instance):
    molecule_instance.state.change_state('created', True)
    molecule_instance.state.change_state('converged', True)
    molecule_instance._driver = mocker.Mock(ansible_connection_params={})
    mocked = mocker.patch('molecule.ansible_playbook.AnsiblePlaybook.execute')

    c = check.Check([], dict(), molecule_instance)
    c.execute()

    assert mocked.called_once_with(hide_errors=True)

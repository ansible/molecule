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

import subprocess

from molecule.command import status


def test_execute(capsys, patched_main, molecule_instance):
    molecule_instance.args = {'--porcelain': False}

    s = status.Status({}, {}, molecule_instance)
    result = s.execute()

    out, err = capsys.readouterr()

    assert 'ubuntu  (default)' in out
    assert 'virtualbox  (default)' in out
    (None, None) == result


def test_execute_with_porcelain(capsys, patched_main, molecule_instance):
    command_args = {'porcelain': True}

    s = status.Status({}, command_args, molecule_instance)
    result = s.execute()

    out, err = capsys.readouterr()

    assert 'ubuntu  d' in out
    assert 'virtualbox  d' in out
    (None, None) == result


def test_exits_when_command_fails_and_exit_flag_set(
        patched_logger_error, mocker, patched_main, molecule_instance):
    command_args = {'porcelain': True}
    patched_status = mocker.patch(
        'molecule.driver.vagrantdriver.VagrantDriver.status')
    patched_status.side_effect = subprocess.CalledProcessError(1, None, None)

    s = status.Status({}, command_args, molecule_instance)
    result = s.execute()

    patched_logger_error.assert_called_once_with('')
    assert (1, '') == result

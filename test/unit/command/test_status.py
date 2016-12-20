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

import subprocess

from molecule.command import status


def test_execute(capsys, molecule_instance):
    s = status.Status({}, {}, molecule_instance)
    result = s.execute()

    out, _ = capsys.readouterr()
    decoded_out = out.encode('ascii', 'ignore').decode('ascii')

    assert 'ubuntu   (default)' in decoded_out
    assert 'centos7' in decoded_out
    assert 'virtualbox  (default)' in decoded_out
    (None, None) == result


def test_execute_with_porcelain(capsys, molecule_instance):
    command_args = {'porcelain': True}

    s = status.Status({}, command_args, molecule_instance)
    result = s.execute()

    out, _ = capsys.readouterr()

    assert 'ubuntu   d' in out
    assert 'centos7' in out
    assert 'virtualbox  d' in out
    (None, None) == result


def test_execute_exits_when_command_fails_and_exit_flag_set(
        patched_print_error, mocker, molecule_instance):
    command_args = {'porcelain': True}
    patched_status = mocker.patch(
        'molecule.driver.vagrantdriver.VagrantDriver.status')
    patched_status.side_effect = subprocess.CalledProcessError(1, None, None)

    s = status.Status({}, command_args, molecule_instance)
    result = s.execute()

    patched_print_error.assert_called_once_with(
        "Command 'None' returned non-zero exit status 1")
    assert (1, '', '') == result

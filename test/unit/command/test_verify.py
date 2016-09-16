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

from molecule.command import verify


def test_execute(mocker, patched_ansible_lint, patched_trailing,
                 patched_ssh_config, patched_main, molecule_instance):
    patched_testinfra = mocker.patch('molecule.verifier.testinfra.Testinfra')

    v = verify.Verify({}, {}, molecule_instance)
    result = v.execute()

    patched_ansible_lint.assert_called_once_with(molecule_instance)
    patched_trailing.assert_called_once_with(molecule_instance)
    patched_testinfra.assert_called_once_with(molecule_instance)
    patched_ssh_config.assert_called_once()
    assert (None, None) == result


def test_execute_with_serverspec(mocker, patched_ansible_lint,
                                 patched_trailing, patched_ssh_config,
                                 patched_main, molecule_instance):
    molecule_instance.verifier = 'serverspec'
    patched_serverspec = mocker.patch(
        'molecule.verifier.serverspec.Serverspec')

    v = verify.Verify({}, {}, molecule_instance)
    v.execute()

    patched_ansible_lint.assert_called_once_with(molecule_instance)
    patched_trailing.assert_called_once_with(molecule_instance)
    patched_serverspec.assert_called_once_with(molecule_instance)
    patched_ssh_config.assert_called_once()


def test_execute_with_goss(mocker, patched_ansible_lint, patched_trailing,
                           patched_ssh_config, patched_main,
                           molecule_instance):
    molecule_instance.verifier = 'goss'
    patched_goss = mocker.patch('molecule.verifier.goss.Goss')

    v = verify.Verify({}, {}, molecule_instance)
    v.execute()

    patched_ansible_lint.assert_called_once_with(molecule_instance)
    patched_trailing.assert_called_once_with(molecule_instance)
    patched_goss.assert_called_once_with(molecule_instance)
    patched_ssh_config.assert_called_once()


def test_execute_exits_when_command_fails_and_exit_flag_set(
        mocker, patched_main, patched_ansible_lint, patched_trailing,
        patched_ssh_config, patched_logger_error, molecule_instance):
    patched_testinfra = mocker.patch('molecule.verifier.testinfra.Testinfra')
    patched_testinfra.side_effect = sh.ErrorReturnCode_1(sh.ls, None, None)

    v = verify.Verify({}, {}, molecule_instance)
    with pytest.raises(SystemExit):
        v.execute()

    msg = ("ERROR: \n\n  RAN: <Command '/bin/ls'>\n\n  "
           "STDOUT:\n<redirected>\n\n  STDERR:\n<redirected>")
    patched_logger_error.assert_called_once_with(msg)


def test_execute_returns_when_command_fails_and_exit_flag_unset(
        mocker, patched_main, patched_ansible_lint, patched_trailing,
        patched_ssh_config, patched_logger_error, molecule_instance):
    patched_testinfra = mocker.patch('molecule.verifier.testinfra.Testinfra')
    patched_testinfra.side_effect = sh.ErrorReturnCode_1(sh.ls, None, None)

    v = verify.Verify({}, {}, molecule_instance)
    result = v.execute(exit=False)

    patched_logger_error.assert_called()
    assert (1, None) == result

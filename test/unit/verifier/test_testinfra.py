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

from molecule import config
from molecule.verifier import testinfra


@pytest.fixture
def testinfra_instance(config_instance):
    return testinfra.Testinfra(config_instance)


def test_config_private_member(testinfra_instance):
    assert isinstance(testinfra_instance._config, config.Config)


def test_options_property(testinfra_instance):
    assert {'connection': 'docker'} == testinfra_instance.options


def test_bake(testinfra_instance):
    testinfra_instance._tests = ['test1', 'test2', 'test3']
    testinfra_instance.bake()
    x = '{} --connection=docker test1 test2 test3'.format(str(sh.testinfra))

    assert x == testinfra_instance._testinfra_command


def test_execute(patched_flake8, patched_print_info, patched_run_command,
                 patched_testinfra_get_tests, testinfra_instance):
    testinfra_instance._testinfra_command = 'patched-command'
    testinfra_instance.execute()

    patched_run_command.assert_called_once_with('patched-command', debug=None)

    patched_flake8.assert_called_once

    msg = 'Executing testinfra tests found in {}/...'.format(
        testinfra_instance._config.verifier_directory)
    patched_print_info.assert_called_with(msg)


def test_execute_does_not_execute(patched_run_command, testinfra_instance):
    testinfra_instance._config.config['verifier']['enabled'] = False
    testinfra_instance.execute()

    assert not patched_run_command.called


def test_does_not_execute_without_tests(patched_run_command,
                                        testinfra_instance):
    testinfra_instance.execute()

    assert not patched_run_command.called


def test_execute_bakes(patched_flake8, patched_run_command,
                       patched_testinfra_get_tests, testinfra_instance):
    testinfra_instance.execute()

    assert testinfra_instance._testinfra_command is not None

    patched_flake8.assert_called_once

    cmd = '{} --connection=docker test1 test2 test3'.format(str(sh.testinfra))
    patched_run_command.assert_called_once_with(cmd, debug=None)


def test_executes_catches_and_exits_return_code(
        patched_run_command, patched_testinfra_get_tests, testinfra_instance):
    patched_run_command.side_effect = sh.ErrorReturnCode_1(sh.ansible_playbook,
                                                           None, None)
    with pytest.raises(SystemExit) as e:
        testinfra_instance.execute()

    assert 1 == e.value.code

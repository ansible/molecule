#  Copyright (c) 2015-2017 Cisco Systems, Inc.
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

import os

import pytest

from molecule.command.init import scenario


@pytest.fixture
def command_args():
    return {
        'driver_name': 'docker',
        'role_name': 'test-role',
        'scenario_name': 'test-scenario',
        'subcommand': __name__,
        'verifier_name': 'testinfra'
    }


@pytest.fixture
def scenario_instance(command_args):
    return scenario.Scenario(command_args)


def test_execute(temp_dir, scenario_instance, patched_logger_info,
                 patched_logger_success):
    scenario_instance.execute()

    msg = 'Initializing new scenario test-scenario...'
    patched_logger_info.assert_called_once_with(msg)

    assert os.path.isdir('./molecule/test-scenario')
    assert os.path.isdir('./molecule/test-scenario/tests')

    scenario_directory = os.path.join(temp_dir.strpath, 'molecule',
                                      'test-scenario')
    msg = 'Initialized scenario in {} successfully.'.format(scenario_directory)
    patched_logger_success.assert_called_once_with(msg)


def test_execute_scenario_exists(temp_dir, scenario_instance,
                                 patched_logger_critical):
    scenario_instance.execute()

    with pytest.raises(SystemExit) as e:
        scenario_instance.execute()

    assert 1 == e.value.code

    msg = ('The directory molecule/test-scenario exists. '
           'Cannot create new scenario.')
    patched_logger_critical.assert_called_once_with(msg)

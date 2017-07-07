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

from molecule.command.init import role


@pytest.fixture
def command_args():
    return {
        'dependency_name': 'galaxy',
        'driver_name': 'docker',
        'lint_name': 'ansible-lint',
        'provisioner_name': 'ansible',
        'role_name': 'test-role',
        'scenario_name': 'default',
        'subcommand': __name__,
        'verifier_name': 'testinfra'
    }


@pytest.fixture
def role_instance(command_args):
    return role.Role(command_args)


def test_execute(temp_dir, role_instance, patched_logger_info,
                 patched_logger_success):
    role_instance.execute()

    msg = 'Initializing new role test-role...'
    patched_logger_info.assert_called_once_with(msg)

    assert os.path.isdir('./test-role')
    assert os.path.isdir('./test-role/molecule/default')
    assert os.path.isdir('./test-role/molecule/default/tests')

    role_directory = os.path.join(temp_dir.strpath, 'test-role')
    msg = 'Initialized role in {} successfully.'.format(role_directory)
    patched_logger_success.assert_called_once_with(msg)


def test_execute_role_exists(temp_dir, role_instance, patched_logger_critical):
    role_instance.execute()

    with pytest.raises(SystemExit) as e:
        role_instance.execute()

    assert 1 == e.value.code

    msg = 'The directory test-role exists. Cannot create new role.'
    patched_logger_critical.assert_called_once_with(msg)

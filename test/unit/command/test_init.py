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
import uuid

import pytest

from molecule.command import init


def test_process_templates(temp_dir):
    template_dir = os.path.join(
        os.path.dirname(__file__), os.path.pardir, os.path.pardir, 'resources',
        'templates')
    repo_name = str(uuid.uuid4())
    context = {'repo_name': repo_name}
    init._process_templates(template_dir, context, temp_dir.strpath)

    expected_file = os.path.join(temp_dir.strpath, repo_name, 'template.yml')
    expected_contents = '- value: foo'

    with open(expected_file, 'r') as stream:
        for line in stream.readlines():
            assert line.strip() in expected_contents


def test_resolve_template_dir_relative():
    result = init._resolve_template_dir('foo')

    parts = pytest.helpers.os_split(result)

    assert ('..', 'cookiecutter', 'foo') == parts[-3:]


def test_resolve_template_dir_absolute():
    result = init._resolve_template_dir('/foo/bar')

    parts = pytest.helpers.os_split(result)

    assert ('foo', 'bar') == parts[-2:]


@pytest.fixture
def init_new_role_command_args():
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


def test_init_new_role(temp_dir, init_new_role_command_args,
                       patched_print_info, patched_print_success):
    init._init_new_role(init_new_role_command_args)

    msg = 'Initializing new role test-role...'
    patched_print_info.assert_called_once_with(msg)

    assert os.path.isdir('./test-role')
    assert os.path.isdir('./test-role/molecule/default')
    assert os.path.isdir('./test-role/molecule/default/tests')

    role_directory = os.path.join(temp_dir.strpath, 'test-role')
    msg = 'Successfully initialized role in {}.'.format(role_directory)
    patched_print_success.assert_called_once_with(msg)


def test_init_new_role_already_exists(temp_dir, init_new_role_command_args,
                                      patched_print_error):
    init._init_new_role(init_new_role_command_args)

    with pytest.raises(SystemExit) as e:
        init._init_new_role(init_new_role_command_args)

    assert 1 == e.value.code

    msg = 'The directory test-role exists. Cannot create new role.'
    patched_print_error.assert_called_once_with(msg)


@pytest.fixture
def init_new_scenario_command_args():
    return {
        'driver_name': 'docker',
        'role_name': 'test-role',
        'scenario_name': 'test-scenario',
        'subcommand': __name__,
        'verifier_name': 'testinfra'
    }


def test_init_new_scenario(temp_dir, init_new_scenario_command_args,
                           patched_print_info, patched_print_success):
    init._init_new_scenario(init_new_scenario_command_args)

    msg = 'Initializing new scenario test-scenario...'
    patched_print_info.assert_called_once_with(msg)

    assert os.path.isdir('./molecule/test-scenario')
    assert os.path.isdir('./molecule/test-scenario/tests')

    scenario_directory = os.path.join(temp_dir.strpath, 'molecule',
                                      'test-scenario')
    msg = 'Successfully initialized scenario in {}.'.format(scenario_directory)
    patched_print_success.assert_called_once_with(msg)


def test_init_new_scenario_already_exists(
        temp_dir, init_new_scenario_command_args, patched_print_error):
    init._init_new_scenario(init_new_scenario_command_args)

    with pytest.raises(SystemExit) as e:
        init._init_new_scenario(init_new_scenario_command_args)

    assert 1 == e.value.code

    msg = ('The directory molecule/test-scenario exists. '
           'Cannot create new scenario.')
    patched_print_error.assert_called_once_with(msg)

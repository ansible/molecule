#  Copyright (c) 2015-2018 Cisco Systems, Inc.
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
def _command_args():
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
def _instance(_command_args):
    return role.Role(_command_args)


@pytest.fixture
def _resources_folder_path():
    resources_folder_path = os.path.join(
        os.path.dirname(__file__), os.pardir, os.pardir, os.pardir,
        'resources')
    return resources_folder_path


@pytest.fixture
def custom_template_dir(_resources_folder_path):
    custom_template_dir_path = os.path.join(_resources_folder_path,
                                            'custom_role_template')
    return custom_template_dir_path


@pytest.fixture
def invalid_template_dir(_resources_folder_path):
    invalid_role_template_path = os.path.join(_resources_folder_path,
                                              'invalid_role_template')
    return invalid_role_template_path


@pytest.fixture
def custom_readme_content(custom_template_dir):
    readme_path = os.path.join(custom_template_dir,
                               '{{cookiecutter.role_name}}', 'README.md')

    custom_readme_content = ""
    with open(readme_path, 'r') as readme:
        custom_readme_content = readme.read()

    return custom_readme_content


def test_execute(temp_dir, _instance, patched_logger_info,
                 patched_logger_success):
    _instance.execute()

    msg = 'Initializing new role test-role...'
    patched_logger_info.assert_called_once_with(msg)

    assert os.path.isdir('./test-role')
    assert os.path.isdir('./test-role/molecule/default')
    assert os.path.isdir('./test-role/molecule/default/tests')

    role_directory = os.path.join(temp_dir.strpath, 'test-role')
    msg = 'Initialized role in {} successfully.'.format(role_directory)
    patched_logger_success.assert_called_once_with(msg)


def test_execute_role_exists(temp_dir, _instance, patched_logger_critical):
    _instance.execute()

    with pytest.raises(SystemExit) as e:
        _instance.execute()

    assert 1 == e.value.code

    msg = 'The directory test-role exists. Cannot create new role.'
    patched_logger_critical.assert_called_once_with(msg)


def test_execute_with_custom_template(temp_dir, custom_template_dir,
                                      custom_readme_content, _command_args):
    _command_args['template'] = custom_template_dir

    custom_template_instance = role.Role(_command_args)
    custom_template_instance.execute()

    readme_path = './test-role/README.md'
    assert os.path.isfile(readme_path)
    with open(readme_path, 'r') as readme:
        assert readme.read() == custom_readme_content

    assert os.path.isdir('./test-role/molecule/default')
    assert os.path.isdir('./test-role/molecule/default/tests')


def test_execute_with_absent_template(temp_dir, _command_args,
                                      patched_logger_critical):
    incorrect_path = os.path.join("absent_template_dir")
    _command_args['template'] = incorrect_path

    absent_template_instance = role.Role(_command_args)
    with pytest.raises(SystemExit) as e:
        absent_template_instance.execute()

    assert e.value.code == 1
    patched_logger_critical.assert_called_once()


def test_execute_with_incorrect_template(temp_dir, invalid_template_dir,
                                         _command_args,
                                         patched_logger_critical):
    _command_args['template'] = invalid_template_dir

    invalid_template_instance = role.Role(_command_args)
    with pytest.raises(SystemExit) as e:
        invalid_template_instance.execute()

    assert e.value.code == 1
    patched_logger_critical.assert_called_once()

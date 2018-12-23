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
def custom_readme_content():
    return "This string should be in the custom readme"


@pytest.fixture
def custom_template_dir(temp_dir, custom_readme_content):
    cookiecutter_json_path = os.path.join(
        os.path.dirname(
            __file__), os.path.pardir, os.path.pardir, os.path.pardir, os.path.pardir,
        'molecule', 'cookiecutter', 'role', 'cookiecutter.json')
    with open(cookiecutter_json_path, 'r') as cookiecutter_json:
        cookiecutter_json_content = cookiecutter_json.read()

    custom_role_template_dir = os.path.join(
        temp_dir, "custom_role_template")

    custom_cookiecutter_json_path = os.path.join(
        custom_role_template_dir, 'cookiecutter.json')
    custom_cookiecutter_dir_path = os.path.join(
        custom_role_template_dir, '{{cookiecutter.role_name}}')
    custom_cookiecutter_readme_path = os.path.join(
        custom_cookiecutter_dir_path, 'README.rst')

    os.makedirs(custom_role_template_dir)
    os.mknod(custom_cookiecutter_json_path)
    with open(custom_cookiecutter_json_path, 'a') as custom_cookiecutter_json:
        custom_cookiecutter_json.write(cookiecutter_json_content)

    os.makedirs(custom_cookiecutter_dir_path)
    os.mknod(custom_cookiecutter_readme_path)
    with open(custom_cookiecutter_readme_path, 'a') as custom_cookiecutter_readme:
        custom_cookiecutter_readme.write(custom_readme_content)

    return custom_role_template_dir


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


def test_execute_with_custom_template(custom_template_dir, custom_readme_content, _command_args, patched_logger_critical):
    _command_args['template'] = custom_template_dir

    custom_template_instance = role.Role(_command_args)
    custom_template_instance.execute()

    readme_path = './test-role/README.rst'
    assert os.path.isfile(readme_path)
    with open(readme_path, 'r') as readme:
        assert readme.read() == custom_readme_content
    
    assert os.path.isdir('./test-role/molecule/default')
    assert os.path.isdir('./test-role/molecule/default/tests')
    
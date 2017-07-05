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
import sh

from molecule import config
from molecule.dependency import ansible_galaxy


@pytest.fixture
def molecule_dependency_section_data():
    return {
        'dependency': {
            'name': 'galaxy',
            'options': {
                'foo': 'bar',
                'vvv': True,
            },
            'env': {
                'foo': 'bar',
            }
        }
    }


@pytest.fixture
def ansible_galaxy_instance(molecule_dependency_section_data, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_dependency_section_data)

    return ansible_galaxy.AnsibleGalaxy(config_instance)


@pytest.fixture
def role_file(ansible_galaxy_instance):
    return os.path.join(ansible_galaxy_instance._config.scenario.directory,
                        'requirements.yml')


@pytest.fixture
def roles_path(ansible_galaxy_instance):
    return os.path.join(
        ansible_galaxy_instance._config.scenario.ephemeral_directory, 'roles')


def test_config_private_member(ansible_galaxy_instance):
    assert isinstance(ansible_galaxy_instance._config, config.Config)


def test_default_options_property(ansible_galaxy_instance, role_file,
                                  roles_path):
    x = {'role-file': role_file, 'roles-path': roles_path, 'force': True}

    assert x == ansible_galaxy_instance.default_options


def test_default_env_property(ansible_galaxy_instance):
    assert 'MOLECULE_FILE' in ansible_galaxy_instance.default_env
    assert 'MOLECULE_INVENTORY_FILE' in ansible_galaxy_instance.default_env
    assert 'MOLECULE_SCENARIO_DIRECTORY' in ansible_galaxy_instance.default_env
    assert 'MOLECULE_INSTANCE_CONFIG' in ansible_galaxy_instance.default_env


def test_name_property(ansible_galaxy_instance):
    assert 'galaxy' == ansible_galaxy_instance.name


def test_enabled_property(ansible_galaxy_instance):
    assert ansible_galaxy_instance.enabled


def test_options_property(ansible_galaxy_instance, role_file, roles_path):
    x = {
        'force': True,
        'role-file': role_file,
        'roles-path': roles_path,
        'foo': 'bar',
        'vvv': True,
    }

    assert x == ansible_galaxy_instance.options


def test_options_property_handles_cli_args(role_file, roles_path,
                                           ansible_galaxy_instance):
    ansible_galaxy_instance._config.args = {'debug': True}
    x = {
        'force': True,
        'role-file': role_file,
        'roles-path': roles_path,
        'foo': 'bar',
        'vvv': True,
    }

    assert x == ansible_galaxy_instance.options


def test_env_property(ansible_galaxy_instance):
    assert 'bar' == ansible_galaxy_instance.env['foo']


def test_bake(ansible_galaxy_instance, role_file, roles_path):
    ansible_galaxy_instance.bake()
    x = [
        str(sh.ansible_galaxy), 'install', '--role-file={}'.format(role_file),
        '--roles-path={}'.format(roles_path), '--force', '--foo=bar', '-vvv'
    ]
    result = str(ansible_galaxy_instance._ansible_galaxy_command).split()

    assert sorted(x) == sorted(result)


def test_execute(patched_run_command,
                 patched_ansible_galaxy_has_requirements_file,
                 patched_logger_success, ansible_galaxy_instance):
    ansible_galaxy_instance._ansible_galaxy_command = 'patched-command'
    ansible_galaxy_instance.execute()

    role_directory = os.path.join(
        ansible_galaxy_instance._config.scenario.directory,
        ansible_galaxy_instance.options['roles-path'])
    assert os.path.isdir(role_directory)

    patched_run_command.assert_called_once_with('patched-command', debug=False)

    msg = 'Dependency completed successfully.'
    patched_logger_success.assert_called_once_with(msg)


def test_execute_does_not_execute_when_disabled(
        patched_run_command, patched_logger_warn, ansible_galaxy_instance):
    ansible_galaxy_instance._config.config['dependency']['enabled'] = False
    ansible_galaxy_instance.execute()

    assert not patched_run_command.called

    msg = 'Skipping, dependency is disabled.'
    patched_logger_warn.assert_called_once_with(msg)


def test_execute_does_not_execute_when_no_requirements_file(
        patched_run_command, patched_ansible_galaxy_has_requirements_file,
        patched_logger_warn, ansible_galaxy_instance):
    patched_ansible_galaxy_has_requirements_file.return_value = False
    ansible_galaxy_instance.execute()

    assert not patched_run_command.called

    msg = 'Skipping, missing the requirements file.'
    patched_logger_warn.assert_called_once_with(msg)


def test_execute_bakes(patched_run_command, ansible_galaxy_instance, role_file,
                       patched_ansible_galaxy_has_requirements_file,
                       roles_path):
    ansible_galaxy_instance.execute()
    assert ansible_galaxy_instance._ansible_galaxy_command is not None

    assert 1 == patched_run_command.call_count


def test_executes_catches_and_exits_return_code(
        patched_run_command, patched_ansible_galaxy_has_requirements_file,
        ansible_galaxy_instance):
    patched_run_command.side_effect = sh.ErrorReturnCode_1(
        sh.ansible_galaxy, b'', b'')
    with pytest.raises(SystemExit) as e:
        ansible_galaxy_instance.execute()

    assert 1 == e.value.code


def test_setup(ansible_galaxy_instance):
    role_directory = os.path.join(
        ansible_galaxy_instance._config.scenario.directory,
        ansible_galaxy_instance.options['roles-path'])
    assert not os.path.isdir(role_directory)

    ansible_galaxy_instance._setup()

    assert os.path.isdir(role_directory)


def test_has_requirements_file(ansible_galaxy_instance):
    assert not ansible_galaxy_instance._has_requirements_file()

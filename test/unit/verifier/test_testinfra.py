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
from molecule import util
from molecule.verifier import testinfra
from molecule.verifier.lint import flake8


@pytest.fixture
def _patched_testinfra_get_tests(mocker):
    m = mocker.patch('molecule.verifier.testinfra.Testinfra._get_tests')
    m.return_value = [
        'foo.py',
        'bar.py',
    ]

    return m


@pytest.fixture
def _verifier_section_data():
    return {
        'verifier': {
            'name':
            'testinfra',
            'options': {
                'foo': 'bar',
                'v': True,
                'verbose': True,
            },
            'additional_files_or_dirs': [
                'file1.py',
                'file2.py',
                'match*.py',
                'dir/*',
            ],
            'env': {
                'FOO': 'bar',
            },
            'lint': {
                'name': 'flake8',
            },
        }
    }


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.fixture
def _instance(patched_config_validate, config_instance):
    return testinfra.Testinfra(config_instance)


@pytest.fixture
def inventory_file(_instance):
    return _instance._config.provisioner.inventory_file


def test_config_private_member(_instance):
    assert isinstance(_instance._config, config.Config)


def test_default_options_property(inventory_file, _instance):
    x = {'connection': 'ansible', 'ansible-inventory': inventory_file}

    assert x == _instance.default_options


def test_default_options_property_updates_debug(inventory_file, _instance):
    _instance._config.args = {'debug': True}
    x = {
        'connection': 'ansible',
        'ansible-inventory': inventory_file,
        'debug': True,
        'vvv': True,
    }

    assert x == _instance.default_options


def test_default_options_property_updates_sudo(inventory_file, _instance,
                                               _patched_testinfra_get_tests):
    _instance._config.args = {'sudo': True}
    x = {
        'connection': 'ansible',
        'ansible-inventory': inventory_file,
        'sudo': True
    }

    assert x == _instance.default_options


def test_default_env_property(_instance):
    assert 'MOLECULE_FILE' in _instance.default_env
    assert 'MOLECULE_INVENTORY_FILE' in _instance.default_env
    assert 'MOLECULE_SCENARIO_DIRECTORY' in _instance.default_env
    assert 'MOLECULE_INSTANCE_CONFIG' in _instance.default_env


@pytest.mark.parametrize(
    'config_instance', ['_verifier_section_data'], indirect=True)
def test_additional_files_or_dirs_property(_instance):
    tests_directory = _instance._config.verifier.directory
    file1_file = os.path.join(tests_directory, 'file1.py')
    file2_file = os.path.join(tests_directory, 'file2.py')
    match1_file = os.path.join(tests_directory, 'match1.py')
    match2_file = os.path.join(tests_directory, 'match2.py')
    test_subdir = os.path.join(tests_directory, 'dir')
    test_subdir_file = os.path.join(test_subdir, 'test_subdir_file.py')

    os.mkdir(tests_directory)
    os.mkdir(test_subdir)
    for f in [
            file1_file,
            file2_file,
            match1_file,
            match2_file,
            test_subdir_file,
    ]:
        util.write_file(f, '')

    x = [
        file1_file,
        file2_file,
        match1_file,
        match2_file,
        test_subdir_file,
    ]
    assert sorted(x) == sorted(_instance.additional_files_or_dirs)


@pytest.mark.parametrize(
    'config_instance', ['_verifier_section_data'], indirect=True)
def test_env_property(_instance):
    assert 'bar' == _instance.env['FOO']
    assert 'ANSIBLE_CONFIG' in _instance.env
    assert 'ANSIBLE_ROLES_PATH' in _instance.env
    assert 'ANSIBLE_LIBRARY' in _instance.env
    assert 'ANSIBLE_FILTER_PLUGINS' in _instance.env


def test_lint_property(_instance):
    assert isinstance(_instance.lint, flake8.Flake8)


def test_name_property(_instance):
    assert 'testinfra' == _instance.name


def test_enabled_property(_instance):
    assert _instance.enabled


def test_directory_property(_instance):
    parts = _instance.directory.split(os.path.sep)

    assert ['molecule', 'default', 'tests'] == parts[-3:]


@pytest.fixture
def _verifier_testinfra_directory_section_data():
    return {
        'verifier': {
            'name': 'testinfra',
            'directory': '/tmp/foo/bar'
        },
    }


@pytest.mark.parametrize(
    'config_instance', ['_verifier_testinfra_directory_section_data'],
    indirect=True)
def test_directory_property_overriden(_instance):
    assert '/tmp/foo/bar' == _instance.directory


@pytest.mark.parametrize(
    'config_instance', ['_verifier_section_data'], indirect=True)
def test_options_property(inventory_file, _instance):
    x = {
        'connection': 'ansible',
        'ansible-inventory': inventory_file,
        'foo': 'bar',
        'v': True,
        'verbose': True,
    }

    assert x == _instance.options


@pytest.mark.parametrize(
    'config_instance', ['_verifier_section_data'], indirect=True)
def test_options_property_handles_cli_args(inventory_file, _instance):
    _instance._config.args = {'debug': True}
    x = {
        'connection': 'ansible',
        'ansible-inventory': inventory_file,
        'foo': 'bar',
        'debug': True,
        'vvv': True,
        'verbose': True,
    }

    assert x == _instance.options


@pytest.mark.parametrize(
    'config_instance', ['_verifier_section_data'], indirect=True)
def test_bake(_patched_testinfra_get_tests, inventory_file, _instance):
    tests_directory = _instance._config.verifier.directory
    file1_file = os.path.join(tests_directory, 'file1.py')

    os.mkdir(tests_directory)
    util.write_file(file1_file, '')

    _instance.bake()
    x = [
        str(sh.Command('py.test')),
        '--ansible-inventory={}'.format(inventory_file),
        '--connection=ansible',
        '-v',
        '--foo=bar',
        'foo.py',
        'bar.py',
        file1_file,
    ]
    result = str(_instance._testinfra_command).split()

    assert sorted(x) == sorted(result)


def test_execute(patched_logger_info, patched_run_command,
                 _patched_testinfra_get_tests, patched_logger_success,
                 _instance):
    _instance._testinfra_command = 'patched-command'
    _instance.execute()

    patched_run_command.assert_called_once_with('patched-command', debug=False)

    msg = 'Executing Testinfra tests found in {}/...'.format(
        _instance.directory)
    patched_logger_info.assert_called_once_with(msg)

    msg = 'Verifier completed successfully.'
    patched_logger_success.assert_called_once_with(msg)


def test_execute_does_not_execute(patched_run_command, patched_logger_warn,
                                  _instance):
    _instance._config.config['verifier']['enabled'] = False
    _instance.execute()

    assert not patched_run_command.called

    msg = 'Skipping, verifier is disabled.'
    patched_logger_warn.assert_called_once_with(msg)


def test_does_not_execute_without_tests(patched_run_command,
                                        patched_logger_warn, _instance):
    _instance.execute()

    assert not patched_run_command.called

    msg = 'Skipping, no tests found.'
    patched_logger_warn.assert_called_once_with(msg)


def test_execute_bakes(patched_run_command, _patched_testinfra_get_tests,
                       _instance):
    _instance.execute()

    assert _instance._testinfra_command is not None

    assert 1 == patched_run_command.call_count


def test_executes_catches_and_exits_return_code(
        patched_run_command, _patched_testinfra_get_tests, _instance):
    patched_run_command.side_effect = sh.ErrorReturnCode_1(
        sh.testinfra, b'', b'')
    with pytest.raises(SystemExit) as e:
        _instance.execute()

    assert 1 == e.value.code

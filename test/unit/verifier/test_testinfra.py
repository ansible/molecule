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
def molecule_verifier_section_data():
    return {
        'verifier': {
            'name':
            'testinfra',
            'options': {
                'foo': 'bar',
                'vvv': True,
                'verbose': True,
            },
            'additional_files_or_dirs': [
                'file1.py',
                'file2.py',
                'match*.py',
                'dir/*',
            ],
            'env': {
                'foo': 'bar',
            },
            'lint': {
                'name': 'flake8',
            },
        }
    }


@pytest.fixture
def testinfra_instance(molecule_verifier_section_data, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_verifier_section_data)

    return testinfra.Testinfra(config_instance)


@pytest.fixture
def inventory_file(testinfra_instance):
    return testinfra_instance._config.provisioner.inventory_file


def test_config_private_member(testinfra_instance):
    assert isinstance(testinfra_instance._config, config.Config)


def test_default_options_property(inventory_file, testinfra_instance):
    x = {'connection': 'ansible', 'ansible-inventory': inventory_file}

    assert x == testinfra_instance.default_options


def test_default_options_property_updates_debug(inventory_file,
                                                testinfra_instance):
    testinfra_instance._config.args = {'debug': True}
    x = {
        'connection': 'ansible',
        'ansible-inventory': inventory_file,
        'debug': True
    }

    assert x == testinfra_instance.default_options


def test_default_options_property_updates_sudo(
        inventory_file, testinfra_instance, patched_testinfra_get_tests):
    testinfra_instance._config.args = {'sudo': True}
    x = {
        'connection': 'ansible',
        'ansible-inventory': inventory_file,
        'sudo': True
    }

    assert x == testinfra_instance.default_options


def test_default_env_property(testinfra_instance):
    assert 'MOLECULE_FILE' in testinfra_instance.default_env
    assert 'MOLECULE_INVENTORY_FILE' in testinfra_instance.default_env
    assert 'MOLECULE_SCENARIO_DIRECTORY' in testinfra_instance.default_env
    assert 'MOLECULE_INSTANCE_CONFIG' in testinfra_instance.default_env


def test_additional_files_or_dirs_property(testinfra_instance):
    tests_directory = testinfra_instance._config.verifier.directory
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
    assert sorted(x) == sorted(testinfra_instance.additional_files_or_dirs)


def test_env_property(testinfra_instance):
    assert 'bar' == testinfra_instance.env['foo']
    assert 'ANSIBLE_CONFIG' in testinfra_instance.env
    assert 'ANSIBLE_ROLES_PATH' in testinfra_instance.env
    assert 'ANSIBLE_LIBRARY' in testinfra_instance.env
    assert 'ANSIBLE_FILTER_PLUGINS' in testinfra_instance.env


def test_lint_property(testinfra_instance):
    assert isinstance(testinfra_instance.lint, flake8.Flake8)


@pytest.fixture
def molecule_verifier_lint_invalid_section_data():
    return {
        'verifier': {
            'name': 'testinfra',
            'lint': {
                'name': 'invalid',
            },
        }
    }


def test_lint_property_raises(molecule_verifier_lint_invalid_section_data,
                              patched_logger_critical, testinfra_instance):
    testinfra_instance._config.merge_dicts(
        testinfra_instance._config.config,
        molecule_verifier_lint_invalid_section_data)
    with pytest.raises(SystemExit) as e:
        testinfra_instance.lint

    assert 1 == e.value.code

    msg = "Invalid lint named 'invalid' configured."
    patched_logger_critical.assert_called_once_with(msg)


def test_name_property(testinfra_instance):
    assert 'testinfra' == testinfra_instance.name


def test_enabled_property(testinfra_instance):
    assert testinfra_instance.enabled


def test_directory_property(testinfra_instance):
    parts = testinfra_instance.directory.split(os.path.sep)

    assert ['molecule', 'default', 'tests'] == parts[-3:]


@pytest.fixture
def molecule_verifier_directory_section_data():
    return {
        'verifier': {
            'name': 'testinfra',
            'directory': '/tmp/foo/bar'
        },
    }


def test_directory_property_overriden(
        testinfra_instance, molecule_verifier_directory_section_data):
    testinfra_instance._config.merge_dicts(
        testinfra_instance._config.config,
        molecule_verifier_directory_section_data)

    assert '/tmp/foo/bar' == testinfra_instance.directory


def test_options_property(inventory_file, testinfra_instance):
    x = {
        'connection': 'ansible',
        'ansible-inventory': inventory_file,
        'foo': 'bar',
        'vvv': True,
        'verbose': True,
    }

    assert x == testinfra_instance.options


def test_options_property_handles_cli_args(inventory_file, testinfra_instance):
    testinfra_instance._config.args = {'debug': True}
    x = {
        'connection': 'ansible',
        'ansible-inventory': inventory_file,
        'foo': 'bar',
        'debug': True,
        'vvv': True,
        'verbose': True,
    }

    assert x == testinfra_instance.options


def test_bake(patched_testinfra_get_tests, inventory_file, testinfra_instance):
    tests_directory = testinfra_instance._config.verifier.directory
    file1_file = os.path.join(tests_directory, 'file1.py')

    os.mkdir(tests_directory)
    util.write_file(file1_file, '')

    testinfra_instance.bake()
    x = [
        str(sh.Command('py.test')),
        '--ansible-inventory={}'.format(inventory_file),
        '--connection=ansible',
        '-vvv',
        '--foo=bar',
        'foo.py',
        'bar.py',
        file1_file,
    ]
    result = str(testinfra_instance._testinfra_command).split()

    assert sorted(x) == sorted(result)


def test_execute(patched_logger_info, patched_run_command,
                 patched_testinfra_get_tests, patched_logger_success,
                 testinfra_instance):
    testinfra_instance._testinfra_command = 'patched-command'
    testinfra_instance.execute()

    patched_run_command.assert_called_once_with('patched-command', debug=False)

    msg = 'Executing Testinfra tests found in {}/...'.format(
        testinfra_instance.directory)
    patched_logger_info.assert_called_once_with(msg)

    msg = 'Verifier completed successfully.'
    patched_logger_success.assert_called_once_with(msg)


def test_execute_does_not_execute(patched_run_command, patched_logger_warn,
                                  testinfra_instance):
    testinfra_instance._config.config['verifier']['enabled'] = False
    testinfra_instance.execute()

    assert not patched_run_command.called

    msg = 'Skipping, verifier is disabled.'
    patched_logger_warn.assert_called_once_with(msg)


def test_does_not_execute_without_tests(
        patched_run_command, patched_logger_warn, testinfra_instance):
    testinfra_instance.execute()

    assert not patched_run_command.called

    msg = 'Skipping, no tests found.'
    patched_logger_warn.assert_called_once_with(msg)


def test_execute_bakes(patched_run_command, patched_testinfra_get_tests,
                       testinfra_instance):
    testinfra_instance.execute()

    assert testinfra_instance._testinfra_command is not None

    assert 1 == patched_run_command.call_count


def test_executes_catches_and_exits_return_code(
        patched_run_command, patched_testinfra_get_tests, testinfra_instance):
    patched_run_command.side_effect = sh.ErrorReturnCode_1(
        sh.testinfra, b'', b'')
    with pytest.raises(SystemExit) as e:
        testinfra_instance.execute()

    assert 1 == e.value.code

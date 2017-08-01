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

import pytest
import sh

from molecule import config
from molecule.verifier.lint import flake8


@pytest.fixture
def molecule_verifier_lint_section_data():
    return {
        'verifier': {
            'name': 'testinfra',
            'lint': {
                'name': 'flake8',
                'options': {
                    'foo': 'bar',
                },
                'env': {
                    'foo': 'bar',
                },
            }
        }
    }


@pytest.fixture
def flake8_instance(molecule_verifier_lint_section_data, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_verifier_lint_section_data)

    return flake8.Flake8(config_instance)


def test_config_private_member(flake8_instance):
    assert isinstance(flake8_instance._config, config.Config)


def test_default_options_property(flake8_instance):
    assert {} == flake8_instance.default_options


def test_default_env_property(flake8_instance):
    assert 'MOLECULE_FILE' in flake8_instance.default_env
    assert 'MOLECULE_INVENTORY_FILE' in flake8_instance.default_env
    assert 'MOLECULE_SCENARIO_DIRECTORY' in flake8_instance.default_env
    assert 'MOLECULE_INSTANCE_CONFIG' in flake8_instance.default_env


def test_name_property(flake8_instance):
    assert 'flake8' == flake8_instance.name


def test_enabled_property(flake8_instance):
    assert flake8_instance.enabled


def test_options_property(flake8_instance):
    x = {
        'foo': 'bar',
    }

    assert x == flake8_instance.options


def test_options_property_handles_cli_args(flake8_instance):
    flake8_instance._config.args = {'debug': True}
    x = {
        'foo': 'bar',
    }

    # Does nothing.  The `flake8` command does not support
    # a `debug` flag.
    assert x == flake8_instance.options


def test_bake(flake8_instance):
    flake8_instance._tests = ['test1', 'test2', 'test3']
    flake8_instance.bake()
    x = '{} --foo=bar test1 test2 test3'.format(str(sh.flake8))

    assert x == flake8_instance._flake8_command


def test_execute(patched_logger_info, patched_logger_success,
                 patched_run_command, flake8_instance):
    flake8_instance._tests = ['test1', 'test2', 'test3']
    flake8_instance._flake8_command = 'patched-command'
    flake8_instance.execute()

    patched_run_command.assert_called_once_with('patched-command', debug=False)

    msg = 'Executing Flake8 on files found in {}/...'.format(
        flake8_instance._config.verifier.directory)
    patched_logger_info.assert_called_once_with(msg)

    msg = 'Lint completed successfully.'
    patched_logger_success.assert_called_once_with(msg)


def test_execute_does_not_execute(patched_run_command, patched_logger_warn,
                                  flake8_instance):
    flake8_instance._config.config['verifier']['lint']['enabled'] = False
    flake8_instance.execute()

    assert not patched_run_command.called

    msg = 'Skipping, verifier_lint is disabled.'
    patched_logger_warn.assert_called_once_with(msg)


def test_does_not_execute_without_tests(patched_run_command,
                                        patched_logger_warn, flake8_instance):
    flake8_instance.execute()

    assert not patched_run_command.called

    msg = 'Skipping, no tests found.'
    patched_logger_warn.assert_called_once_with(msg)


def test_execute_bakes(patched_run_command, flake8_instance):
    flake8_instance._tests = ['test1', 'test2', 'test3']
    flake8_instance.execute()

    assert flake8_instance._flake8_command is not None

    cmd = '{} --foo=bar test1 test2 test3'.format(str(sh.flake8))
    patched_run_command.assert_called_once_with(cmd, debug=False)


def test_executes_catches_and_exits_return_code(
        patched_run_command, patched_get_tests, flake8_instance):
    patched_run_command.side_effect = sh.ErrorReturnCode_1(sh.flake8, b'', b'')
    with pytest.raises(SystemExit) as e:
        flake8_instance.execute()

    assert 1 == e.value.code

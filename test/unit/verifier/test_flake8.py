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
from molecule.verifier import flake8


@pytest.fixture
def flake8_instance(molecule_verifier_section_data, config_instance):
    config_instance.config.update(molecule_verifier_section_data)

    return flake8.Flake8(config_instance)


def test_config_private_member(flake8_instance):
    assert isinstance(flake8_instance._config, config.Config)


def test_default_options_property(flake8_instance):
    assert {} == flake8_instance.default_options


def test_name_property(flake8_instance):
    assert 'testinfra' == flake8_instance.name


def test_enabled_property(flake8_instance):
    assert flake8_instance.enabled


def test_directory_property(flake8_instance):
    parts = flake8_instance.directory.split(os.path.sep)
    assert 'tests' == parts[-1]


def test_options_property(flake8_instance):
    assert {'foo': 'bar'} == flake8_instance.options


def test_options_property_handles_cli_args(flake8_instance):
    flake8_instance._config.args = {'debug': True}
    x = {'foo': 'bar'}

    # Does nothing.  The `flake8` command does not support
    # a `debug` flag.
    assert x == flake8_instance.options


def test_bake(flake8_instance):
    flake8_instance._tests = ['test1', 'test2', 'test3']
    flake8_instance.bake()
    x = '{} test1 test2 test3'.format(str(sh.flake8))

    assert x == flake8_instance._flake8_command


def test_execute(patched_print_info, patched_run_command,
                 patched_testinfra_get_tests, flake8_instance):
    flake8_instance._tests = ['test1', 'test2', 'test3']
    flake8_instance._flake8_command = 'patched-command'
    flake8_instance.execute()

    patched_run_command.assert_called_once_with('patched-command', debug=None)

    msg = 'Executing flake8 on files found in {}/...'.format(
        flake8_instance.directory)
    patched_print_info.assert_called_once_with(msg)


def test_execute_bakes(patched_run_command, flake8_instance):
    flake8_instance._tests = ['test1', 'test2', 'test3']
    flake8_instance.execute()

    assert flake8_instance._flake8_command is not None

    cmd = '{} test1 test2 test3'.format(str(sh.flake8))
    patched_run_command.assert_called_once_with(cmd, debug=None)


def test_executes_catches_and_exits_return_code(patched_run_command,
                                                flake8_instance):
    patched_run_command.side_effect = sh.ErrorReturnCode_1(sh.flake8, b'', b'')
    with pytest.raises(SystemExit) as e:
        flake8_instance.execute()

    assert 1 == e.value.code

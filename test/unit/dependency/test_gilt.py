#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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
from molecule.dependency import gilt


@pytest.fixture
def dependency_data():
    return {'dependency': {'name': 'gilt', 'options': {'foo': 'bar'}}}


@pytest.fixture
def gilt_instance(molecule_file, dependency_data):
    c = config.Config(molecule_file, configs=[dependency_data])

    return gilt.Gilt(c)


@pytest.fixture
def gilt_config(gilt_instance):
    return os.path.join(gilt_instance._config.scenario.directory, 'gilt.yml')


def test_config_private_member(gilt_instance):
    assert isinstance(gilt_instance._config, config.Config)


def test_default_options_property(gilt_config, gilt_instance):
    x = {'config': gilt_config}

    assert x == gilt_instance.default_options


def test_name_property(gilt_instance):
    assert 'gilt' == gilt_instance.name


def test_enabled_property(gilt_instance):
    assert gilt_instance.enabled


def test_options_property(gilt_config, gilt_instance):
    x = {'config': gilt_config, 'foo': 'bar'}

    assert x == gilt_instance.options


def test_options_property_handles_cli_args(molecule_file, gilt_config,
                                           dependency_data):
    c = config.Config(
        molecule_file, args={'debug': True}, configs=[dependency_data])
    d = gilt.Gilt(c)
    x = {'config': gilt_config, 'foo': 'bar', 'debug': True}

    assert x == d.options


@pytest.mark.skip(reason="baked command does not always return arguments in"
                  "the same order")
def test_bake(gilt_config, gilt_instance):
    gilt_instance.bake()
    x = '{} --foo=bar --config={} overlay'.format(str(sh.gilt), gilt_config)

    assert x == gilt_instance._gilt_command


def test_execute(patched_run_command, gilt_instance):
    gilt_instance._gilt_command = 'patched-command'
    gilt_instance.execute()

    patched_run_command.assert_called_once_with('patched-command', debug=None)


def test_execute_does_not_execute(patched_run_command, gilt_instance):
    gilt_instance._config.config['dependency']['enabled'] = False
    gilt_instance.execute()

    assert not patched_run_command.called


@pytest.mark.skip(reason="baked command does not always return arguments in"
                  "the same order")
def test_execute_bakes(patched_run_command, gilt_config, gilt_instance):
    gilt_instance.execute()
    assert gilt_instance._gilt_command is not None

    cmd = '{} --foo=bar --config={} overlay'.format(str(sh.gilt), gilt_config)

    patched_run_command.assert_called_with(cmd, debug=None)


def test_executes_catches_and_exits_return_code(patched_run_command,
                                                gilt_instance):
    patched_run_command.side_effect = sh.ErrorReturnCode_1(sh.ansible_galaxy,
                                                           None, None)
    with pytest.raises(SystemExit) as e:
        gilt_instance.execute()

    assert 1 == e.value.code

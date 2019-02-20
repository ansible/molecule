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
import shutil
import tempfile

import pytest

from molecule import config
from molecule import scenario


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.fixture
def _instance(patched_config_validate, config_instance):
    return scenario.Scenario(config_instance)


def test_config_member(_instance):
    assert isinstance(_instance.config, config.Config)


def test_init_calls_setup(patched_scenario_setup, _instance):
    patched_scenario_setup.assert_called_once_with()


def test_name_property(_instance):
    assert 'default' == _instance.name


def test_directory_property(molecule_scenario_directory_fixture, _instance):
    assert molecule_scenario_directory_fixture == _instance.directory


def test_ephemeral_directory_property(_instance):
    project_directory = os.path.basename(_instance.config.project_directory)
    scenario_name = _instance.name
    project_scenario_directory = os.path.join('molecule', project_directory,
                                              scenario_name)
    e_dir = os.path.join(tempfile.gettempdir(), project_scenario_directory)

    assert e_dir == _instance.ephemeral_directory


def test_inventory_directory_property(_instance):
    ephemeral_directory = _instance.config.scenario.ephemeral_directory
    e_dir = os.path.join(ephemeral_directory, "inventory")

    assert e_dir == _instance.inventory_directory


def test_check_sequence_property(_instance):
    sequence = [
        'destroy',
        'dependency',
        'create',
        'prepare',
        'converge',
        'check',
        'destroy',
    ]

    assert sequence == _instance.check_sequence


def test_converge_sequence_property(_instance):
    sequence = [
        'dependency',
        'create',
        'prepare',
        'converge',
    ]

    assert sequence == _instance.converge_sequence


def test_create_sequence_property(_instance):
    sequence = [
        'create',
        'prepare',
    ]

    assert sequence == _instance.create_sequence


def test_dependency_sequence_property(_instance):
    assert ['dependency'] == _instance.dependency_sequence


def test_destroy_sequence_property(_instance):
    assert ['destroy'] == _instance.destroy_sequence


def test_idempotence_sequence_property(_instance):
    assert ['idempotence'] == _instance.idempotence_sequence


def test_lint_sequence_property(_instance):
    assert ['lint'] == _instance.lint_sequence


def test_prepare_sequence_property(_instance):
    assert ['prepare'] == _instance.prepare_sequence


def test_side_effect_sequence_property(_instance):
    assert ['side_effect'] == _instance.side_effect_sequence


def test_syntax_sequence_property(_instance):
    assert ['syntax'] == _instance.syntax_sequence


def test_test_sequence_property(_instance):
    sequence = [
        'lint',
        'destroy',
        'dependency',
        'syntax',
        'create',
        'prepare',
        'converge',
        'idempotence',
        'side_effect',
        'verify',
        'destroy',
    ]

    assert sequence == _instance.test_sequence


def test_verify_sequence_property(_instance):
    assert ['verify'] == _instance.verify_sequence


def test_sequence_property(_instance):
    assert 'lint' == _instance.sequence[0]


def test_sequence_property_with_invalid_subcommand(_instance):
    _instance.config.command_args = {'subcommand': 'invalid'}

    assert [] == _instance.sequence


def test_setup_creates_ephemeral_and_inventory_directories(_instance):
    ephemeral_dir = _instance.config.scenario.ephemeral_directory
    inventory_dir = _instance.config.scenario.inventory_directory
    shutil.rmtree(ephemeral_dir)
    _instance._setup()

    assert os.path.isdir(ephemeral_dir)
    assert os.path.isdir(inventory_dir)


def test_ephemeral_directory():
    e_dir = os.path.join(tempfile.gettempdir(), 'foo/bar')

    assert e_dir == scenario.ephemeral_directory('foo/bar')


def test_ephemeral_directory_overriden_via_env_var(monkeypatch):
    monkeypatch.setenv('MOLECULE_EPHEMERAL_DIRECTORY', 'foo/bar')
    e_dir = os.path.join(tempfile.gettempdir(), 'foo/bar')

    assert e_dir == scenario.ephemeral_directory('foo/bar')


def test_ephemeral_directory_overriden_via_env_var_uses_absolute_path(
        monkeypatch):
    monkeypatch.setenv('MOLECULE_EPHEMERAL_DIRECTORY', '/foo/bar')

    assert '/foo/bar' == scenario.ephemeral_directory('foo/bar')

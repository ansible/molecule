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
import shutil

import pytest

from molecule import config
from molecule import scenario


@pytest.fixture
def scenario_instance(config_instance):
    return scenario.Scenario(config_instance)


def test_config_member(scenario_instance):
    assert isinstance(scenario_instance.config, config.Config)


def test_init_calls_setup(patched_scenario_setup, scenario_instance):
    patched_scenario_setup.assert_called_once_with()


def test_name_property(scenario_instance):
    assert 'default' == scenario_instance.name


def test_directory_property(molecule_scenario_directory_fixture,
                            scenario_instance):
    assert molecule_scenario_directory_fixture == scenario_instance.directory


def test_ephemeral_directory_property(molecule_scenario_directory_fixture,
                                      scenario_instance):
    x = os.path.join(molecule_scenario_directory_fixture, '.molecule')

    assert x == scenario_instance.ephemeral_directory


def test_check_sequence_property(scenario_instance):
    x = [
        'destroy',
        'dependency',
        'create',
        'prepare',
        'converge',
        'check',
        'destroy',
    ]

    assert x == scenario_instance.check_sequence


def test_converge_sequence_property(scenario_instance):
    x = [
        'dependency',
        'create',
        'prepare',
        'converge',
    ]

    assert x == scenario_instance.converge_sequence


def test_create_sequence_property(scenario_instance):
    x = [
        'create',
        'prepare',
    ]

    assert x == scenario_instance.create_sequence


def test_dependency_sequence_property(scenario_instance):
    assert ['dependency'] == scenario_instance.dependency_sequence


def test_destroy_sequence_property(scenario_instance):
    assert ['destroy'] == scenario_instance.destroy_sequence


def test_idempotence_sequence_property(scenario_instance):
    assert ['idempotence'] == scenario_instance.idempotence_sequence


def test_lint_sequence_property(scenario_instance):
    assert ['lint'] == scenario_instance.lint_sequence


def test_prepare_sequence_property(scenario_instance):
    assert ['prepare'] == scenario_instance.prepare_sequence


def test_side_effect_sequence_property(scenario_instance):
    assert ['side_effect'] == scenario_instance.side_effect_sequence


def test_syntax_sequence_property(scenario_instance):
    assert ['syntax'] == scenario_instance.syntax_sequence


def test_test_sequence_property(scenario_instance):
    x = [
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

    assert x == scenario_instance.test_sequence


def test_verify_sequence_property(scenario_instance):
    assert ['verify'] == scenario_instance.verify_sequence


def test_sequence_property(scenario_instance):
    assert 'lint' == scenario_instance.sequence[0]


def test_sequence_property_with_invalid_subcommand(scenario_instance):
    scenario_instance.config.command_args = {'subcommand': 'invalid'}

    assert [] == scenario_instance.sequence


def test_setup_creates_ephemeral_directory(scenario_instance):
    ephemeral_directory = scenario_instance.config.scenario.ephemeral_directory
    shutil.rmtree(ephemeral_directory)
    scenario_instance._setup()

    assert os.path.isdir(ephemeral_directory)


def test_ephemeral_directory():
    assert '/foo/bar/.molecule' == scenario.ephemeral_directory('/foo/bar')


def test_ephemeral_directory_overriden_via_env_var(monkeypatch):
    monkeypatch.setenv('MOLECULE_EPHEMERAL_DIRECTORY', '.foo')

    assert '/foo/bar/.foo' == scenario.ephemeral_directory('/foo/bar')

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

from molecule import config
from molecule import platforms
from molecule import scenario
from molecule import state
from molecule.dependency import ansible_galaxy
from molecule.dependency import gilt
from molecule.driver import dockr
from molecule.lint import ansible_lint
from molecule.provisioner import ansible
from molecule.verifier import testinfra


@pytest.fixture
def config_data():
    return {}


@pytest.fixture
def config_instance(platforms_data, molecule_file, config_data):
    configs = [platforms_data, config_data]

    return config.Config(molecule_file, configs=configs)


def test_molecule_file_private_member(molecule_file, config_instance):
    assert molecule_file == config_instance.molecule_file


def test_args_member(config_instance):
    assert {} == config_instance.args


def test_command_args_member(config_instance):
    assert {} == config_instance.command_args


def test_init_calls_setup(mocker, molecule_file, platforms_data, config_data):
    m = mocker.patch('molecule.config.Config._setup')
    config.Config(
        molecule_file,
        args={'debug': True},
        configs=[platforms_data, config_data])

    m.assert_called_once_with()


def test_ephemeral_directory_property(config_instance):
    x = os.path.join(
        config.molecule_ephemeral_directory(
            config_instance.scenario.directory))

    assert x == config_instance.ephemeral_directory


def test_dependency_property(config_instance):
    assert isinstance(config_instance.dependency, ansible_galaxy.AnsibleGalaxy)


def test_dependency_property_raises(patched_print_error, platforms_data,
                                    molecule_file):
    config_data = {'dependency': {'name': 'invalid'}}
    configs = [platforms_data, config_data]
    c = config.Config(molecule_file, configs=configs)

    with pytest.raises(SystemExit) as e:
        c.dependency

    assert 1 == e.value.code

    msg = "Invalid dependency named 'invalid' configured."
    patched_print_error.assert_called_once_with(msg)


def test_dependency_property_is_gilt(config_instance, molecule_file):
    gilt_data = {'dependency': {'name': 'gilt'}}
    configs = [gilt_data]
    c = config.Config(molecule_file, configs=configs)

    assert isinstance(c.dependency, gilt.Gilt)


def test_driver_property(config_instance):
    assert isinstance(config_instance.driver, dockr.Dockr)


def test_driver_property_raises(patched_print_error, platforms_data,
                                molecule_file):
    config_data = {'driver': {'name': 'invalid'}}
    configs = [platforms_data, config_data]
    c = config.Config(molecule_file, configs=configs)

    with pytest.raises(SystemExit) as e:
        c.driver

    assert 1 == e.value.code

    msg = "Invalid driver named 'invalid' configured."
    patched_print_error.assert_called_once_with(msg)


def test_lint_property(config_instance):
    assert isinstance(config_instance.lint, ansible_lint.AnsibleLint)


def test_lint_property_raises(patched_print_error, platforms_data,
                              molecule_file):
    config_data = {'lint': {'name': 'invalid'}}
    configs = [platforms_data, config_data]
    c = config.Config(molecule_file, configs=configs)

    with pytest.raises(SystemExit) as e:
        c.lint

    assert 1 == e.value.code

    msg = "Invalid lint named 'invalid' configured."
    patched_print_error.assert_called_once_with(msg)


def test_platforms_property(config_instance):
    assert isinstance(config_instance.platforms, platforms.Platforms)


def test_provisioner_property(config_instance):
    assert isinstance(config_instance.provisioner, ansible.Ansible)


def test_provisioner_property_raises(patched_print_error, platforms_data,
                                     molecule_file):
    config_data = {'provisioner': {'name': 'invalid'}}
    configs = [platforms_data, config_data]
    c = config.Config(molecule_file, configs=configs)

    with pytest.raises(SystemExit) as e:
        c.provisioner

    assert 1 == e.value.code

    msg = "Invalid provisioner named 'invalid' configured."
    patched_print_error.assert_called_once_with(msg)


def test_scenario_property(config_instance):
    assert isinstance(config_instance.scenario, scenario.Scenario)


def test_state_property(config_instance):
    assert isinstance(config_instance.state, state.State)


def test_verifier_property(config_instance):
    assert isinstance(config_instance.verifier, testinfra.Testinfra)


def test_verifier_property_raises(patched_print_error, platforms_data,
                                  molecule_file):
    config_data = {'verifier': {'name': 'invalid'}}
    configs = [platforms_data, config_data]
    c = config.Config(molecule_file, configs=configs)

    with pytest.raises(SystemExit) as e:
        c.verifier

    assert 1 == e.value.code

    msg = "Invalid verifier named 'invalid' configured."
    patched_print_error.assert_called_once_with(msg)


@pytest.fixture()
def project_config_data():
    return {'driver': {'name': 'project-override'}}


@pytest.fixture()
def local_config_data():
    return {'driver': {'name': 'local-override', 'options': {'foo': 'bar'}}}


def test_combine_default_and_project_dicts(project_config_data, molecule_file,
                                           config_data):
    configs = [project_config_data, config_data]
    c = config.Config(molecule_file, configs=configs)

    assert 'project-override' == c.config['driver']['name']
    assert {} == c.config['driver']['options']


def test_combine_default_local_and_project_dicts(
        project_config_data, local_config_data, molecule_file, config_data):
    configs = [project_config_data, local_config_data]
    c = config.Config(molecule_file, configs=configs)

    assert 'local-override' == c.config['driver']['name']
    return {'foo': 'bar'} == c.config['driver']['options']


def test_merge_dicts(config_instance):
    # example taken from python-anyconfig/anyconfig/__init__.py
    a = {'b': [{'c': 0}, {'c': 2}], 'd': {'e': 'aaa', 'f': 3}}
    b = {'a': 1, 'b': [{'c': 3}], 'd': {'e': 'bbb'}}
    x = {'a': 1, 'b': [{'c': 3}], 'd': {'e': "bbb", 'f': 3}}

    assert x == config_instance.merge_dicts(a, b)


def test_setup(config_instance):
    config_instance._setup()

    assert os.path.isdir(config_instance.ephemeral_directory)


def test_exit_with_invalid_section(config_instance, patched_print_error):
    with pytest.raises(SystemExit) as e:
        config_instance._exit_with_invalid_section('section', 'name')

    assert 1 == e.value.code

    msg = "Invalid section named 'name' configured."
    patched_print_error.assert_called_once_with(msg)


def test_molecule_directory():
    assert '/foo/molecule' == config.molecule_directory('/foo')


def test_molecule_ephemeral_directory():
    assert '/foo/.molecule' == config.molecule_ephemeral_directory('/foo')


def test_molecule_file():
    assert '/foo/molecule.yml' == config.molecule_file('/foo')

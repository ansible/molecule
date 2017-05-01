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
from molecule.driver import lxc
from molecule.driver import lxd
from molecule.driver import static
from molecule.driver import vagrant
from molecule.lint import ansible_lint
from molecule.provisioner import ansible
from molecule.verifier import goss
from molecule.verifier import testinfra


def test_molecule_file_private_member(molecule_file, config_instance):
    assert molecule_file == config_instance.molecule_file


def test_args_member(config_instance):
    assert {} == config_instance.args


def test_command_args_member(config_instance):
    assert {} == config_instance.command_args


def test_ephemeral_directory_property(config_instance):
    x = os.path.join(
        config.molecule_ephemeral_directory(
            config_instance.scenario.directory))

    assert x == config_instance.ephemeral_directory


def test_dependency_property(config_instance):
    assert isinstance(config_instance.dependency, ansible_galaxy.AnsibleGalaxy)


@pytest.fixture
def molecule_dependency_gilt_section_data():
    return {'dependency': {'name': 'gilt'}, }


def test_dependency_property_is_gilt(molecule_dependency_gilt_section_data,
                                     config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_dependency_gilt_section_data)

    assert isinstance(config_instance.dependency, gilt.Gilt)


@pytest.fixture
def molecule_dependency_invalid_section_data():
    return {'dependency': {'name': 'invalid'}, }


def test_dependency_property_raises(molecule_dependency_invalid_section_data,
                                    patched_logger_critical, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_dependency_invalid_section_data)
    with pytest.raises(SystemExit) as e:
        config_instance.dependency

    assert 1 == e.value.code

    msg = "Invalid dependency named 'invalid' configured."
    patched_logger_critical.assert_called_once_with(msg)


def test_driver_property(config_instance):
    assert isinstance(config_instance.driver, dockr.Dockr)


@pytest.fixture
def molecule_driver_lxc_section_data():
    return {'driver': {'name': 'lxc'}, }


def test_driver_property_is_lxc(molecule_driver_lxc_section_data,
                                config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_lxc_section_data)

    assert isinstance(config_instance.driver, lxc.Lxc)


@pytest.fixture
def molecule_driver_lxd_section_data():
    return {'driver': {'name': 'lxd'}, }


def test_driver_property_is_lxd(molecule_driver_lxd_section_data,
                                config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_lxd_section_data)

    assert isinstance(config_instance.driver, lxd.Lxd)


def test_driver_property_is_static(molecule_driver_static_section_data,
                                   config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_static_section_data)

    assert isinstance(config_instance.driver, static.Static)


@pytest.fixture
def molecule_driver_vagrant_section_data():
    return {'driver': {'name': 'vagrant'}, }


def test_driver_property_is_vagrant(molecule_driver_vagrant_section_data,
                                    config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_vagrant_section_data)

    assert isinstance(config_instance.driver, vagrant.Vagrant)


@pytest.fixture
def molecule_driver_invalid_section_data():
    return {'driver': {'name': 'invalid'}, }


def test_driver_property_raises(molecule_driver_invalid_section_data,
                                patched_logger_critical, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_invalid_section_data)
    with pytest.raises(SystemExit) as e:
        config_instance.driver

    assert 1 == e.value.code

    msg = "Invalid driver named 'invalid' configured."
    patched_logger_critical.assert_called_once_with(msg)


def test_drivers_property(config_instance):
    x = ['docker', 'lxc', 'lxd', 'static', 'vagrant']

    assert x == config_instance.drivers


def test_lint_property(config_instance):
    assert isinstance(config_instance.lint, ansible_lint.AnsibleLint)


@pytest.fixture
def molecule_lint_invalid_section_data():
    return {'lint': {'name': 'invalid'}, }


def test_lint_property_raises(molecule_lint_invalid_section_data,
                              patched_logger_critical, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_lint_invalid_section_data)
    with pytest.raises(SystemExit) as e:
        config_instance.lint

    assert 1 == e.value.code

    msg = "Invalid lint named 'invalid' configured."
    patched_logger_critical.assert_called_once_with(msg)


def test_platforms_property(config_instance):
    assert isinstance(config_instance.platforms, platforms.Platforms)


def test_provisioner_property(config_instance):
    assert isinstance(config_instance.provisioner, ansible.Ansible)


@pytest.fixture
def molecule_provisioner_invalid_section_data():
    return {'provisioner': {'name': 'invalid'}, }


def test_provisioner_property_raises(molecule_provisioner_invalid_section_data,
                                     patched_logger_critical, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_provisioner_invalid_section_data)
    with pytest.raises(SystemExit) as e:
        config_instance.provisioner

    assert 1 == e.value.code

    msg = "Invalid provisioner named 'invalid' configured."
    patched_logger_critical.assert_called_once_with(msg)


def test_scenario_property(config_instance):
    assert isinstance(config_instance.scenario, scenario.Scenario)


def test_state_property(config_instance):
    assert isinstance(config_instance.state, state.State)


def test_verifier_property(config_instance):
    assert isinstance(config_instance.verifier, testinfra.Testinfra)


@pytest.fixture
def molecule_verifier_goss_section_data():
    return {'verifier': {'name': 'goss'}, }


def test_verifier_property_is_goss(molecule_verifier_goss_section_data,
                                   config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_verifier_goss_section_data)

    assert isinstance(config_instance.verifier, goss.Goss)


@pytest.fixture
def molecule_verifier_invalid_section_data():
    return {'verifier': {'name': 'invalid'}, }


def test_verifier_property_raises(molecule_verifier_invalid_section_data,
                                  patched_logger_critical, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_verifier_invalid_section_data)
    with pytest.raises(SystemExit) as e:
        config_instance.verifier

    assert 1 == e.value.code

    msg = "Invalid verifier named 'invalid' configured."
    patched_logger_critical.assert_called_once_with(msg)


def test_verifiers_property(config_instance):
    x = ['goss', 'testinfra']

    assert x == config_instance.verifiers


def test_exit_with_invalid_section(config_instance, patched_logger_critical):
    with pytest.raises(SystemExit) as e:
        config_instance._exit_with_invalid_section('section', 'name')

    assert 1 == e.value.code

    msg = "Invalid section named 'name' configured."
    patched_logger_critical.assert_called_once_with(msg)


def test_merge_dicts(config_instance):
    # example taken from python-anyconfig/anyconfig/__init__.py
    a = {'b': [{'c': 0}, {'c': 2}], 'd': {'e': 'aaa', 'f': 3}}
    b = {'a': 1, 'b': [{'c': 3}], 'd': {'e': 'bbb'}}
    x = {'a': 1, 'b': [{'c': 3}], 'd': {'e': "bbb", 'f': 3}}

    assert x == config.merge_dicts(a, b)


def test_molecule_directory():
    assert '/foo/molecule' == config.molecule_directory('/foo')


def test_molecule_ephemeral_directory():
    assert '/foo/.molecule' == config.molecule_ephemeral_directory('/foo')


def test_molecule_file():
    assert '/foo/molecule.yml' == config.molecule_file('/foo')


def test_molecule_drivers():
    x = ['docker', 'lxc', 'lxd', 'static', 'vagrant']

    assert x == config.molecule_drivers()


def test_molecule_verifiers():
    x = ['goss', 'testinfra']

    assert x == config.molecule_verifiers()

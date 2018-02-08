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
from molecule import util
from molecule.dependency import ansible_galaxy
from molecule.dependency import gilt
from molecule.driver import azure
from molecule.driver import delegated
from molecule.driver import docker
from molecule.driver import ec2
from molecule.driver import gce
from molecule.driver import lxc
from molecule.driver import lxd
from molecule.driver import openstack
from molecule.driver import vagrant
from molecule.lint import yamllint
from molecule.provisioner import ansible
from molecule.verifier import goss
from molecule.verifier import testinfra


def test_molecule_file_private_member(molecule_file_fixture, config_instance):
    assert molecule_file_fixture == config_instance.molecule_file


def test_args_member(config_instance):
    assert {} == config_instance.args


def test_command_args_member(config_instance):
    x = {'subcommand': 'test'}

    assert x == config_instance.command_args


def test_debug_property(config_instance):
    assert not config_instance.debug


def test_subcommand_property(config_instance):
    assert 'test' == config_instance.subcommand


def test_action_property(config_instance):
    assert config_instance.action is None


def test_action_setter(config_instance):
    config_instance.action = 'foo'

    assert 'foo' == config_instance.action


def test_project_directory_property(config_instance):
    assert os.getcwd() == config_instance.project_directory


def test_molecule_directory_property(config_instance):
    x = os.path.join(os.getcwd(), 'molecule')

    assert x == config_instance.molecule_directory


def test_dependency_property(config_instance):
    assert isinstance(config_instance.dependency, ansible_galaxy.AnsibleGalaxy)


@pytest.fixture
def molecule_dependency_gilt_section_data():
    return {
        'dependency': {
            'name': 'gilt'
        },
    }


def test_dependency_property_is_gilt(molecule_dependency_gilt_section_data,
                                     config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_dependency_gilt_section_data)

    assert isinstance(config_instance.dependency, gilt.Gilt)


@pytest.fixture
def molecule_dependency_invalid_section_data():
    return {
        'dependency': {
            'name': 'invalid'
        },
    }


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
    assert isinstance(config_instance.driver, docker.Docker)


@pytest.fixture
def molecule_driver_azure_section_data():
    return {
        'driver': {
            'name': 'azure'
        },
    }


def test_driver_property_is_azure(molecule_driver_azure_section_data,
                                  config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_azure_section_data)

    assert isinstance(config_instance.driver, azure.Azure)


def test_driver_property_is_delegated(molecule_driver_delegated_section_data,
                                      config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_delegated_section_data)

    assert isinstance(config_instance.driver, delegated.Delegated)


@pytest.fixture
def molecule_driver_ec2_section_data():
    return {
        'driver': {
            'name': 'ec2'
        },
    }


def test_driver_property_is_ec2(molecule_driver_ec2_section_data,
                                config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_ec2_section_data)

    assert isinstance(config_instance.driver, ec2.Ec2)


@pytest.fixture
def molecule_driver_gce_section_data():
    return {
        'driver': {
            'name': 'gce'
        },
    }


def test_driver_property_is_gce(molecule_driver_gce_section_data,
                                config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_gce_section_data)

    assert isinstance(config_instance.driver, gce.Gce)


@pytest.fixture
def molecule_driver_lxc_section_data():
    return {
        'driver': {
            'name': 'lxc'
        },
    }


def test_driver_property_is_lxc(molecule_driver_lxc_section_data,
                                config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_lxc_section_data)

    assert isinstance(config_instance.driver, lxc.Lxc)


@pytest.fixture
def molecule_driver_lxd_section_data():
    return {
        'driver': {
            'name': 'lxd'
        },
    }


def test_driver_property_is_lxd(molecule_driver_lxd_section_data,
                                config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_lxd_section_data)

    assert isinstance(config_instance.driver, lxd.Lxd)


@pytest.fixture
def molecule_driver_openstack_section_data():
    return {
        'driver': {
            'name': 'openstack'
        },
    }


def test_driver_property_is_openstack(molecule_driver_openstack_section_data,
                                      config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_openstack_section_data)

    assert isinstance(config_instance.driver, openstack.Openstack)


@pytest.fixture
def molecule_driver_vagrant_section_data():
    return {
        'driver': {
            'name': 'vagrant'
        },
    }


def test_driver_property_is_vagrant(molecule_driver_vagrant_section_data,
                                    config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_vagrant_section_data)

    assert isinstance(config_instance.driver, vagrant.Vagrant)


@pytest.fixture
def molecule_driver_invalid_section_data():
    return {
        'driver': {
            'name': 'invalid'
        },
    }


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
    x = [
        'azure',
        'delegated',
        'docker',
        'ec2',
        'gce',
        'lxc',
        'lxd',
        'openstack',
        'vagrant',
    ]

    assert x == config_instance.drivers


def test_env(config_instance):
    x = {
        'MOLECULE_DEBUG':
        'False',
        'MOLECULE_FILE':
        config_instance.molecule_file,
        'MOLECULE_INVENTORY_FILE':
        config_instance.provisioner.inventory_file,
        'MOLECULE_EPHEMERAL_DIRECTORY':
        config_instance.scenario.ephemeral_directory,
        'MOLECULE_SCENARIO_DIRECTORY':
        config_instance.scenario.directory,
        'MOLECULE_INSTANCE_CONFIG':
        config_instance.driver.instance_config,
        'MOLECULE_DEPENDENCY_NAME':
        'galaxy',
        'MOLECULE_DRIVER_NAME':
        'docker',
        'MOLECULE_LINT_NAME':
        'yamllint',
        'MOLECULE_PROVISIONER_NAME':
        'ansible',
        'MOLECULE_SCENARIO_NAME':
        'default',
        'MOLECULE_VERIFIER_NAME':
        'testinfra'
    }

    assert x == config_instance.env


def test_lint_property(config_instance):
    assert isinstance(config_instance.lint, yamllint.Yamllint)


@pytest.fixture
def molecule_lint_invalid_section_data():
    return {
        'lint': {
            'name': 'invalid'
        },
    }


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
    return {
        'provisioner': {
            'name': 'invalid'
        },
    }


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
    return {
        'verifier': {
            'name': 'goss'
        },
    }


def test_verifier_property_is_goss(molecule_verifier_goss_section_data,
                                   config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_verifier_goss_section_data)

    assert isinstance(config_instance.verifier, goss.Goss)


@pytest.fixture
def molecule_verifier_invalid_section_data():
    return {
        'verifier': {
            'name': 'invalid'
        },
    }


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


def test_merge_dicts_instance_proxies(config_instance):
    a = {'a': 1}
    b = {'b': 2}
    result = config.merge_dicts(a, b)

    assert isinstance(result, dict)


def test_get_driver_name_from_state_file(config_instance):
    config_instance.state.change_state('driver', 'state-driver')

    assert 'state-driver' == config_instance._get_driver_name()


def test_get_driver_name_from_cli(config_instance):
    config_instance.command_args = {'driver_name': 'cli-driver'}

    assert 'cli-driver' == config_instance._get_driver_name()


def test_get_driver_name(config_instance):
    assert 'docker' == config_instance._get_driver_name()


def test_get_driver_name_raises_when_different_driver_used(
        patched_logger_critical, config_instance):
    config_instance.state.change_state('driver', 'foo')
    config_instance.command_args = {'driver_name': 'bar'}
    with pytest.raises(SystemExit) as e:
        config_instance._get_driver_name()

    assert 1 == e.value.code

    msg = ("Instance(s) were created with the 'foo' driver, "
           "but the subcommand is using 'bar' driver.")

    patched_logger_critical.assert_called_once_with(msg)


def test_combine(config_instance):
    assert isinstance(config_instance._combine(), dict)


def test_combine_raises_on_failed_interpolation(patched_logger_critical,
                                                config_instance):
    contents = {'foo': '$6$8I5Cfmpr$kGZB'}
    util.write_file(config_instance.molecule_file, util.safe_dump(contents))

    with pytest.raises(SystemExit) as e:
        config_instance._combine()

    assert 1 == e.value.code

    msg = ("parsing config file '{}'.\n\n"
           'Invalid placeholder in string: line 4, col 6\n'
           '# Molecule managed\n\n'
           '---\n'
           'foo: $6$8I5Cfmpr$kGZB\n').format(config_instance.molecule_file)
    patched_logger_critical.assert_called_once_with(msg)


def test_merge_dicts():
    # example taken from python-anyconfig/anyconfig/__init__.py
    a = {'b': [{'c': 0}, {'c': 2}], 'd': {'e': 'aaa', 'f': 3}}
    b = {'a': 1, 'b': [{'c': 3}], 'd': {'e': 'bbb'}}
    x = {'a': 1, 'b': [{'c': 3}], 'd': {'e': "bbb", 'f': 3}}

    assert x == config.merge_dicts(a, b)


def test_molecule_directory():
    assert '/foo/bar/molecule' == config.molecule_directory('/foo/bar')


def test_molecule_file():
    assert '/foo/bar/molecule.yml' == config.molecule_file('/foo/bar')


def test_molecule_drivers():
    x = [
        'azure',
        'delegated',
        'docker',
        'ec2',
        'gce',
        'lxc',
        'lxd',
        'openstack',
        'vagrant',
    ]

    assert x == config.molecule_drivers()


def test_molecule_verifiers():
    x = ['goss', 'testinfra']

    assert x == config.molecule_verifiers()

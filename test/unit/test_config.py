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

import pytest

from molecule import config
from molecule import platforms
from molecule import scenario
from molecule import state
from molecule import util
from molecule.dependency import ansible_galaxy
from molecule.dependency import gilt
from molecule.dependency import shell
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
from molecule.verifier import inspec
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


def test_env_file_property(config_instance):
    config_instance.args = {'env_file': '.env'}
    result = config_instance.env_file

    assert util.abs_path(config_instance.args.get('env_file')) == result


def test_subcommand_property(config_instance):
    assert 'test' == config_instance.subcommand


def test_action_property(config_instance):
    assert config_instance.action is None


def test_action_setter(config_instance):
    config_instance.action = 'foo'

    assert 'foo' == config_instance.action


def test_init_calls_validate(patched_config_validate, config_instance):
    patched_config_validate.assert_called_once_with()


def test_project_directory_property(config_instance):
    assert os.getcwd() == config_instance.project_directory


def test_molecule_directory_property(config_instance):
    x = os.path.join(os.getcwd(), 'molecule')

    assert x == config_instance.molecule_directory


def test_dependency_property(config_instance):
    assert isinstance(config_instance.dependency, ansible_galaxy.AnsibleGalaxy)


@pytest.fixture
def _config_dependency_gilt_section_data():
    return {
        'dependency': {
            'name': 'gilt'
        },
    }


@pytest.mark.parametrize(
    'config_instance', ['_config_dependency_gilt_section_data'], indirect=True)
def test_dependency_property_is_gilt(config_instance):
    assert isinstance(config_instance.dependency, gilt.Gilt)


@pytest.fixture
def _config_dependency_shell_section_data():
    return {
        'dependency': {
            'name': 'shell',
            'command': 'bin/command',
        },
    }


@pytest.mark.parametrize(
    'config_instance', ['_config_dependency_shell_section_data'],
    indirect=True)
def test_dependency_property_is_shell(config_instance):
    assert isinstance(config_instance.dependency, shell.Shell)


def test_driver_property(config_instance):
    assert isinstance(config_instance.driver, docker.Docker)


@pytest.fixture
def _config_driver_azure_section_data():
    return {
        'driver': {
            'name': 'azure'
        },
    }


@pytest.mark.parametrize(
    'config_instance', ['_config_driver_azure_section_data'], indirect=True)
def test_driver_property_is_azure(config_instance):
    assert isinstance(config_instance.driver, azure.Azure)


@pytest.fixture
def _config_driver_delegated_section_data():
    return {
        'driver': {
            'name': 'delegated',
            'options': {
                'managed': False,
            },
        },
    }


@pytest.mark.parametrize(
    'config_instance', ['_config_driver_delegated_section_data'],
    indirect=True)
def test_driver_property_is_delegated(config_instance):
    assert isinstance(config_instance.driver, delegated.Delegated)


@pytest.fixture
def _config_driver_ec2_section_data():
    return {
        'driver': {
            'name': 'ec2'
        },
    }


@pytest.mark.parametrize(
    'config_instance', ['_config_driver_ec2_section_data'], indirect=True)
def test_driver_property_is_ec2(config_instance):
    assert isinstance(config_instance.driver, ec2.EC2)


@pytest.fixture
def _config_driver_gce_section_data():
    return {
        'driver': {
            'name': 'gce'
        },
    }


@pytest.mark.parametrize(
    'config_instance', ['_config_driver_gce_section_data'], indirect=True)
def test_driver_property_is_gce(config_instance):
    assert isinstance(config_instance.driver, gce.GCE)


@pytest.fixture
def _config_driver_lxc_section_data():
    return {
        'driver': {
            'name': 'lxc'
        },
    }


@pytest.mark.parametrize(
    'config_instance', ['_config_driver_lxc_section_data'], indirect=True)
def test_driver_property_is_lxc(config_instance):
    assert isinstance(config_instance.driver, lxc.LXC)


@pytest.fixture
def _config_driver_lxd_section_data():
    return {
        'driver': {
            'name': 'lxd'
        },
    }


@pytest.mark.parametrize(
    'config_instance', ['_config_driver_lxd_section_data'], indirect=True)
def test_driver_property_is_lxd(config_instance):
    assert isinstance(config_instance.driver, lxd.LXD)


@pytest.fixture
def _config_driver_openstack_section_data():
    return {
        'driver': {
            'name': 'openstack'
        },
    }


@pytest.mark.parametrize(
    'config_instance', ['_config_driver_openstack_section_data'],
    indirect=True)
def test_driver_property_is_openstack(config_instance):
    assert isinstance(config_instance.driver, openstack.Openstack)


@pytest.fixture
def _config_driver_vagrant_section_data():
    return {
        'driver': {
            'name': 'vagrant',
            'provider': {
                'name': 'virtualbox',
            },
        },
    }


@pytest.mark.parametrize(
    'config_instance', ['_config_driver_vagrant_section_data'], indirect=True)
def test_driver_property_is_vagrant(config_instance):
    assert isinstance(config_instance.driver, vagrant.Vagrant)


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
    config_instance.args = {'env_file': '.env'}
    x = {
        'MOLECULE_DEBUG':
        'False',
        'MOLECULE_FILE':
        config_instance.molecule_file,
        'MOLECULE_ENV_FILE':
        util.abs_path(config_instance.args.get('env_file')),
        'MOLECULE_INVENTORY_FILE':
        config_instance.provisioner.inventory_file,
        'MOLECULE_EPHEMERAL_DIRECTORY':
        config_instance.scenario.ephemeral_directory,
        'MOLECULE_SCENARIO_DIRECTORY':
        config_instance.scenario.directory,
        'MOLECULE_PROJECT_DIRECTORY':
        config_instance.project_directory,
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
        'MOLECULE_PROVISIONER_LINT_NAME':
        'ansible-lint',
        'MOLECULE_SCENARIO_NAME':
        'default',
        'MOLECULE_VERIFIER_NAME':
        'testinfra',
        'MOLECULE_VERIFIER_LINT_NAME':
        'flake8',
        'MOLECULE_VERIFIER_TEST_DIRECTORY':
        config_instance.verifier.directory,
    }

    assert x == config_instance.env


def test_lint_property(config_instance):
    assert isinstance(config_instance.lint, yamllint.Yamllint)


def test_platforms_property(config_instance):
    assert isinstance(config_instance.platforms, platforms.Platforms)


def test_provisioner_property(config_instance):
    assert isinstance(config_instance.provisioner, ansible.Ansible)


def test_scenario_property(config_instance):
    assert isinstance(config_instance.scenario, scenario.Scenario)


def test_state_property(config_instance):
    assert isinstance(config_instance.state, state.State)


def test_verifier_property(config_instance):
    assert isinstance(config_instance.verifier, testinfra.Testinfra)


@pytest.fixture
def _config_verifier_inspec_section_data():
    return {
        'verifier': {
            'name': 'inspec',
            'lint': {
                'name': 'rubocop',
            },
        },
    }


@pytest.mark.parametrize(
    'config_instance', ['_config_verifier_inspec_section_data'], indirect=True)
def test_verifier_property_is_inspec(config_instance):
    assert isinstance(config_instance.verifier, inspec.Inspec)


@pytest.fixture
def _config_verifier_goss_section_data():
    return {
        'verifier': {
            'name': 'goss',
            'lint': {
                'name': 'yamllint',
            },
        },
    }


@pytest.mark.parametrize(
    'config_instance', ['_config_verifier_goss_section_data'], indirect=True)
def test_verifier_property_is_goss(config_instance):
    assert isinstance(config_instance.verifier, goss.Goss)


def test_verifiers_property(config_instance):
    x = ['goss', 'inspec', 'testinfra']

    assert x == config_instance.verifiers


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


def test_get_config(config_instance):
    assert isinstance(config_instance._get_config(), dict)


def test_get_config_with_base_config(config_instance):
    config_instance.args = {'base_config': './foo.yml'}
    contents = {'foo': 'bar'}
    util.write_file(config_instance.args['base_config'],
                    util.safe_dump(contents))
    result = config_instance._get_config()

    assert result['foo'] == 'bar'


def test_reget_config(config_instance):
    assert isinstance(config_instance._reget_config(), dict)


def test_interpolate(patched_logger_critical, config_instance):
    string = 'foo: $HOME'
    x = 'foo: {}'.format(os.environ['HOME'])

    assert x == config_instance._interpolate(string, os.environ, None)


def test_interpolate_raises_on_failed_interpolation(patched_logger_critical,
                                                    config_instance):
    string = '$6$8I5Cfmpr$kGZB'

    with pytest.raises(SystemExit) as e:
        config_instance._interpolate(string, os.environ, None)

    assert 1 == e.value.code

    msg = ("parsing config file '{}'.\n\n"
           'Invalid placeholder in string: line 1, col 1\n'
           '$6$8I5Cfmpr$kGZB').format(config_instance.molecule_file)
    patched_logger_critical.assert_called_once_with(msg)


def test_preflight(mocker, config_instance, patched_logger_info):
    m = mocker.patch('molecule.model.schema_v2.pre_validate')
    m.return_value = None

    config_instance._preflight('foo')

    m.assert_called_once_with('foo', os.environ, config.MOLECULE_KEEP_STRING)


def test_preflight_exists_when_validation_fails(
        mocker, patched_logger_critical, config_instance):
    m = mocker.patch('molecule.model.schema_v2.pre_validate')
    m.return_value = 'validation errors'

    with pytest.raises(SystemExit) as e:
        config_instance._preflight('invalid stream')

    assert 1 == e.value.code

    msg = 'Failed to validate.\n\nvalidation errors'
    patched_logger_critical.assert_called_once_with(msg)


def test_validate(mocker, config_instance, patched_logger_info,
                  patched_logger_success):
    m = mocker.patch('molecule.model.schema_v2.validate')
    m.return_value = None

    config_instance._validate()

    msg = 'Validating schema {}.'.format(config_instance.molecule_file)
    patched_logger_info.assert_called_once_with(msg)

    m.assert_called_once_with(config_instance.config)

    msg = 'Validation completed successfully.'
    patched_logger_success.assert_called_once_with(msg)


def test_validate_exists_when_validation_fails(mocker, patched_logger_critical,
                                               config_instance):
    m = mocker.patch('molecule.model.schema_v2.validate')
    m.return_value = 'validation errors'

    with pytest.raises(SystemExit) as e:
        config_instance._validate()

    assert 1 == e.value.code

    msg = 'Failed to validate.\n\nvalidation errors'
    patched_logger_critical.assert_called_once_with(msg)


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
    x = ['goss', 'inspec', 'testinfra']

    assert x == config.molecule_verifiers()


def test_set_env_from_file(config_instance):
    config_instance.args = {'env_file': '.env'}
    contents = {
        'foo': 'bar',
        'BAZ': 'zzyzx',
    }
    env_file = config_instance.args.get('env_file')
    util.write_file(env_file, util.safe_dump(contents))
    env = config.set_env_from_file({}, env_file)

    assert contents == env


def test_set_env_from_file_returns_original_env_when_env_file_not_found(
        config_instance):
    env = config.set_env_from_file({}, 'file-not-found')

    assert {} == env

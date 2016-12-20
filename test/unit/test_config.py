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

from molecule import config
from molecule.dependency import ansible_galaxy
from molecule.driver import docker
from molecule.lint import ansible_lint
from molecule.provisioner import ansible
from molecule.verifier import testinfra


@pytest.fixture()
def project_config_data():
    return {'driver': {'name': 'project-override'}}


@pytest.fixture()
def local_config_data():
    return {'driver': {'name': 'local-override', 'options': {'foo': 'bar'}}}


@pytest.fixture()
def config_instance(temp_dir, request):
    configs = []
    params = request.param
    for fixture in params.get('configs', []):
        if isinstance(fixture, str):
            configs.append(request.getfuncargvalue(fixture))
        else:
            configs.append(fixture)
    params['configs'] = configs
    defaults = {
        'molecule_file': config.molecule_file(temp_dir.strpath),
        'args': {},
        'command_args': {},
        'configs': configs
    }
    defaults.update(params)

    return config.Config(**defaults)


@pytest.mark.parametrize(
    'config_instance', [{
        'molecule_file': config.molecule_file('/foo/bar/molecule/default')
    }],
    indirect=['config_instance'])
def test_molecule_file_private_member(config_instance):
    x = '/foo/bar/molecule/default/molecule.yml'

    assert x == config_instance.molecule_file


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_args_member(config_instance):
    assert {} == config_instance.args


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_command_args_member(config_instance):
    assert {} == config_instance.command_args


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_ephemeral_directory_property(config_instance):
    x = os.path.join(
        config.molecule_ephemeral_directory(
            config_instance.scenario_directory))

    assert x == config_instance.ephemeral_directory


@pytest.mark.parametrize(
    'config_instance', [{
        'configs': [{
            'platforms': [
                {
                    'name': 'instance-1',
                },
                {
                    'name': 'instance-2',
                },
            ]
        }]
    }],
    indirect=['config_instance'])
def test_inventory_property(config_instance):
    x = {
        'instance-1-default': ['ansible_connection=docker'],
        'instance-2-default': ['ansible_connection=docker']
    }

    assert x == config_instance.inventory


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_inventory_file_property(config_instance):
    x = os.path.join(config_instance.ephemeral_directory, 'ansible_inventory')

    assert x == config_instance.inventory_file


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_config_file_property(config_instance):
    x = os.path.join(config_instance.ephemeral_directory, 'ansible.cfg')

    assert x == config_instance.config_file


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_default_dict(config_instance):
    c = config_instance.config

    assert 'galaxy' == c['dependency']['name']
    assert [] == c['platforms']
    assert 'testinfra' == c['verifier']['name']


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_dependency_property(config_instance):
    assert isinstance(config_instance.dependency, ansible_galaxy.AnsibleGalaxy)


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_dependency_name_property(config_instance):
    assert 'galaxy' == config_instance.dependency_name


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_dependency_enabled_property(config_instance):
    assert config_instance.dependency_enabled


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_dependency_options_property(config_instance):
    x = {
        'force': True,
        'role_file': 'requirements.yml',
        'roles_path': '.molecule/roles'
    }

    assert x == config_instance.dependency_options


@pytest.mark.parametrize(
    'config_instance', [{
        'configs': [{
            'dependency': {
                'name': 'galaxy',
                'options': {
                    'foo': 'bar'
                }
            }
        }]
    }],
    indirect=['config_instance'])
def test_dependency_options_property_handles_dependency_options(
        config_instance):
    x = {
        'role_file': 'requirements.yml',
        'roles_path': '.molecule/roles',
        'foo': 'bar',
        'force': True
    }

    assert x == config_instance.dependency_options


@pytest.mark.parametrize(
    'config_instance', [{
        'args': {
            'debug': True
        },
    }],
    indirect=['config_instance'])
def test_dependency_options_property_handles_cli_args(config_instance):
    # Does nothing.  The `ansible-galaxy` command does not support
    # a `debug` flag.
    x = {
        'force': True,
        'role_file': 'requirements.yml',
        'roles_path': '.molecule/roles'
    }

    assert x == config_instance.dependency_options


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_driver_property(config_instance):
    assert isinstance(config_instance.driver, docker.Docker)


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_driver_name_property(config_instance):
    assert 'docker' == config_instance.driver_name


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_driver_options_property(config_instance):
    assert {} == config_instance.driver_options


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_lint_property(config_instance):
    assert isinstance(config_instance.lint, ansible_lint.AnsibleLint)


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_lint_name_property(config_instance):
    assert 'ansible-lint' == config_instance.lint_name


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_lint_enabled_property(config_instance):
    assert config_instance.lint_enabled


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_lint_options_property(config_instance):
    assert {} == config_instance.lint_options


@pytest.mark.parametrize(
    'config_instance', [{
        'configs': [{
            'lint': {
                'name': 'ansible-lint',
                'options': {
                    'foo': 'bar'
                }
            }
        }]
    }],
    indirect=['config_instance'])
def test_lint_options_property_handles_lint_options(config_instance):
    assert {'foo': 'bar'} == config_instance.lint_options


@pytest.mark.parametrize(
    'config_instance', [{
        'args': {
            'debug': True
        },
    }],
    indirect=['config_instance'])
def test_lint_options_property_handles_cli_args(config_instance):
    # Does nothing.  The `ansible-galaxy` command does not support
    # a `debug` flag.
    assert {} == config_instance.lint_options


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_platforms_property(config_instance):
    assert [] == config_instance.platforms


@pytest.mark.parametrize(
    'config_instance', [{
        'configs': [{
            'platforms': [
                {
                    'name': 'instance-1',
                    'groups': ['foo', 'bar'],
                },
                {
                    'name': 'instance-2',
                    'groups': ['baz'],
                },
            ]
        }]
    }],
    indirect=['config_instance'])
def test_platform_groups_property(config_instance):
    x = {
        'bar': ['instance-1-default'],
        'foo': ['instance-1-default'],
        'baz': ['instance-2-default']
    }

    assert x == config_instance.platform_groups


@pytest.mark.parametrize(
    'config_instance', [{
        'configs': [{
            'platforms': [
                {
                    'name': 'instance-1',
                    'groups': ['foo', 'bar'],
                },
                {
                    'name': 'instance-2',
                },
            ]
        }]
    }],
    indirect=['config_instance'])
def test_platform_groups_property_handles_missing_group(config_instance):
    x = {'foo': ['instance-1-default'], 'bar': ['instance-1-default']}

    assert x == config_instance.platform_groups


@pytest.mark.parametrize(
    'config_instance', [{
        'configs': [{
            'platforms': [
                {
                    'name': 'instance-1',
                },
                {
                    'name': 'instance-2',
                },
            ]
        }]
    }],
    indirect=['config_instance'])
def test_platform_groups_property_handles_no_groups(config_instance):
    assert {} == config_instance.platform_groups


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_provisioner_property(config_instance):
    assert isinstance(config_instance.provisioner, ansible.Ansible)


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_provisioner_name_property(config_instance):
    assert 'ansible' == config_instance.provisioner_name


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_provisioner_options_property(config_instance):
    x = {
        'ask_sudo_pass': False,
        'ask_vault_pass': False,
        'config_file': 'ansible.cfg',
        'diff': True,
        'host_key_checking': False,
        'inventory_file': 'ansible_inventory',
        'limit': 'all',
        'playbook': 'playbook.yml',
        'raw_ssh_args': [
            '-o UserKnownHostsFile=/dev/null', '-o IdentitiesOnly=yes',
            '-o ControlMaster=auto', '-o ControlPersist=60s'
        ],
        'sudo': True,
        'sudo_user': False,
        'tags': False,
        'timeout': 30,
        'vault_password_file': False,
        'verbose': False
    }

    assert x == config_instance.provisioner_options


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_scenario_name_property(config_instance):
    assert 'default' == config_instance.scenario_name


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_scenario_setup_property(config_instance):
    x = os.path.join(config_instance.scenario_directory, 'create.yml')

    assert x == config_instance.scenario_setup


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_scenario_converge_property(config_instance):
    x = os.path.join(config_instance.scenario_directory, 'playbook.yml')

    assert x == config_instance.scenario_converge


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_scenario_teardown_property(config_instance):
    x = os.path.join(config_instance.scenario_directory, 'destroy.yml')

    assert x == config_instance.scenario_teardown


@pytest.mark.parametrize(
    'config_instance', [{
        'molecule_file': config.molecule_file('/foo/bar/molecule/default/')
    }],
    indirect=['config_instance'])
def test_scenario_directory_property(config_instance):
    assert '/foo/bar/molecule/default' == config_instance.scenario_directory


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_verifier_property(config_instance):
    assert isinstance(config_instance.verifier, testinfra.Testinfra)


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_verifier_name_property(config_instance):
    assert 'testinfra' == config_instance.verifier_name


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_verifier_enabled_property(config_instance):
    assert config_instance.verifier_enabled


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_verifier_directory_property(config_instance):
    parts = config_instance.verifier_directory.split(os.path.sep)
    assert 'tests' == parts[-1]


@pytest.mark.parametrize('config_instance', [{}], indirect=['config_instance'])
def test_verifier_options_property(config_instance):
    assert {'connection': 'docker'} == config_instance.verifier_options


@pytest.mark.parametrize(
    'config_instance', [{
        'configs': [{
            'verifier': {
                'name': 'testinfra',
                'options': {
                    'foo': 'bar'
                }
            }
        }]
    }],
    indirect=['config_instance'])
def test_verifier_options_property_handles_verifier_options(config_instance):
    x = {'connection': 'docker', 'foo': 'bar'}

    assert x == config_instance.verifier_options


@pytest.mark.parametrize(
    'config_instance', [{
        'args': {
            'debug': True
        },
    }],
    indirect=['config_instance'])
def test_verifier_options_property_handles_cli_args(config_instance):
    assert {
        'debug': True,
        'connection': 'docker'
    } == config_instance.verifier_options


@pytest.mark.parametrize(
    'config_instance', [{
        'configs': ['project_config_data']
    }],
    indirect=['config_instance'])
def test_combine_default_and_project_dicts(config_instance):
    c = config_instance.config

    assert 'project-override' == c['driver']['name']
    assert {} == c['driver']['options']


@pytest.mark.parametrize(
    'config_instance', [{
        'configs': ['project_config_data', 'local_config_data']
    }],
    indirect=['config_instance'])
def test_combine_default_project_and_local_dicts(config_instance):
    c = config_instance.config

    assert 'local-override' == c['driver']['name']
    return {'foo': 'bar'} == c['driver']['options']


def test_merge_dicts():
    # example taken from python-anyconfig/anyconfig/__init__.py
    a = {'b': [{'c': 0}, {'c': 2}], 'd': {'e': 'aaa', 'f': 3}}
    b = {'a': 1, 'b': [{'c': 3}], 'd': {'e': 'bbb'}}
    x = {'a': 1, 'b': [{'c': 3}], 'd': {'e': "bbb", 'f': 3}}

    result = config.merge_dicts(a, b)
    assert x == result


def test_molecule_directory():
    assert '/foo/molecule' == config.molecule_directory('/foo')


def test_molecule_ephemeral_directory():
    assert '/foo/.molecule' == config.molecule_ephemeral_directory('/foo')


def test_molecule_file():
    assert '/foo/molecule.yml' == config.molecule_file('/foo')

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
from molecule import provisioner
from molecule import scenario
from molecule.dependency import ansible_galaxy
from molecule.driver import docker
from molecule.lint import ansible_lint
from molecule.verifier import testinfra


@pytest.fixture()
def project_config_data():
    return {'driver': {'name': 'project-override'}}


@pytest.fixture()
def local_config_data():
    return {'driver': {'name': 'local-override', 'options': {'foo': 'bar'}}}


@pytest.mark.parametrize(
    'config_instance', [{
        'molecule_file': config.molecule_file('/foo/bar/molecule/default')
    }],
    indirect=['config_instance'])
def test_molecule_file_private_member(config_instance):
    x = '/foo/bar/molecule/default/molecule.yml'

    assert x == config_instance.molecule_file


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


def test_driver_property(config_instance):
    assert isinstance(config_instance.driver, docker.Docker)


def test_lint_property(config_instance):
    assert isinstance(config_instance.lint, ansible_lint.AnsibleLint)


@pytest.mark.parametrize(
    'config_instance', [{
        'configs': [{
            'platforms': []
        }]
    }],
    indirect=['config_instance'])
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


def test_provisioner_property(config_instance):
    assert isinstance(config_instance.provisioner, provisioner.Ansible)


def test_scenario_property(config_instance):
    assert isinstance(config_instance.scenario, scenario.Scenario)


def test_verifier_property(config_instance):
    assert isinstance(config_instance.verifier, testinfra.Testinfra)


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


def test_merge_dicts(config_instance):
    # example taken from python-anyconfig/anyconfig/__init__.py
    a = {'b': [{'c': 0}, {'c': 2}], 'd': {'e': 'aaa', 'f': 3}}
    b = {'a': 1, 'b': [{'c': 3}], 'd': {'e': 'bbb'}}
    x = {'a': 1, 'b': [{'c': 3}], 'd': {'e': "bbb", 'f': 3}}

    assert x == config_instance.merge_dicts(a, b)


def test_molecule_directory():
    assert '/foo/molecule' == config.molecule_directory('/foo')


def test_molecule_ephemeral_directory():
    assert '/foo/.molecule' == config.molecule_ephemeral_directory('/foo')


def test_molecule_file():
    assert '/foo/molecule.yml' == config.molecule_file('/foo')

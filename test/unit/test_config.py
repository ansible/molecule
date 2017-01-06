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


@pytest.fixture
def config_data():
    return {}


@pytest.fixture
def config_instance(platforms_data, molecule_file, config_data):
    configs = [platforms_data, config_data]

    return config.Config(molecule_file, configs=configs)


def test_molecule_file_private_member(platforms_data, config_data):
    configs = [platforms_data, config_data]
    c = config.Config('/foo/bar/default/molecule.yml', configs=configs)
    x = '/foo/bar/default/molecule.yml'

    assert x == c.molecule_file


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


def test_platforms_property(config_instance):
    x = [{
        'groups': ['foo', 'bar'],
        'name': 'instance-1'
    }, {
        'groups': ['baz', 'foo'],
        'name': 'instance-2'
    }]

    assert x == config_instance.platforms


def test_provisioner_property(config_instance):
    assert isinstance(config_instance.provisioner, provisioner.Ansible)


def test_scenario_property(config_instance):
    assert isinstance(config_instance.scenario, scenario.Scenario)


def test_verifier_property(config_instance):
    assert isinstance(config_instance.verifier, testinfra.Testinfra)


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


def test_molecule_directory():
    assert '/foo/molecule' == config.molecule_directory('/foo')


def test_molecule_ephemeral_directory():
    assert '/foo/.molecule' == config.molecule_ephemeral_directory('/foo')


def test_molecule_file():
    assert '/foo/molecule.yml' == config.molecule_file('/foo')

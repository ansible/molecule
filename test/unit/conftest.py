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

import functools
import os

import m9dicts
import pytest

from molecule import util
from molecule import config


@pytest.helpers.register
def write_molecule_file(filename, data):
    data = m9dicts.convert_to(data)

    util.write_file(filename, util.safe_dump(data))


@pytest.helpers.register
def os_split(s):
    rest, tail = os.path.split(s)
    if rest in ('', os.path.sep):
        return tail,
    return os_split(rest) + (tail, )


@pytest.fixture
def molecule_dependency_galaxy_section_data():
    return {'dependency': {'name': 'galaxy'}, }


@pytest.fixture
def molecule_driver_section_data():
    return {'driver': {'name': 'docker', }, }


@pytest.fixture
def molecule_lint_section_data():
    return {'lint': {'name': 'ansible-lint'}, }


@pytest.fixture
def molecule_platforms_section_data():
    return {
        'platforms': [{
            'name': 'instance-1',
            'groups': ['foo', 'bar'],
            'children': ['child1'],
        }, {
            'name': 'instance-2',
            'groups': ['baz', 'foo'],
            'children': ['child2'],
        }],
    }


@pytest.fixture
def molecule_provisioner_section_data():
    return {'provisioner': {'name': 'ansible'}, }


@pytest.fixture
def molecule_scenario_section_data():
    return {'scenario': {'name': 'default'}, }


@pytest.fixture
def molecule_verifier_section_data():
    return {'verifier': {'name': 'testinfra'}, }


@pytest.fixture
def molecule_data(
        molecule_dependency_galaxy_section_data, molecule_driver_section_data,
        molecule_lint_section_data, molecule_platforms_section_data,
        molecule_provisioner_section_data, molecule_scenario_section_data,
        molecule_verifier_section_data):

    fixtures = [
        molecule_dependency_galaxy_section_data, molecule_driver_section_data,
        molecule_lint_section_data, molecule_platforms_section_data,
        molecule_provisioner_section_data, molecule_scenario_section_data,
        molecule_verifier_section_data
    ]

    return functools.reduce(lambda x, y: config.merge_dicts(x, y), fixtures)


@pytest.fixture
def molecule_directory(temp_dir):
    return config.molecule_directory(temp_dir.strpath)


@pytest.fixture
def molecule_scenario_directory(molecule_directory):
    path = os.path.join(molecule_directory, 'default')
    if not os.path.isdir(path):
        os.makedirs(path)

    return path


@pytest.fixture
def molecule_ephemeral_directory(molecule_scenario_directory):
    path = config.molecule_ephemeral_directory(molecule_scenario_directory)
    if not os.path.isdir(path):
        os.makedirs(path)


@pytest.fixture
def molecule_file(molecule_scenario_directory, molecule_ephemeral_directory):
    return config.molecule_file(molecule_scenario_directory)


@pytest.fixture
def config_instance(molecule_file, molecule_data):
    pytest.helpers.write_molecule_file(molecule_file, molecule_data)

    return config.Config(molecule_file)


# Mocks


@pytest.fixture
def patched_ansible_playbook(mocker):
    m = mocker.patch('molecule.ansible_playbook.AnsiblePlaybook')
    m.return_value.execute.return_value = 'patched-ansible-playbook-stdout'

    return m


@pytest.fixture
def patched_print_debug(mocker):
    return mocker.patch('molecule.util.print_debug')


@pytest.fixture
def patched_logger_info(mocker):
    return mocker.patch('logging.Logger.info')


@pytest.fixture
def patched_logger_warn(mocker):
    return mocker.patch('logging.Logger.warn')


@pytest.fixture
def patched_logger_error(mocker):
    return mocker.patch('logging.Logger.error')


@pytest.fixture
def patched_logger_critical(mocker):
    return mocker.patch('logging.Logger.critical')


@pytest.fixture
def patched_logger_success(mocker):
    return mocker.patch('molecule.logger.CustomLogger.success')


@pytest.fixture
def patched_run_command(mocker):
    m = mocker.patch('molecule.util.run_command')
    m.return_value = mocker.Mock(stdout='patched-run-command-stdout')

    return m

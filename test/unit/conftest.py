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

from molecule import util
from molecule import config


@pytest.helpers.register
def create_molecule_file(molecule_file, config):
    util.write_file(molecule_file, util.safe_dump(config.config))


@pytest.helpers.register
def os_split(s):
    rest, tail = os.path.split(s)
    if rest in ('', os.path.sep):
        return tail,
    return os_split(rest) + (tail, )


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
def molecule_file(molecule_scenario_directory):
    return config.molecule_file(molecule_scenario_directory)


@pytest.fixture
def platforms_data():
    return {
        'platforms': [{
            'name': 'instance-1',
            'groups': ['foo', 'bar'],
            'children': ['child1'],
        }, {
            'name': 'instance-2',
            'groups': ['baz', 'foo'],
            'children': ['child2'],
        }]
    }


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
def patched_print_error(mocker):
    return mocker.patch('molecule.util.print_error')


@pytest.fixture
def patched_print_info(mocker):
    return mocker.patch('molecule.util.print_info')


@pytest.fixture
def patched_print_success(mocker):
    return mocker.patch('molecule.util.print_success')


@pytest.fixture
def patched_run_command(mocker):
    m = mocker.patch('molecule.util.run_command')
    m.return_value = mocker.Mock(stdout='patched-run-command-stdout')

    return m

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
import yaml

from molecule import config


def create_scenario_directory(basedir):
    molecule_directory = config.molecule_directory(basedir)
    scenario_directory = os.path.join(molecule_directory, 'default')
    os.makedirs(scenario_directory)

    return scenario_directory


def create_molecule_file(molecule_file, data):
    with open(molecule_file, 'w') as outfile:
        outfile.write(yaml.dump(data))


@pytest.helpers.register
def os_split(s):
    rest, tail = os.path.split(s)
    if rest in ('', os.path.sep):
        return tail,
    return os_split(rest) + (tail, )


@pytest.fixture
def platforms_data():
    return {
        'platforms': [{
            'name': 'instance-1',
            'groups': ['foo', 'bar']
        }, {
            'name': 'instance-2',
            'groups': ['baz', 'foo']
        }]
    }


@pytest.fixture()
def config_instance(temp_dir, platforms_data, request):
    configs = []
    scenario_directory = create_scenario_directory(temp_dir.strpath)
    molecule_file = config.molecule_file(scenario_directory)
    factory_data = {
        'molecule_file': molecule_file,
        'args': {},
        'command_args': {},
    }
    params = {}
    # handle parameterized tests
    if hasattr(request, 'param'):
        params = request.param
        for fixture in params.get('configs', []):
            # merge platform data onto provided dict
            if isinstance(fixture, dict):
                platforms_data.update(fixture)
                configs.append(platforms_data)
            # merge platform data onto fixture lookup data
            else:
                fixture_data = request.getfuncargvalue(fixture)
                platforms_data.update(fixture_data)
                configs.append(platforms_data)
        params['configs'] = configs
        factory_data['configs'] = configs
    # non-parameterized
    else:
        factory_data['configs'] = [platforms_data]

    factory_data.update(params)
    create_molecule_file(molecule_file, factory_data)

    return config.Config(**factory_data)


# Mocks


@pytest.fixture
def patched_ansible_playbook(mocker):
    return mocker.patch('molecule.ansible_playbook.AnsiblePlaybook')


@pytest.fixture
def patched_ansible_playbook_execute(mocker):
    return mocker.patch('molecule.ansible_playbook.AnsiblePlaybook.execute')


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
    return mocker.patch('molecule.util.run_command')

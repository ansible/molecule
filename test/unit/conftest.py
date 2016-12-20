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


@pytest.helpers.register
def os_split(s):
    rest, tail = os.path.split(s)
    if rest in ('', os.path.sep):
        return tail,
    return os_split(rest) + (tail, )


@pytest.fixture
def create_scenario(temp_dir):
    molecule_directory = config.molecule_directory(temp_dir.strpath)
    scenario_directory = os.path.join(molecule_directory, 'default')
    molecule_file = config.molecule_file(scenario_directory)
    os.makedirs(scenario_directory)

    d = {
        'platforms': [{
            'name': 'instance-1',
            'groups': ['foo', 'bar']
        }, {
            'name': 'instance-2',
            'groups': ['baz', 'foo']
        }]
    }
    with open(molecule_file, 'w') as outfile:
        outfile.write(yaml.dump(d))

    return molecule_file


@pytest.fixture()
def config_instance(create_scenario):
    molecule_file = create_scenario
    configs = [(yaml.load(open(molecule_file, 'r')))]

    return config.Config(molecule_file, configs=configs)


# Mocks


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

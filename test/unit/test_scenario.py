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
from molecule import scenario


@pytest.fixture
def scenario_data():
    return {}


@pytest.fixture
def scenario_instance(scenario_data):
    molecule_file = config.molecule_file('/foo/bar/molecule/default')
    c = config.Config(molecule_file, configs=[scenario_data])

    return scenario.Scenario(c)


def test_name_property(scenario_instance):
    assert 'default' == scenario_instance.name


def test_setup_property(scenario_instance):
    x = os.path.join(scenario_instance.directory, 'create.yml')

    assert x == scenario_instance.setup


def test_converge_property(scenario_instance):
    x = os.path.join(scenario_instance.directory, 'playbook.yml')

    assert x == scenario_instance.converge


def test_teardown_property(scenario_instance):
    x = os.path.join(scenario_instance.directory, 'destroy.yml')

    assert x == scenario_instance.teardown


def test_directory_property(scenario_instance):
    assert '/foo/bar/molecule/default' == scenario_instance.directory


def test_converge_sequence_property(scenario_instance):
    x = ['create', 'converge']

    assert x == scenario_instance.converge_sequence


def test_test_sequence_property(scenario_instance):
    x = ['destroy', 'create', 'converge', 'lint', 'verify', 'destroy']

    assert x == scenario_instance.test_sequence


def test_idempotence_sequence_property(scenario_instance):
    x = ['create', 'converge', 'idempotence']

    assert x == scenario_instance.idempotence_sequence

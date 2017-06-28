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

from molecule import scenario


@pytest.fixture
def scenario_instance(config_instance):
    return scenario.Scenario(config_instance)


def test_name_property(scenario_instance):
    assert 'default' == scenario_instance.name


def test_directory_property(molecule_scenario_directory_fixture,
                            scenario_instance):
    assert molecule_scenario_directory_fixture == scenario_instance.directory


def test_ephemeral_directory_property(molecule_scenario_directory_fixture,
                                      scenario_instance):
    x = os.path.join(molecule_scenario_directory_fixture, '.molecule')

    assert x == scenario_instance.ephemeral_directory


def test_check_sequence_property(scenario_instance):
    x = ['destroy', 'create', 'converge', 'check', 'destroy']

    assert x == scenario_instance.check_sequence


def test_converge_sequence_property(scenario_instance):
    x = [
        'create',
        'converge',
    ]

    assert x == scenario_instance.converge_sequence


def test_test_sequence_property(scenario_instance):
    x = [
        'destroy',
        'dependency',
        'syntax',
        'create',
        'converge',
        'idempotence',
        'lint',
        'destruct',
        'verify',
        'destroy',
    ]

    assert x == scenario_instance.test_sequence

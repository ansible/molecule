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

from molecule import config
from molecule import state
from molecule import util


@pytest.fixture
def state_instance(config_instance):
    return state.State(config_instance)


def test_state_file_property(state_instance):
    x = os.path.join(state_instance._config.scenario.ephemeral_directory,
                     'state.yml')

    assert x == state_instance.state_file


def test_converged(state_instance):
    assert not state_instance.converged


def test_created(state_instance):
    assert not state_instance.created


def test_driver(state_instance):
    assert not state_instance.driver


def test_prepared(state_instance):
    assert not state_instance.prepared


def test_reset(state_instance):
    assert not state_instance.converged

    state_instance.change_state('converged', True)
    assert state_instance.converged

    state_instance.reset()
    assert not state_instance.converged


def test_reset_persists(state_instance):
    assert not state_instance.converged

    state_instance.change_state('converged', True)
    assert state_instance.converged

    state_instance.reset()
    assert not state_instance.converged

    d = util.safe_load_file(state_instance.state_file)
    assert not d.get('converged')


def test_change_state_converged(state_instance):
    state_instance.change_state('converged', True)

    assert state_instance.converged


def test_change_state_created(state_instance):
    state_instance.change_state('created', True)

    assert state_instance.created


def test_change_state_driver(state_instance):
    state_instance.change_state('driver', 'foo')

    assert 'foo' == state_instance.driver


def test_change_state_prepared(state_instance):
    state_instance.change_state('prepared', True)

    assert state_instance.prepared


def test_change_state_raises(state_instance):
    with pytest.raises(state.InvalidState):
        state_instance.change_state('invalid-state', True)


def test_get_data_loads_existing_state_file(temp_dir, molecule_data):
    molecule_directory = pytest.helpers.molecule_directory()
    scenario_directory = os.path.join(molecule_directory, 'default')
    molecule_file = pytest.helpers.get_molecule_file(scenario_directory)
    ephemeral_directory = pytest.helpers.molecule_ephemeral_directory()
    state_file = os.path.join(ephemeral_directory, 'state.yml')

    os.makedirs(ephemeral_directory)

    data = {
        'converged': False,
        'created': True,
        'driver': None,
        'prepared': None,
    }
    util.write_file(state_file, util.safe_dump(data))

    pytest.helpers.write_molecule_file(molecule_file, molecule_data)
    c = config.Config(molecule_file)
    s = state.State(c)

    assert not s.converged
    assert s.created
    assert not s.driver
    assert not s.prepared

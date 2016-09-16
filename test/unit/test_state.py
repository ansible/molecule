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

import pytest
import yaml

from molecule import state


@pytest.fixture()
def state_instance_with_data(state_path_with_data):
    return state.State(state_file=state_path_with_data)


@pytest.fixture()
def state_instance_without_data(state_path_without_data):
    return state.State(state_file=state_path_without_data)


def test_converged(state_instance_without_data):
    assert not state_instance_without_data.converged


def test_created(state_instance_without_data):
    assert not state_instance_without_data.created


def test_customconf(state_instance_without_data):
    assert not state_instance_without_data.customconf


def test_default_platform(state_instance_without_data):
    assert not state_instance_without_data.default_platform


def test_default_provider(state_instance_without_data):
    assert not state_instance_without_data.default_provider


def test_driver(state_instance_without_data):
    assert not state_instance_without_data.driver


def test_hosts(state_instance_without_data):
    assert {} == state_instance_without_data.hosts


def test_installed_deps(state_instance_without_data):
    assert not state_instance_without_data.installed_deps


def test_multiple_platforms(state_instance_without_data):
    assert not state_instance_without_data.multiple_platforms


def test_reset(state_instance_without_data):
    assert not state_instance_without_data.created

    state_instance_without_data.change_state('created', True)
    assert state_instance_without_data.created

    state_instance_without_data.reset()
    assert not state_instance_without_data.created


def test_reset_persists(state_instance_without_data):
    assert not state_instance_without_data.created

    state_instance_without_data.change_state('created', True)
    assert state_instance_without_data.created

    state_instance_without_data.reset()
    assert not state_instance_without_data.created

    with open(state_instance_without_data._state_file) as stream:
        d = yaml.safe_load(stream)

        assert not d.get('created')


def test_change_state(state_instance_without_data):
    state_instance_without_data.change_state('created', True)

    assert state_instance_without_data.created


def test_change_state_raises(state_instance_without_data):
    with pytest.raises(state.InvalidState):
        state_instance_without_data.change_state('invalid-state', True)


def test_change_state_persists(state_instance_without_data):
    assert not state_instance_without_data.created

    state_instance_without_data.change_state('created', True)
    assert state_instance_without_data.created

    with open(state_instance_without_data._state_file) as stream:
        d = yaml.safe_load(stream)

        assert d.get('created')


def test_get_data():
    # Already tested through the property tests
    pass


def test_get_data_loads_existing_state_file(state_instance_with_data):

    assert state_instance_with_data.created

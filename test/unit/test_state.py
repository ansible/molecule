#  Copyright (c) 2015-2016 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

import os

import pytest
import yaml

from molecule import state


@pytest.fixture()
def state_instance(state_path):
    return state.State(state_file=state_path)


def test_converged(state_instance):
    assert not state_instance.converged


def test_created(state_instance):
    assert not state_instance.created


def test_customconf(state_instance):
    assert not state_instance.customconf


def test_default_platform(state_instance):
    assert not state_instance.default_platform


def test_default_provider(state_instance):
    assert not state_instance.default_provider


def test_hosts(state_instance):
    assert not state_instance.hosts


def test_installed_deps(state_instance):
    assert not state_instance.installed_deps


def test_multiple_platforms(state_instance):
    assert not state_instance.multiple_platforms


def test_reset(state_instance):
    assert not state_instance.created

    state_instance.change_state('created', True)
    assert state_instance.created

    state_instance.reset()
    assert not state_instance.created


def test_reset_persists(state_instance):
    assert not state_instance.created

    state_instance.change_state('created', True)
    assert state_instance.created

    state_instance.reset()
    assert not state_instance.created

    with open(state_instance._state_file) as stream:
        d = yaml.safe_load(stream)

        assert not d.get('created')


def test_change_state(state_instance):
    state_instance.change_state('created', True)

    assert state_instance.created


def test_change_state_raises(state_instance):
    with pytest.raises(state.InvalidState):
        state_instance.change_state('invalid-state', True)


def test_change_state_persists(state_instance):
    assert not state_instance.created

    state_instance.change_state('created', True)
    assert state_instance.created

    with open(state_instance._state_file) as stream:
        d = yaml.safe_load(stream)

        assert d.get('created')


def test_get_data():
    # Already tested through the property tests
    pass


def test_get_data_loads_existing_state_file():
    d = os.path.dirname(os.path.abspath(__file__))
    f = os.path.join(d, 'support', 'state.yml')
    s = state.State(state_file=f)

    assert 'test' == s.created

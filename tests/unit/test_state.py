#  Copyright (c) 2015-2018 Cisco Systems, Inc.  # noqa: D100
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
from __future__ import annotations

import os

from typing import TYPE_CHECKING

import pytest

from molecule import config, state, util


if TYPE_CHECKING:
    from typing import Any


@pytest.fixture
def _instance(config_instance: config.Config) -> state.State:
    return state.State(config_instance)


def test_state_file_property(_instance: state.State) -> None:  # noqa: PT019, D103
    x = os.path.join(_instance._config.scenario.ephemeral_directory, "state.yml")  # noqa: PTH118

    assert x == _instance.state_file


def test_converged(_instance: state.State) -> None:  # noqa: PT019, D103
    assert not _instance.converged


def test_created(_instance: state.State) -> None:  # noqa: PT019, D103
    assert not _instance.created


def test_state_driver(_instance: state.State) -> None:  # noqa: PT019, D103
    assert not _instance.driver


def test_prepared(_instance: state.State) -> None:  # noqa: PT019, D103
    assert not _instance.prepared


def test_reset(_instance: state.State) -> None:  # noqa: PT019, D103
    assert not _instance.converged

    _instance.change_state("converged", True)  # noqa: FBT003
    assert _instance.converged

    _instance.reset()
    assert not _instance.converged


def test_reset_persists(_instance: state.State) -> None:  # noqa: PT019, D103
    assert not _instance.converged

    _instance.change_state("converged", True)  # noqa: FBT003
    assert _instance.converged

    _instance.reset()
    assert not _instance.converged

    d = util.safe_load_file(_instance.state_file)
    assert not d.get("converged")


def test_change_state_converged(_instance: state.State) -> None:  # noqa: PT019, D103
    _instance.change_state("converged", True)  # noqa: FBT003

    assert _instance.converged


def test_change_state_created(_instance: state.State) -> None:  # noqa: PT019, D103
    _instance.change_state("created", True)  # noqa: FBT003

    assert _instance.created


def test_change_state_driver(_instance: state.State) -> None:  # noqa: PT019, D103
    _instance.change_state("driver", "foo")

    assert _instance.driver == "foo"


def test_change_state_prepared(_instance: state.State) -> None:  # noqa: PT019, D103
    _instance.change_state("prepared", True)  # noqa: FBT003

    assert _instance.prepared


def test_change_state_raises(_instance: state.State) -> None:  # noqa: PT019, D103
    with pytest.raises(state.InvalidState):
        _instance.change_state("invalid-state", True)  # noqa: FBT003


def test_get_data_loads_existing_state_file(  # noqa: D103
    _instance: state.State,  # noqa: PT019
    molecule_data: dict[str, Any],
    config_instance: config.Config,
) -> None:
    data = {"converged": False, "created": True, "driver": None, "prepared": None}
    util.write_file(_instance._state_file, util.safe_dump(data))

    s = state.State(config_instance)

    assert not s.converged
    assert s.created
    assert not s.driver
    assert not s.prepared

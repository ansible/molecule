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

from pathlib import Path
from typing import TYPE_CHECKING

import click
import pytest

from molecule import config, state, util


if TYPE_CHECKING:
    from typing import Any

    from pytest_mock import MockerFixture


@pytest.fixture
def _instance(config_instance: config.Config) -> state.State:
    """Build a State instance from the config fixture.

    Args:
        config_instance: Instance of Config.

    Returns:
        A molecule State bound to config_instance.
    """
    return state.State(config_instance)


def test_state_file_property(_instance: state.State) -> None:  # noqa: PT019
    """Without shared_state the state file resolves under the scenario's ephemeral dir.

    Args:
        _instance: A molecule State instance.
    """
    x = os.path.join(_instance._config.scenario.ephemeral_directory, "state.yml")  # noqa: PTH118

    assert x == _instance.state_file


def test_shared_state_state_file_at_shared_root(
    _instance: state.State,  # noqa: PT019
) -> None:
    """Under shared_state the state file resolves to the shared root, not a scenario dir.

    Args:
        _instance: A molecule State instance.
    """
    _instance._config.config_data["shared_state"] = True
    scenario = _instance._config.scenario
    expected = Path(scenario.shared_ephemeral_directory) / "state.yml"

    assert _instance._get_state_file() == expected


def test_shared_state_env_directory_places_every_path_in_it(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """With MOLECULE_EPHEMERAL_DIRECTORY set, shared_state uses that one directory for everything.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        tmp_path: Pytest tmp_path fixture.
    """
    one_directory = tmp_path / "one"
    monkeypatch.setenv("MOLECULE_EPHEMERAL_DIRECTORY", str(one_directory))
    monkeypatch.setenv("ANSIBLE_HOME", str(tmp_path / ".ansible"))
    monkeypatch.chdir(tmp_path)
    # Config.__init__ caches the scenario and state paths, so shared_state
    # has to be in force before construction: give it the way the CLI does.
    with click.Context(click.Command("test")) as ctx:
        ctx.set_parameter_source("shared_state", click.core.ParameterSource.COMMANDLINE)
        cfg = config.Config("", command_args={"shared_state": True})

    assert cfg.shared_state is True
    assert Path(cfg.scenario.ephemeral_directory) == one_directory
    assert Path(cfg.scenario.shared_ephemeral_directory) == one_directory
    assert Path(cfg.state.state_file).parent == one_directory
    assert Path(cfg.driver.instance_config).parent == one_directory


def test_converged(_instance: state.State) -> None:  # noqa: PT019
    """A fresh State reports converged as False.

    Args:
        _instance: A molecule State instance.
    """
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


def test_change_state_raises(_instance: state.State) -> None:  # noqa: PT019
    """change_state rejects an unknown state key.

    Args:
        _instance: A molecule State instance.
    """
    with pytest.raises(state.InvalidState):
        _instance.change_state("invalid-state", True)  # noqa: FBT003


def test_change_state_does_not_clobber_a_sibling_states_write(
    _instance: state.State,  # noqa: PT019
    config_instance: config.Config,
) -> None:
    """change_state merges into state.yml on disk instead of overwriting a sibling's write.

    Args:
        _instance: A molecule State instance.
        config_instance: Instance of Config.
    """
    # `_instance` is constructed first, so its in-memory snapshot predates the
    # write below, the same way a scenario's own State object under
    # shared_state is constructed before default_config's create step runs.
    creator = state.State(config_instance)
    creator.change_state("created", True)  # noqa: FBT003

    _instance.change_state("prepared", True)  # noqa: FBT003

    on_disk = util.safe_load_file(_instance.state_file)
    assert on_disk["created"] is True
    assert on_disk["prepared"] is True


def test_write_state_file_routes_through_atomic_write(
    config_instance: config.Config,
    mocker: MockerFixture,
) -> None:
    """change_state must persist state.yml via util.atomic_write_file (#4667/#4666).

    State.__init__ already writes through util.atomic_write_file, so the spy
    count is taken after construction. Asserts that change_state adds exactly
    one util.atomic_write_file call, that the call targets the state file, and
    that the state file's inode changes across the write, which an in-place
    write_text would keep and a mkstemp-then-replace changes.

    Args:
        config_instance: Instance of Config.
        mocker: pytest-mock fixture.
    """
    atomic_spy = mocker.spy(util, "atomic_write_file")

    s = state.State(config_instance)
    calls_after_init = atomic_spy.call_count
    before_inode = Path(s.state_file).stat().st_ino

    s.change_state("converged", True)  # noqa: FBT003

    assert atomic_spy.call_count == calls_after_init + 1
    assert atomic_spy.call_args.args[0] == s.state_file
    assert Path(s.state_file).stat().st_ino != before_inode


def test_get_data_loads_existing_state_file(
    _instance: state.State,  # noqa: PT019
    molecule_data: dict[str, Any],
    config_instance: config.Config,
) -> None:
    """A fresh State reads back the data already written to the state file.

    Args:
        _instance: A molecule State instance.
        molecule_data: Baseline molecule config data fixture.
        config_instance: Instance of Config.
    """
    data = {"converged": False, "created": True, "driver": None, "prepared": None}
    util.write_file(_instance._state_file, util.safe_dump(data))

    s = state.State(config_instance)

    assert not s.converged
    assert s.created
    assert not s.driver
    assert not s.prepared

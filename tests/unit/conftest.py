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

import copy
import os

from subprocess import CompletedProcess
from typing import TYPE_CHECKING, Any

import pytest

from molecule import config, util


if TYPE_CHECKING:
    from collections.abc import Generator, MutableMapping
    from pathlib import Path
    from unittest.mock import Mock

    from pytest_mock import MockerFixture


def write_molecule_file(file: Path, data: Any) -> None:  # noqa: ANN401, D103
    util.write_file(file, util.safe_dump(data))


def os_split(s: str) -> tuple[str, ...]:  # noqa: D103
    rest, tail = os.path.split(s)
    if rest in ("", os.path.sep):
        return (tail,)
    return (*os_split(rest), tail)


@pytest.fixture(name="molecule_data")
def fixture_molecule_data() -> dict[str, Any]:
    """Provide a default molecule data dictionary."""
    return {
        "dependency": {"name": "galaxy"},
        "driver": {"name": "default", "options": {"managed": True}},
        "platforms": [
            {"name": "instance-1", "groups": ["foo", "bar"], "children": ["child1"]},
            {"name": "instance-2", "groups": ["baz", "foo"], "children": ["child2"]},
        ],
        "provisioner": {
            "name": "ansible",
            "options": {"become": True},
            "config_options": {},
        },
        "scenario": {"name": "default"},
        "verifier": {"name": "ansible"},
    }


@pytest.fixture
def config_instance(
    monkeypatch: pytest.MonkeyPatch,
    molecule_data: dict[str, Any],
    request: pytest.FixtureRequest,
    test_cache_path: Path,
) -> Generator[config.Config, None, None]:
    """Return a Config instance.

    Merge molecule_data with any fixture that requests it and write the
    resulting data to a molecule file.  Return a Config instance with the
    molecule file path.

    Because the test_cache_path is gitignored, monkeypatch the filter_ignored_scenarios
    function to return the original list of scenarios.

    Args:
        monkeypatch: The pytest fixture for patching
        molecule_data: The pytest fixture for molecule data.
        request: The pytest fixture request
        test_cache_path: The test cache path

    Yields:
        config.Config: A Config instance
    """
    mdc: MutableMapping[str, Any] = copy.deepcopy(molecule_data)
    if hasattr(request, "param"):
        mdc = util.merge_dicts(molecule_data, request.getfixturevalue(request.param))

    monkeypatch.chdir(test_cache_path)
    molecule_dir = test_cache_path / "molecule" / "default"
    molecule_dir.mkdir(parents=True, exist_ok=True)
    molecule_file = molecule_dir / "molecule.yml"
    write_molecule_file(molecule_file, mdc)

    def _filter_ignored_scenarios(scenario_paths: list[str]) -> list[str]:
        return scenario_paths

    monkeypatch.setattr("molecule.command.base.filter_ignored_scenarios", _filter_ignored_scenarios)

    _environ = dict(os.environ)
    c = config.Config(str(molecule_file))
    c.command_args = {"subcommand": "test"}
    yield c
    # restore environ which can be modified by Config()
    os.environ.clear()
    os.environ.update(_environ)


# Mocks


@pytest.fixture
def patched_print_debug(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    return mocker.patch("molecule.util.print_debug")


@pytest.fixture
def patched_logger_info(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    return mocker.patch("logging.Logger.info")


@pytest.fixture
def patched_logger_debug(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    return mocker.patch("logging.Logger.debug")


@pytest.fixture
def patched_logger_error(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    return mocker.patch("logging.Logger.error")


@pytest.fixture
def patched_run_command(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    m = mocker.patch("molecule.app.App.run_command")
    m.return_value = CompletedProcess(
        args="foo",
        returncode=0,
        stdout="patched-run-command-stdout",
        stderr="",
    )

    return m


@pytest.fixture
def patched_ansible_converge(mocker: MockerFixture) -> Mock:  # noqa: D103
    m = mocker.patch("molecule.provisioner.ansible.Ansible.converge")
    m.return_value = "patched-ansible-converge-stdout"

    return m


@pytest.fixture
def patched_add_or_update_vars(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    return mocker.patch("molecule.provisioner.ansible.Ansible._add_or_update_vars")


@pytest.fixture
def patched_ansible_galaxy(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    return mocker.patch("molecule.dependency.ansible_galaxy.AnsibleGalaxy.execute")


@pytest.fixture
def patched_default_verifier(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    return mocker.patch("molecule.verifier.ansible.Ansible.execute")


@pytest.fixture
def patched_scenario_setup(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker.patch("molecule.config.Config.env")

    return mocker.patch("molecule.scenario.Scenario._setup")


@pytest.fixture
def patched_config_validate(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    return mocker.patch("molecule.config.Config._validate")

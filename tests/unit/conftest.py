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

import copy
import os
import shutil

from collections.abc import Generator
from pathlib import Path
from subprocess import CompletedProcess
from typing import Any
from unittest.mock import Mock
from uuid import uuid4

import pytest

from pytest_mock import MockerFixture

from molecule import config, util
from tests.conftest import (  # pylint:disable=C0411
    molecule_directory,
    molecule_ephemeral_directory,
    molecule_file,
    molecule_scenario_directory,
)


def write_molecule_file(filename: str, data: Any) -> None:  # noqa: ANN401, D103
    util.write_file(filename, util.safe_dump(data))


def os_split(s: str) -> tuple[str, ...]:  # noqa: D103
    rest, tail = os.path.split(s)
    if rest in ("", os.path.sep):
        return (tail,)
    return (*os_split(rest), tail)


@pytest.fixture()
def _molecule_dependency_galaxy_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202, PT005
    return {"dependency": {"name": "galaxy"}}


@pytest.fixture()
def _molecule_driver_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202, PT005
    return {"driver": {"name": "default", "options": {"managed": True}}}


@pytest.fixture()
def _molecule_platforms_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202, PT005
    return {
        "platforms": [
            {"name": "instance-1", "groups": ["foo", "bar"], "children": ["child1"]},
            {"name": "instance-2", "groups": ["baz", "foo"], "children": ["child2"]},
        ],
    }


@pytest.fixture()
def _molecule_provisioner_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202, PT005
    return {
        "provisioner": {
            "name": "ansible",
            "options": {"become": True},
            "config_options": {},
        },
    }


@pytest.fixture()
def _molecule_scenario_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202, PT005
    return {"scenario": {"name": "default"}}


@pytest.fixture()
def _molecule_verifier_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202, PT005
    return {"verifier": {"name": "ansible"}}


@pytest.fixture(name="molecule_data")
def fixture_molecule_data(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    _molecule_dependency_galaxy_section_data,  # noqa: ANN001
    _molecule_driver_section_data,  # noqa: ANN001
    _molecule_platforms_section_data,  # noqa: ANN001
    _molecule_provisioner_section_data,  # noqa: ANN001
    _molecule_scenario_section_data,  # noqa: ANN001
    _molecule_verifier_section_data,  # noqa: ANN001
):
    fixtures = [
        _molecule_dependency_galaxy_section_data,
        _molecule_driver_section_data,
        _molecule_platforms_section_data,
        _molecule_provisioner_section_data,
        _molecule_scenario_section_data,
        _molecule_verifier_section_data,
    ]

    merged_dict = {}
    for fixture in fixtures:
        merged_dict.update(fixture)

    return merged_dict


@pytest.fixture(name="molecule_directory_fixture")
def fixture_molecule_directory_fixture(temp_dir):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    return molecule_directory()


@pytest.fixture(name="molecule_scenario_directory_fixture")
def fixture_molecule_scenario_directory_fixture(molecule_directory_fixture):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    path = molecule_scenario_directory()
    if not os.path.isdir(path):  # noqa: PTH112
        os.makedirs(path, exist_ok=True)  # noqa: PTH103

    return path


@pytest.fixture(name="molecule_ephemeral_directory_fixture")
def fixture_molecule_ephemeral_directory_fixture(molecule_scenario_directory_fixture):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT004, ARG001, D103
    path = molecule_ephemeral_directory(str(uuid4()))
    if not os.path.isdir(path):  # noqa: PTH112
        os.makedirs(path, exist_ok=True)  # noqa: PTH103
    yield
    shutil.rmtree(str(Path(path).parent))


@pytest.fixture(name="molecule_file_fixture")
def fixture_molecule_file_fixture(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    molecule_scenario_directory_fixture,  # noqa: ANN001, ARG001
    molecule_ephemeral_directory_fixture,  # noqa: ANN001, ARG001
):
    return molecule_file()


@pytest.fixture()
def config_instance(  # type: ignore[no-untyped-def]  # noqa: D103
    molecule_file_fixture: str,
    molecule_data,  # noqa: ANN001
    request,  # noqa: ANN001
) -> Generator[config.Config, None, None]:
    mdc = copy.deepcopy(molecule_data)
    if hasattr(request, "param"):
        mdc = util.merge_dicts(mdc, request.getfixturevalue(request.param))
    write_molecule_file(molecule_file_fixture, mdc)

    _environ = dict(os.environ)
    c = config.Config(molecule_file_fixture)
    c.command_args = {"subcommand": "test"}
    yield c
    # restore environ which can be modified by Config()
    os.environ.clear()
    os.environ.update(_environ)


# Mocks


@pytest.fixture()
def patched_print_debug(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    return mocker.patch("molecule.util.print_debug")


@pytest.fixture()
def patched_logger_info(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    return mocker.patch("logging.Logger.info")


@pytest.fixture()
def patched_logger_debug(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    return mocker.patch("logging.Logger.debug")


@pytest.fixture()
def patched_logger_error(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    return mocker.patch("logging.Logger.error")


@pytest.fixture()
def patched_run_command(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    m = mocker.patch("molecule.util.run_command")
    m.return_value = CompletedProcess(
        args="foo",
        returncode=0,
        stdout="patched-run-command-stdout",
        stderr="",
    )

    return m


@pytest.fixture()
def patched_ansible_converge(mocker: MockerFixture) -> Mock:  # noqa: D103
    m = mocker.patch("molecule.provisioner.ansible.Ansible.converge")
    m.return_value = "patched-ansible-converge-stdout"

    return m


@pytest.fixture()
def patched_add_or_update_vars(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    return mocker.patch("molecule.provisioner.ansible.Ansible._add_or_update_vars")


@pytest.fixture()
def patched_ansible_galaxy(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    return mocker.patch("molecule.dependency.ansible_galaxy.AnsibleGalaxy.execute")


@pytest.fixture()
def patched_default_verifier(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    return mocker.patch("molecule.verifier.ansible.Ansible.execute")


@pytest.fixture()
def patched_scenario_setup(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    mocker.patch("molecule.config.Config.env")

    return mocker.patch("molecule.scenario.Scenario._setup")


@pytest.fixture()
def patched_config_validate(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    return mocker.patch("molecule.config.Config._validate")

#  Copyright (c) 2015-2018 Cisco Systems, Inc.
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
import functools
import os
import shutil
from pathlib import Path
from subprocess import CompletedProcess
from typing import Any, Generator, Tuple
from uuid import uuid4

import pytest

from molecule import config, util
from molecule.test.conftest import (
    molecule_directory,
    molecule_ephemeral_directory,
    molecule_file,
    molecule_scenario_directory,
)


def write_molecule_file(filename: str, data: Any) -> None:
    util.write_file(filename, util.safe_dump(data))


def os_split(s: str) -> Tuple[str, ...]:
    rest, tail = os.path.split(s)
    if rest in ("", os.path.sep):
        return (tail,)
    return os_split(rest) + (tail,)


@pytest.fixture
def _molecule_dependency_galaxy_section_data():
    return {"dependency": {"name": "galaxy"}}


@pytest.fixture
def _molecule_driver_section_data():
    return {"driver": {"name": "delegated", "options": {"managed": True}}}


@pytest.fixture
def _molecule_platforms_section_data():
    return {
        "platforms": [
            {"name": "instance-1", "groups": ["foo", "bar"], "children": ["child1"]},
            {"name": "instance-2", "groups": ["baz", "foo"], "children": ["child2"]},
        ]
    }


@pytest.fixture
def _molecule_provisioner_section_data():
    return {
        "provisioner": {
            "name": "ansible",
            "options": {"become": True},
            "config_options": {},
        }
    }


@pytest.fixture
def _molecule_scenario_section_data():
    return {"scenario": {"name": "default"}}


@pytest.fixture
def _molecule_verifier_section_data():
    return {"verifier": {"name": "ansible"}}


@pytest.fixture
def molecule_data(
    _molecule_dependency_galaxy_section_data,
    _molecule_driver_section_data,
    _molecule_platforms_section_data,
    _molecule_provisioner_section_data,
    _molecule_scenario_section_data,
    _molecule_verifier_section_data,
):

    fixtures = [
        _molecule_dependency_galaxy_section_data,
        _molecule_driver_section_data,
        _molecule_platforms_section_data,
        _molecule_provisioner_section_data,
        _molecule_scenario_section_data,
        _molecule_verifier_section_data,
    ]

    return functools.reduce(lambda x, y: util.merge_dicts(x, y), fixtures)


@pytest.fixture
def molecule_directory_fixture(temp_dir):
    return molecule_directory()


@pytest.fixture
def molecule_scenario_directory_fixture(molecule_directory_fixture):
    path = molecule_scenario_directory()
    if not os.path.isdir(path):
        os.makedirs(path)

    return path


@pytest.fixture
def molecule_ephemeral_directory_fixture(molecule_scenario_directory_fixture):
    path = molecule_ephemeral_directory(str(uuid4()))
    if not os.path.isdir(path):
        os.makedirs(path)
    yield
    shutil.rmtree(str(Path(path).parent))


@pytest.fixture
def molecule_file_fixture(
    molecule_scenario_directory_fixture, molecule_ephemeral_directory_fixture
):
    return molecule_file()


@pytest.fixture
def config_instance(
    molecule_file_fixture: str, molecule_data, request
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


@pytest.fixture
def patched_print_debug(mocker):
    return mocker.patch("molecule.util.print_debug")


@pytest.fixture
def patched_logger_info(mocker):
    return mocker.patch("logging.Logger.info")


@pytest.fixture
def patched_logger_debug(mocker):
    return mocker.patch("logging.Logger.debug")


@pytest.fixture
def patched_logger_warning(mocker):
    return mocker.patch("logging.Logger.warning")


@pytest.fixture
def patched_logger_error(mocker):
    return mocker.patch("logging.Logger.error")


@pytest.fixture
def patched_logger_critical(mocker):
    return mocker.patch("logging.Logger.critical")


@pytest.fixture
def patched_run_command(mocker):
    m = mocker.patch("molecule.util.run_command")
    m.return_value = CompletedProcess(
        args="foo", returncode=0, stdout="patched-run-command-stdout", stderr=""
    )

    return m


@pytest.fixture
def patched_ansible_converge(mocker):
    m = mocker.patch("molecule.provisioner.ansible.Ansible.converge")
    m.return_value = "patched-ansible-converge-stdout"

    return m


@pytest.fixture
def patched_add_or_update_vars(mocker):
    return mocker.patch("molecule.provisioner.ansible.Ansible._add_or_update_vars")


@pytest.fixture
def patched_ansible_galaxy(mocker):
    return mocker.patch("molecule.dependency.ansible_galaxy.AnsibleGalaxy.execute")


@pytest.fixture
def patched_default_verifier(mocker):
    return mocker.patch("molecule.verifier.ansible.Ansible.execute")


@pytest.fixture
def patched_scenario_setup(mocker):
    mocker.patch("molecule.config.Config.env")

    return mocker.patch("molecule.scenario.Scenario._setup")


@pytest.fixture
def patched_config_validate(mocker):
    return mocker.patch("molecule.config.Config._validate")

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

import os

import pytest
import sh

from molecule import util
from molecule.command.init import base
from molecule.model import schema_v3


class CommandBase(base.Base):
    """CommandBase Class."""

    pass


@pytest.fixture
def _base_class():
    return CommandBase


@pytest.fixture
def _instance(_base_class):
    return _base_class()


@pytest.fixture
def _command_args():
    return {
        "dependency_name": "galaxy",
        "driver_name": "docker",
        "provisioner_name": "ansible",
        "scenario_name": "default",
        "role_name": "test-role",
        "verifier_name": "ansible",
    }


@pytest.fixture
def _role_directory():
    return "."


@pytest.fixture
def _molecule_file(_role_directory):
    return os.path.join(
        _role_directory, "test-role", "molecule", "default", "molecule.yml"
    )


def test_valid(temp_dir, _molecule_file, _role_directory, _command_args, _instance):
    _instance._process_templates("molecule", _command_args, _role_directory)

    data = util.safe_load_file(_molecule_file)

    assert {} == schema_v3.validate(data)

    cmd = sh.yamllint.bake("-s", _molecule_file)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize("driver", [("docker")])
def test_drivers(
    driver, temp_dir, _molecule_file, _role_directory, _command_args, _instance
):
    _command_args["driver_name"] = driver
    _instance._process_templates("molecule", _command_args, _role_directory)

    data = util.safe_load_file(_molecule_file)

    assert {} == schema_v3.validate(data)

    cmd = sh.yamllint.bake("-s", _molecule_file)
    pytest.helpers.run_command(cmd)

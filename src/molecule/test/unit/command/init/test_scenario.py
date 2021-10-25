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

from molecule.command.init import scenario


@pytest.fixture
def _command_args():
    return {
        "driver_name": "delegated",
        "role_name": "test-role",
        "scenario_name": "test-scenario",
        "subcommand": __name__,
        "verifier_name": "ansible",
    }


@pytest.fixture
def _instance(_command_args):
    return scenario.Scenario(_command_args)


@pytest.fixture
def invalid_template_dir(resources_folder_path):
    invalid_role_template_path = os.path.join(
        resources_folder_path, "invalid_scenario_template"
    )
    return invalid_role_template_path


def test_execute(temp_dir, _instance, patched_logger_info):
    _instance.execute()

    msg = "Initializing new scenario test-scenario..."
    patched_logger_info.assert_any_call(msg)

    assert os.path.isdir("./molecule/test-scenario")

    scenario_directory = os.path.join(temp_dir.strpath, "molecule", "test-scenario")
    msg = f"Initialized scenario in {scenario_directory} successfully."
    patched_logger_info.assert_any_call(msg)


def test_execute_scenario_exists(temp_dir, _instance, patched_logger_critical):
    _instance.execute()

    with pytest.raises(SystemExit) as e:
        _instance.execute()

    assert 1 == e.value.code

    msg = "The directory molecule/test-scenario exists. " "Cannot create new scenario."
    patched_logger_critical.assert_called_once_with(msg)


def test_execute_with_invalid_driver(
    temp_dir, _instance, _command_args, patched_logger_critical
):
    _command_args["driver_name"] = "ec3"

    with pytest.raises(KeyError):
        _instance.execute()

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
import re
import shutil

import pytest
import sh

from molecule import util
from molecule.test.conftest import change_dir_to


@pytest.fixture
def scenario_to_test(request):
    return request.param


@pytest.fixture
def scenario_name(request):
    try:
        return request.param
    except AttributeError:
        return None


@pytest.fixture
def driver_name(request):
    return request.param


@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [("side_effect", "docker", "default")],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_side_effect(scenario_to_test, with_scenario, scenario_name):
    options = {"driver_name": "docker", "all": True}
    cmd = sh.molecule.bake("test", **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [("cleanup", "docker", "default")],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_cleanup(scenario_to_test, with_scenario, scenario_name):
    options = {"driver_name": "docker", "all": True}
    cmd = sh.molecule.bake("test", **options)
    pytest.helpers.run_command(cmd)


def test_command_init_scenario_with_invalid_role_raises(temp_dir):
    role_directory = os.path.join(temp_dir.strpath, "test-role")
    options = {}
    cmd = sh.molecule.bake("init", "role", "test-role", **options)
    pytest.helpers.run_command(cmd)
    pytest.helpers.metadata_lint_update(role_directory)

    with change_dir_to(role_directory):
        options = {"role_name": "invalid-role-name"}
        with pytest.raises(sh.ErrorReturnCode) as e:
            cmd = sh.molecule.bake("init", "scenario", "default", **options)
            pytest.helpers.run_command(cmd, log=False)

        msg = (
            "ERROR: The role 'invalid-role-name' not found. "
            "Please choose the proper role name."
        )
        assert msg in str(e.value.stderr)


def test_command_init_scenario_as_default_without_default_scenario(temp_dir):
    role_directory = os.path.join(temp_dir.strpath, "test-role")
    options = {}
    cmd = sh.molecule.bake("init", "role", "test-role", **options)
    pytest.helpers.run_command(cmd)
    pytest.helpers.metadata_lint_update(role_directory)

    with change_dir_to(role_directory):
        molecule_directory = pytest.helpers.molecule_directory()
        scenario_directory = os.path.join(molecule_directory, "default")
        shutil.rmtree(scenario_directory)

        options = {"role_name": "test-role"}
        cmd = sh.molecule.bake("init", "scenario", "default", **options)
        pytest.helpers.run_command(cmd)

        assert os.path.isdir(scenario_directory)


# NOTE(retr0h): Molecule does not allow the creation of a role without
# a default scenario.  This tests roles not created by a newer Molecule.
def test_command_init_scenario_without_default_scenario_raises(temp_dir):
    role_directory = os.path.join(temp_dir.strpath, "test-role")
    options = {}
    cmd = sh.molecule.bake("init", "role", "test-role", **options)
    pytest.helpers.run_command(cmd)
    pytest.helpers.metadata_lint_update(role_directory)

    with change_dir_to(role_directory):
        molecule_directory = pytest.helpers.molecule_directory()
        scenario_directory = os.path.join(molecule_directory, "default")
        shutil.rmtree(scenario_directory)

        options = {"role_name": "test-role"}
        with pytest.raises(sh.ErrorReturnCode) as e:
            cmd = sh.molecule.bake("init", "scenario", "invalid-role-name", **options)
            pytest.helpers.run_command(cmd, log=False)

        msg = (
            "The default scenario not found.  Please create a scenario "
            "named 'default' first."
        )
        assert msg in str(e.value.stderr)


@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [("overrride_driver", "docker", "default")],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_test_overrides_driver(
    scenario_to_test, with_scenario, driver_name, scenario_name
):
    options = {"driver_name": driver_name, "all": True}
    cmd = sh.molecule.bake("test", **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [("driver/docker", "docker", "default")],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_test_builds_local_molecule_image(
    scenario_to_test, with_scenario, scenario_name, driver_name, environ
):
    try:
        image = os.environ["TEST_BASE_IMAGE"]
        cmd = sh.docker.bake("rmi", "molecule_local/{}".format(image), "--force")
        pytest.helpers.run_command(cmd)
    except sh.ErrorReturnCode:
        pass

    pytest.helpers.test(driver_name, scenario_name)


@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [("test_destroy_strategy", "docker", "default")],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_test_destroy_strategy_always(
    scenario_to_test, with_scenario, scenario_name, driver_name
):
    options = {"destroy": "always"}
    with pytest.raises(sh.ErrorReturnCode) as e:
        cmd = sh.molecule.bake("test", **options)
        pytest.helpers.run_command(cmd, log=False)

    stdout = util.strip_ansi_escape(e.value.stdout)

    assert "Action: 'cleanup'" in stdout
    assert "PLAY [Destroy]" in stdout
    assert 0 != e.value.exit_code


@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [("test_destroy_strategy", "docker", "default")],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_test_destroy_strategy_never(
    scenario_to_test, with_scenario, scenario_name, driver_name
):
    options = {"destroy": "never"}
    with pytest.raises(sh.ErrorReturnCode) as e:
        cmd = sh.molecule.bake("test", **options)
        pytest.helpers.run_command(cmd, log=False)

    msg = "An error occurred during the test sequence action: 'lint'. " "Cleaning up."
    assert msg not in str(e.value.stdout)

    assert 0 != e.value.exit_code


@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [("host_group_vars", "docker", "default")],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_host_group_vars(scenario_to_test, with_scenario, scenario_name):
    options = {"all": True}
    cmd = sh.molecule.bake("test", **options)
    out = pytest.helpers.run_command(cmd, log=False)
    out = util.strip_ansi_escape(out.stdout)

    assert re.search(r"\[instance\].*?ok: \[instance\]", out, re.DOTALL)
    assert re.search(r"\[example\].*?ok: \[instance\]", out, re.DOTALL)
    assert re.search(r"\[example_1\].*?ok: \[instance\]", out, re.DOTALL)


@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [("idempotence", "docker", "raises")],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_idempotence_raises(scenario_to_test, with_scenario, scenario_name):
    options = {"scenario_name": scenario_name, "all": True, "destroy": "never"}
    cmd = sh.molecule.bake("test", **options)
    with pytest.raises(sh.ErrorReturnCode_2) as e:
        pytest.helpers.run_command(cmd)

    assert 2 == e.value.exit_code


@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [("interpolation", "docker", "default")],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_interpolation(scenario_to_test, with_scenario, scenario_name):
    # Modify global environment so cleanup inherits our environment.
    options = {"all": True}
    env = os.environ
    env.update({"DRIVER_NAME": "docker", "INSTANCE_NAME": "instance"})

    cmd = sh.molecule.bake("test", **options)
    pytest.helpers.run_command(cmd, env=env)


@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [("verifier", "docker", "testinfra-pre-commit")],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_verify_testinfra_precommit(
    scenario_to_test, with_scenario, scenario_name
):
    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("create", **options)
    pytest.helpers.run_command(cmd)

    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("converge", **options)
    pytest.helpers.run_command(cmd)

    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("verify", **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [("verifier", "docker", "testinfra")],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_verify_testinfra(scenario_to_test, with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("create", **options)
    pytest.helpers.run_command(cmd)

    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("converge", **options)
    pytest.helpers.run_command(cmd)

    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("verify", **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [("plugins", "docker", "default")],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_plugins(scenario_to_test, with_scenario, scenario_name):
    options = {"scenario_name": scenario_name, "all": True}
    cmd = sh.molecule.bake("test", **options)
    pytest.helpers.run_command(cmd)

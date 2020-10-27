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

import pytest
import sh


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


@pytest.mark.extensive
@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [
        ("driver/delegated", "delegated", "default"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_check(scenario_to_test, with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("check", **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.extensive
@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [
        ("driver/delegated", "delegated", "default"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_cleanup(scenario_to_test, with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("cleanup", **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.extensive
@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [
        ("driver/delegated", "delegated", "default"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_converge(scenario_to_test, with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("converge", **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.extensive
@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [
        ("driver/delegated", "delegated", "default"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_create(scenario_to_test, with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("create", **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [
        pytest.param("dependency", "delegated", "shell", id="shell"),
        pytest.param("dependency", "delegated", "ansible-galaxy", id="galaxy"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_dependency(request, scenario_to_test, with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("dependency", **options)
    result = pytest.helpers.run_command(cmd, log=False)
    assert result.exit_code == 0

    # Validate that depdendency worked by running converge, which make use
    cmd = sh.molecule.bake("converge", **options)
    result = pytest.helpers.run_command(cmd, log=False)
    assert result.exit_code == 0


@pytest.mark.extensive
@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [("driver/delegated", "delegated", "default")],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_destroy(scenario_to_test, with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("destroy", **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.extensive
@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [
        ("driver/delegated", "delegated", "default"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_idempotence(scenario_to_test, with_scenario, scenario_name):
    pytest.helpers.idempotence(scenario_name)


@pytest.mark.parametrize("driver_name", [("delegated")], indirect=["driver_name"])
def test_command_init_role(temp_dir, driver_name, skip_test):
    pytest.helpers.init_role(temp_dir, driver_name)


@pytest.mark.parametrize("driver_name", [("delegated")], indirect=["driver_name"])
def test_command_init_scenario(temp_dir, driver_name, skip_test):
    pytest.helpers.init_scenario(temp_dir, driver_name)


@pytest.mark.extensive
@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [
        ("driver/delegated", "delegated", "default"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_lint(scenario_to_test, with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("lint", **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    "scenario_to_test, driver_name, expected",
    [
        (
            "driver/delegated",
            "delegated",
            "instance        delegated       ansible default",
        ),
    ],
    indirect=["scenario_to_test", "driver_name"],
)
def test_command_list_with_format_plain(scenario_to_test, with_scenario, expected):
    pytest.helpers.list_with_format_plain(expected)


# @pytest.mark.parametrize(
#     "scenario_to_test, driver_name, login_args, scenario_name",
#     [
#         (
#             "driver/delegated",
#             "delegated",
#             [["instance", ".*instance.*"]],
#             "default",
#         ),
#     ],
#     indirect=["scenario_to_test", "driver_name", "scenario_name"],
# )
# def test_command_login(scenario_to_test, with_scenario, login_args, scenario_name):
#     pytest.helpers.login(login_args, scenario_name)


@pytest.mark.extensive
@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [
        ("driver/delegated", "delegated", "default"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_prepare(scenario_to_test, with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}

    cmd = sh.molecule.bake("create", **options)
    pytest.helpers.run_command(cmd)

    cmd = sh.molecule.bake("prepare", **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.extensive
@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [
        ("driver/delegated", "delegated", "default"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_side_effect(scenario_to_test, with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("side-effect", **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.extensive
@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [
        ("driver/delegated", "delegated", "default"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_syntax(scenario_to_test, with_scenario, scenario_name):
    options = {"scenario_name": scenario_name}
    cmd = sh.molecule.bake("syntax", **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [
        ("driver/delegated", "delegated", "default"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_test(scenario_to_test, with_scenario, scenario_name, driver_name):
    pytest.helpers.test(driver_name, scenario_name)


@pytest.mark.extensive
@pytest.mark.parametrize(
    "scenario_to_test, driver_name, scenario_name",
    [
        ("driver/delegated", "delegated", "default"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_verify(scenario_to_test, with_scenario, scenario_name):
    pytest.helpers.verify(scenario_name)

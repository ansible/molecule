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
import pathlib

from pathlib import Path

import pytest

from pytest import FixtureRequest  # noqa: PT013

from molecule.command import base
from molecule.util import run_command
from tests.b_functional.conftest import (  # pylint:disable=C0411
    idempotence,
    init_scenario,
    list_with_format_plain,
    run_test,
    verify,
)
from tests.conftest import mac_on_gh  # pylint:disable=C0411


@pytest.fixture(name="scenario_to_test")
def fixture_scenario_to_test(request):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    return request.param


@pytest.fixture(name="scenario_name")
def fixture_scenario_name(request):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    try:
        return request.param
    except AttributeError:
        return None


@pytest.fixture(name="driver_name")
def fixture_driver_name(request: FixtureRequest) -> str | None:  # noqa: D103
    try:
        # https://stackoverflow.com/q/65334215/99834
        return request.param  # type: ignore  # noqa: PGH003
    except AttributeError:
        return None


@pytest.fixture(name="platform_name")
def fixture_platform_name(request):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    try:
        return request.param
    except AttributeError:
        return None


@pytest.mark.extensive()
@pytest.mark.parametrize(
    ("scenario_to_test", "driver_name", "scenario_name"),
    [  # noqa: PT007
        pytest.param("driver/delegated", "default", "default", id="0"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_check(scenario_to_test, with_scenario, scenario_name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    cmd = ["molecule", "check", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0


@pytest.mark.extensive()
@pytest.mark.parametrize(
    ("scenario_to_test", "driver_name", "scenario_name"),
    [  # noqa: PT007
        pytest.param("driver/delegated", "default", "default", id="0"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
@pytest.mark.serial()
def test_command_cleanup(scenario_to_test, with_scenario, scenario_name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    cmd = ["molecule", "cleanup", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0


@pytest.mark.extensive()
@pytest.mark.parametrize(
    ("scenario_to_test", "driver_name", "scenario_name"),
    [  # noqa: PT007
        pytest.param("driver/delegated", "default", "default", id="0"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
@pytest.mark.serial()
def test_command_converge(scenario_to_test, with_scenario, scenario_name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    cmd = ["molecule", "converge", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0


@pytest.mark.extensive()
@pytest.mark.parametrize(
    ("scenario_to_test", "driver_name", "scenario_name"),
    [  # noqa: PT007
        pytest.param("driver/delegated", "default", "default", id="0"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
@pytest.mark.serial()
def test_command_create(scenario_to_test, with_scenario, scenario_name, tmp_path):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    cmd = ["molecule", "create", "--scenario-name", scenario_name]
    assert run_command(cmd, env=os.environ).returncode == 0


@pytest.mark.parametrize(
    ("scenario_to_test", "driver_name", "scenario_name"),
    [  # noqa: PT007
        pytest.param(
            "dependency",
            "default",
            "shell",
        ),
        pytest.param(
            "dependency",
            "default",
            "ansible-galaxy",
            id="galaxy",
        ),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
@pytest.mark.serial()
def test_command_dependency(request, scenario_to_test, with_scenario, scenario_name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    cmd = ["molecule", "dependency", "--scenario-name", scenario_name]
    assert run_command(cmd, echo=True).returncode == 0

    # Validate that dependency worked by running converge, which make use
    cmd = ["molecule", "converge", "--scenario-name", scenario_name]
    assert run_command(cmd, echo=True).returncode == 0


@pytest.mark.serial()
@pytest.mark.extensive()
@pytest.mark.parametrize(
    ("scenario_to_test", "driver_name", "scenario_name"),
    [pytest.param("driver/delegated", "default", "default", id="0")],  # noqa: PT007
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_destroy(scenario_to_test, with_scenario, scenario_name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    cmd = ["molecule", "destroy", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0


@pytest.mark.serial()
@pytest.mark.extensive()
@pytest.mark.parametrize(
    ("scenario_to_test", "driver_name", "scenario_name"),
    [  # noqa: PT007
        pytest.param("driver/delegated", "default", "default", id="0"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_idempotence(scenario_to_test, with_scenario, scenario_name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    idempotence(scenario_name)  # type: ignore[no-untyped-call]


@pytest.mark.serial()
def test_command_init_scenario(temp_dir):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    init_scenario(temp_dir, "default")  # type: ignore[no-untyped-call]


@pytest.mark.serial()
@pytest.mark.parametrize(
    ("scenario_to_test", "driver_name", "expected"),
    [  # noqa: PT007
        pytest.param(
            "driver/delegated",
            "default",
            "instance        default ansible default",
            id="0",
        ),
    ],
    indirect=["scenario_to_test", "driver_name"],
)
def test_command_list_with_format_plain(scenario_to_test, with_scenario, expected):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    list_with_format_plain(expected)  # type: ignore[no-untyped-call]


@pytest.mark.serial()
@pytest.mark.extensive()
@pytest.mark.parametrize(
    ("scenario_to_test", "driver_name", "scenario_name"),
    [  # noqa: PT007
        pytest.param("driver/delegated", "default", "default", id="0"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_prepare(scenario_to_test, with_scenario, scenario_name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    cmd = ["molecule", "create", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0

    cmd = ["molecule", "prepare", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0


@pytest.mark.serial()
@pytest.mark.extensive()
@pytest.mark.parametrize(
    ("scenario_to_test", "driver_name", "scenario_name"),
    [  # noqa: PT007
        pytest.param("driver/delegated", "default", "default", id="0"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_side_effect(scenario_to_test, with_scenario, scenario_name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    cmd = ["molecule", "side-effect", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0


@pytest.mark.serial()
@pytest.mark.extensive()
@pytest.mark.parametrize(
    ("scenario_to_test", "driver_name", "scenario_name"),
    [  # noqa: PT007
        pytest.param("driver/delegated", "default", "default", id="0"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_syntax(scenario_to_test, with_scenario, scenario_name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    cmd = ["molecule", "syntax", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0


@pytest.mark.serial()
@pytest.mark.parametrize(
    ("scenario_to_test", "driver_name", "scenario_name"),
    [  # noqa: PT007
        pytest.param("driver/delegated", "default", "default", id="0"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_test(scenario_to_test, with_scenario, scenario_name, driver_name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    run_test(driver_name, scenario_name)  # type: ignore[no-untyped-call]


def run_test_with_platform_name(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    driver_name,  # noqa: ANN001
    platform_name,  # noqa: ANN001
    scenario_name="default",  # noqa: ANN001
    parallel=False,  # noqa: ANN001, FBT002
):
    cmd = [
        "molecule",
        "-vvv",
        "--debug",
        "test",
        "--scenario-name",
        scenario_name,
        "--platform-name",
        platform_name,
    ]
    if driver_name != "default":
        if scenario_name is None:
            cmd.append("--all")
        if parallel:
            cmd.append("--parallel")

    assert run_command(cmd).returncode == 0


@pytest.mark.serial()
@pytest.mark.parametrize(
    ("scenario_to_test", "driver_name", "scenario_name", "platform_name"),
    [  # noqa: PT007
        pytest.param("driver/delegated", "default", "default", "instance", id="0"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name", "platform_name"],
)
def test_command_test_with_platform_name(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    scenario_to_test,  # noqa: ANN001, ARG001
    with_scenario,  # noqa: ANN001, ARG001
    scenario_name,  # noqa: ANN001
    driver_name,  # noqa: ANN001
    platform_name,  # noqa: ANN001
):
    run_test_with_platform_name(driver_name, platform_name, scenario_name)  # type: ignore[no-untyped-call]


@pytest.mark.serial()
@pytest.mark.parametrize(
    ("scenario_to_test", "driver_name", "scenario_name"),
    [  # noqa: PT007
        pytest.param(
            "driver/delegated_invalid_role_name_with_role_name_check_equals_to_1",
            "default",
            "default",
            id="0",
        ),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_test_with_role_name_check_equals_to_1(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    scenario_to_test,  # noqa: ANN001, ARG001
    with_scenario,  # noqa: ANN001, ARG001
    scenario_name,  # noqa: ANN001
    driver_name,  # noqa: ANN001
):
    run_test(driver_name, scenario_name)  # type: ignore[no-untyped-call]


@pytest.mark.serial()
@pytest.mark.extensive()
@pytest.mark.parametrize(
    ("scenario_to_test", "driver_name", "scenario_name"),
    [  # noqa: PT007
        pytest.param("driver/delegated", "default", "default", id="0"),
    ],
    indirect=["scenario_to_test", "driver_name", "scenario_name"],
)
def test_command_verify(scenario_to_test, with_scenario, scenario_name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    verify(scenario_name)  # type: ignore[no-untyped-call]


def test_sample_collection() -> None:  # noqa: D103
    assert (
        run_command(
            ["molecule", "test"],
            cwd="tests/resources/sample-collection",
        ).returncode
        == 0
    )


@pytest.mark.parametrize(
    ("scenario_name"),
    [  # noqa: PT007
        ("test_w_gitignore"),
        ("test_wo_gitignore"),
    ],
)
def test_with_and_without_gitignore(  # noqa: D103
    monkeypatch: pytest.MonkeyPatch,
    scenario_name: str,
) -> None:
    if scenario_name == "test_wo_gitignore":

        def mock_return(scenario_paths) -> list[str]:  # type: ignore[no-untyped-def]  # noqa: ANN001
            return scenario_paths  # type: ignore[no-any-return]

        monkeypatch.setattr(
            "molecule.command.base.filter_ignored_scenarios",
            mock_return,
        )

    resource_path = pathlib.Path(__file__).parent.parent / "resources"

    monkeypatch.chdir(resource_path)

    pathlib.Path(resource_path / f".extensions/molecule/{scenario_name}").mkdir(
        parents=True,
        exist_ok=True,
    )

    pathlib.Path(f".extensions/molecule/{scenario_name}/molecule.yml").touch()

    op = base.get_configs({}, {}, glob_str="**/molecule/*/molecule.yml")  # type: ignore[no-untyped-call]

    names = [config.scenario.name for config in op]
    if scenario_name == "test_w_gitignore":
        assert scenario_name not in names
    elif scenario_name == "test_wo_gitignore":
        assert scenario_name in names


@mac_on_gh
def test_podman(monkeypatch: pytest.MonkeyPatch, test_fixture_dir: Path) -> None:
    """Execute Podman scenario.

    Args:
        monkeypatch: Pytest fixture.
        test_fixture_dir: Path to the test fixture directory.
    """
    monkeypatch.chdir(test_fixture_dir)
    command = ["molecule", "test", "--scenario-name", "podman"]
    assert run_command(command).returncode == 0


@mac_on_gh
def test_docker(monkeypatch: pytest.MonkeyPatch, test_fixture_dir: Path) -> None:
    """Execute Docker scenario.

    Args:
        monkeypatch: Pytest fixture.
        test_fixture_dir: Path to the test fixture directory.
    """
    monkeypatch.chdir(test_fixture_dir)
    command = ["molecule", "test", "--scenario-name", "docker"]
    assert run_command(command).returncode == 0


def test_smoke(monkeypatch: pytest.MonkeyPatch, test_fixture_dir: Path) -> None:
    """Execute smoke-test scenario that should spot potentially breaking changes.

    Args:
        monkeypatch: Pytest fixture.
        test_fixture_dir: Path to the test fixture directory.
    """
    monkeypatch.chdir(test_fixture_dir)
    command = ["molecule", "test", "--scenario-name", "smoke"]
    assert run_command(command).returncode == 0

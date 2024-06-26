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

from pathlib import Path
from typing import TypedDict

import pytest

from pytest import FixtureRequest  # noqa: PT013

from molecule.command import base
from molecule.util import run_command
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


class ParamDefault(TypedDict):
    """Typed params."""

    argnames: tuple[str, str]
    argvalues: tuple[tuple[str, str]]
    ids: str
    indirect: tuple[str, str]


PARAMS_DEFAULT: ParamDefault = {
    "argnames": ("scenario_to_test", "scenario_name"),
    "argvalues": (("driver/delegated", "default"),),
    "ids": "0",
    "indirect": ("scenario_to_test", "scenario_name"),
}


@pytest.mark.extensive()
@pytest.mark.parametrize(**PARAMS_DEFAULT)
@pytest.mark.usefixtures("with_scenario")
@pytest.mark.parametrize(
    "command",
    (
        "check",
        "cleanup",
        "converge",
        "create",
        "destroy",
        "prepare",
        "syntax",
        "side-effect",
        "test",
        "verify",
    ),
)
def test_command(
    test_ephemeral_dir_env: dict[str, str],
    scenario_name: str,
    command: str,
) -> None:
    """Test a scenario using command.

    Args:
        test_ephemeral_dir_env: The ephemeral directory env.
        scenario_name: The scenario name.
        command: The command to run.
    """
    cmd = ["molecule", command, "--scenario-name", scenario_name]
    result = run_command(cmd=cmd, env=test_ephemeral_dir_env)
    assert run_command(cmd=cmd, env=test_ephemeral_dir_env).returncode == 0
    if command == "syntax":
        assert "converge.yml" in result.stdout
    else:
        assert "PLAY RECAP" in result.stdout


@pytest.mark.extensive()
@pytest.mark.parametrize(**PARAMS_DEFAULT)
@pytest.mark.usefixtures("with_scenario")
def test_command_idempotence(test_ephemeral_dir_env: dict[str, str], scenario_name: str) -> None:
    """Test idempotence of a scenario.

    Args:
        test_ephemeral_dir_env: The ephemeral directory env.
        scenario_name: The scenario name.
    """
    cmd = ["molecule", "create", "--scenario-name", scenario_name]
    assert run_command(cmd=cmd, env=test_ephemeral_dir_env).returncode == 0

    cmd = ["molecule", "converge", "--scenario-name", scenario_name]
    assert run_command(cmd=cmd, env=test_ephemeral_dir_env).returncode == 0

    cmd = ["molecule", "idempotence", "--scenario-name", scenario_name]
    assert run_command(cmd=cmd, env=test_ephemeral_dir_env).returncode == 0


@pytest.mark.parametrize(
    ("scenario_to_test", "scenario_name"),
    (("dependency", "shell"), ("dependency", "ansible-galaxy")),
)
@pytest.mark.usefixtures("with_scenario")
def test_command_dependency(test_ephemeral_dir_env: dict[str, str], scenario_name: str) -> None:
    """Test scenario dependency.

    Args:
        test_ephemeral_dir_env: The ephemeral directory env.
        scenario_name: The scenario name.
    """
    cmd = ["molecule", "dependency", "--scenario-name", scenario_name]
    assert run_command(cmd, env=test_ephemeral_dir_env).returncode == 0

    # Validate that dependency worked by running converge, which make use it
    cmd = ["molecule", "converge", "--scenario-name", scenario_name]
    assert run_command(cmd, env=test_ephemeral_dir_env).returncode == 0


def test_command_init_scenario(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    test_ephemeral_dir_env: dict[str, str],
) -> None:
    """Test scenario initialization.

    Manually destroy the scenario after the test because the with_scenario fixture
    is not used.

    Args:
        monkeypatch: Pytest fixture.
        tmp_path: Path to the temporary directory.
        test_ephemeral_dir_env: The ephemeral directory env.
    """
    monkeypatch.chdir(tmp_path)
    scenario_name = "test-scenario"

    cmd = ["molecule", "init", "scenario", scenario_name]
    assert run_command(cmd).returncode == 0
    assert (tmp_path / "molecule" / scenario_name).is_dir()

    cmd = ["molecule", "test", "--scenario-name", "test-scenario", "--all"]
    assert run_command(cmd=cmd, env=test_ephemeral_dir_env).returncode == 0

    cmd = ["molecule", "destroy", "--scenario-name", "test-scenario"]
    assert run_command(cmd=cmd, env=test_ephemeral_dir_env).returncode == 0


def test_command_list_with_format_plain(
    monkeypatch: pytest.MonkeyPatch,
    test_fixture_dir: Path,
    test_ephemeral_dir_env: dict[str, str],
) -> None:
    """Test list command with plain format.

    Args:
        monkeypatch: Pytest fixture.
        test_fixture_dir: Path to the test fixture directory.
        test_ephemeral_dir_env: The ephemeral directory env.
    """
    monkeypatch.chdir(test_fixture_dir / "scenarios" / "driver" / "delegated")
    cmd = ["molecule", "list", "--format", "plain"]
    result = run_command(cmd=cmd, env=test_ephemeral_dir_env)
    assert result.returncode == 0
    assert result.stdout == "instance        default ansible default false   false\n"


@pytest.mark.extensive()
@pytest.mark.parametrize(**PARAMS_DEFAULT)
@pytest.mark.usefixtures("with_scenario")
@pytest.mark.parametrize(("platform", "missing"), (("instance", False), ("gonzo", True)))
def test_with_missing_platform_name(
    test_ephemeral_dir_env: dict[str, str],
    scenario_name: str,
    platform: str,
    missing: bool,  # noqa: FBT001
) -> None:
    """Test a scenario using command with missing platform name.

    Args:
        test_ephemeral_dir_env: The ephemeral directory env.
        scenario_name: The scenario name.
        platform: The platform name.
        missing: If platform name is missing.
    """
    cmd = ["molecule", "test", "-s", scenario_name, "-p", platform]
    result = run_command(cmd=cmd, env=test_ephemeral_dir_env)
    assert bool(result.returncode) == missing
    if missing:
        assert "Instances missing" in result.stderr
    else:
        assert "PLAY RECAP" in result.stdout


def test_role_name_check_one(
    monkeypatch: pytest.MonkeyPatch,
    test_fixture_dir: Path,
    test_ephemeral_dir_env: dict[str, str],
) -> None:
    """Test role name check only warns when equal to 1.

    Args:
        monkeypatch: Pytest fixture.
        test_fixture_dir: Path to the test fixture directory.
        test_ephemeral_dir_env: The ephemeral directory env.
    """
    scenario_dir = "delegated_invalid_role_name_with_role_name_check_equals_to_1"
    monkeypatch.chdir(test_fixture_dir / "scenarios" / "driver" / scenario_dir)
    cmd = ["molecule", "dependency"]
    result = run_command(cmd=cmd, env=test_ephemeral_dir_env)
    assert result.returncode == 0
    string = "molecule.delegated-test does not follow current galaxy requirements"
    assert string in result.stderr
    cmd = ["molecule", "destroy"]
    result = run_command(cmd=cmd, env=test_ephemeral_dir_env)
    assert result.returncode == 0


def test_sample_collection(
    monkeypatch: pytest.MonkeyPatch,
    resources_folder_path: Path,
    test_ephemeral_dir_env: dict[str, str],
) -> None:
    """Test the sample collection.

    Args:
        monkeypatch: Pytest fixture.
        resources_folder_path: Path to the resources folder.
        test_ephemeral_dir_env: The ephemeral directory env.
    """
    monkeypatch.chdir(resources_folder_path / "sample-collection")
    cmd = ["molecule", "test"]
    assert run_command(cmd=cmd, env=test_ephemeral_dir_env).returncode == 0


@pytest.mark.usefixtures("test_cache_path")
@pytest.mark.parametrize(("scenario_name"), (("test_w_gitignore"), ("test_wo_gitignore")))
def test_with_and_without_gitignore(
    monkeypatch: pytest.MonkeyPatch,
    scenario_name: str,
    resources_folder_path: Path,
) -> None:
    """Test with and without gitignore.

    Args:
        monkeypatch: Pytest fixture.
        scenario_name: The scenario name.
        resources_folder_path: Path to the resources folder.
    """
    if scenario_name == "test_wo_gitignore":

        def mock_return(scenario_paths: list[str]) -> list[str]:
            return scenario_paths

        monkeypatch.setattr(
            "molecule.command.base.filter_ignored_scenarios",
            mock_return,
        )

    monkeypatch.chdir(resources_folder_path)

    scenario_dir = resources_folder_path / ".extensions" / "molecule" / scenario_name
    scenario_dir.mkdir(parents=True, exist_ok=True)

    molecule_file = scenario_dir / "molecule.yml"
    molecule_file.touch()

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
    result = run_command(command)
    assert result.returncode == 0, result

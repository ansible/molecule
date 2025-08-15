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

import difflib
import os
import re
import shutil
import subprocess
import warnings

from functools import cache
from pathlib import Path
from typing import Any, TypedDict

import pytest

from pytest import FixtureRequest  # noqa: PT013

from molecule.command import base
from molecule.text import strip_ansi_escape
from tests.conftest import mac_on_gh  # pylint:disable=C0411


def run(cmd: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[Any]:
    """Run a command.

    Args:
        cmd: The command to run.
        env: The environment.

    Returns:
        The result.
    """
    return subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)


@cache
def has_pure_docker() -> bool:
    """Check if pure working Docker is available.

    Returns:
        True if Docker is installed, working and not using podman backend.
    """
    # https://github.com/podman-desktop/podman-desktop/issues/10745
    failure = ""
    default_docker_socket = Path("/var/run/docker.sock")
    if not shutil.which("docker"):
        failure = "Docker is not installed."
    elif default_docker_socket.exists():
        # detect if docker is NOT using podman's backend (libpod)
        result = run(
            [
                "curl",
                "--silent",
                "--unix-socket",
                "/var/run/docker.sock",
                "http:/v1/_ping",
            ],
        )
        if result.returncode != 0:
            failure = "Docker does not seem to respond to default socket."
        else:
            result = run(
                [
                    "curl",
                    "--silent",
                    "--unix-socket",
                    "/var/run/docker.sock",
                    "http:/v1/libpod/_ping",
                ],
            )
            if result.stdout == "OK":
                if shutil.which("podman-mac-helper"):
                    failure = "Docker is using podman's backend, run `sudo podman-mac-helper uninstall` to disable it."
                else:
                    failure = "Docker is using podman's backend, so we will skip running docker tests as they are high likely to fail. See https://github.com/ansible-collections/community.docker/issues/660 https://github.com/containers/podman/issues/16548"
            elif result.stdout.rstrip() not in (
                "Not Found",
                '{"message":"page not found"}',
            ):
                failure = f"Unexpected response from Docker's default socket {result.stdout}."
    else:
        result = run(["docker", "context", "inspect", "--format", "{{.Endpoints.docker.Host}}"])
        if result.returncode != 0:
            failure = f"Docker was not able to report its currently active socket for current context: {result.stderr.rstrip()}"
        else:
            docker_current_socket = result.stdout.rstrip()
            warnings.warn(
                f"Docker found but not using default socket from {default_docker_socket}, we will define DOCKER_HOST={docker_current_socket} during testing. See https://github.com/ansible-collections/community.docker/issues/660#issuecomment-2607286542",
                stacklevel=2,
            )
            os.environ["DOCKER_HOST"] = result.stdout.rstrip()
    if failure:
        warnings.warn(  # noqa: B028
            failure,
            category=RuntimeWarning,
        )
        return False
    return True


@pytest.fixture(name="scenario_to_test")
def fixture_scenario_to_test(request: FixtureRequest):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    return request.param


@pytest.fixture(name="scenario_name")
def fixture_scenario_name(request: FixtureRequest):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
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
    """Typed params.

    Attributes:
        argnames: The argnames.
        argvalues: The argvalues.
        ids: The ids.
        indirect: The indirect.
    """

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


def normalize_report_whitespace(text: str) -> str:
    """Normalize whitespace in report text for comparison.

    Strips trailing whitespace from each line while preserving line structure.
    This handles the 79-character padding in headers like 'DETAILS' and 'SCENARIO RECAP'.

    Args:
        text: Text to normalize.

    Returns:
        Text with trailing whitespace stripped from each line.
    """
    return "\n".join(line.rstrip() for line in text.splitlines()) + (
        "\n" if text.endswith("\n") else ""
    )


@pytest.mark.extensive
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
    result = run(cmd=cmd, env=test_ephemeral_dir_env)
    assert result.returncode == 0
    if command == "syntax":
        assert "converge.yml" in result.stdout
    else:
        assert "PLAY RECAP" in result.stdout


@pytest.mark.extensive
@pytest.mark.parametrize(**PARAMS_DEFAULT)
@pytest.mark.usefixtures("with_scenario")
def test_command_idempotence(
    test_ephemeral_dir_env: dict[str, str],
    scenario_name: str,
) -> None:
    """Test idempotence of a scenario.

    Args:
        test_ephemeral_dir_env: The ephemeral directory env.
        scenario_name: The scenario name.
    """
    cmd = ["molecule", "create", "--scenario-name", scenario_name]
    assert run(cmd=cmd, env=test_ephemeral_dir_env).returncode == 0

    cmd = ["molecule", "converge", "--scenario-name", scenario_name]
    assert run(cmd=cmd, env=test_ephemeral_dir_env).returncode == 0

    cmd = ["molecule", "idempotence", "--scenario-name", scenario_name]
    assert run(cmd=cmd, env=test_ephemeral_dir_env).returncode == 0


@pytest.mark.parametrize(
    ("scenario_to_test", "scenario_name"),
    (("dependency", "shell"), ("dependency", "ansible-galaxy")),
)
@pytest.mark.usefixtures("with_scenario")
def test_command_dependency(
    test_ephemeral_dir_env: dict[str, str],
    scenario_name: str,
) -> None:
    """Test scenario dependency.

    Args:
        test_ephemeral_dir_env: The ephemeral directory env.
        scenario_name: The scenario name.
    """
    cmd = ["molecule", "dependency", "--scenario-name", scenario_name]
    assert run(cmd, env=test_ephemeral_dir_env).returncode == 0

    # Validate that dependency worked by running converge, which make use it
    cmd = ["molecule", "converge", "--scenario-name", scenario_name]
    assert run(cmd, env=test_ephemeral_dir_env).returncode == 0


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
    assert run(cmd).returncode == 0
    assert (tmp_path / "molecule" / scenario_name).is_dir()

    cmd = ["molecule", "test", "--scenario-name", "test-scenario", "--all"]
    assert run(cmd=cmd, env=test_ephemeral_dir_env).returncode == 0

    cmd = ["molecule", "destroy", "--scenario-name", "test-scenario"]
    assert run(cmd=cmd, env=test_ephemeral_dir_env).returncode == 0


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
    result = run(cmd=cmd, env=test_ephemeral_dir_env)
    assert result.returncode == 0
    assert result.stdout == "instance        default ansible default false   false\n"


@pytest.mark.extensive
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
    result = run(cmd=cmd, env=test_ephemeral_dir_env)
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
    result = run(cmd=cmd, env=test_ephemeral_dir_env)
    assert result.returncode == 0
    string = "molecule.delegated-test does not follow current galaxy requirements"
    assert string in result.stderr
    cmd = ["molecule", "destroy"]
    result = run(cmd=cmd, env=test_ephemeral_dir_env)
    assert result.returncode == 0


def test_sample_collection(
    monkeypatch: pytest.MonkeyPatch,
    resources_folder_path: Path,
    test_ephemeral_dir_env: dict[str, str],
) -> None:
    """Test the sample collection with collection detection.

    Args:
        monkeypatch: Pytest fixture.
        resources_folder_path: Path to the resources folder.
        test_ephemeral_dir_env: The ephemeral directory env.
    """
    monkeypatch.chdir(resources_folder_path / "sample-collection")
    cmd = ["molecule", "test"]
    result = run(cmd=cmd, env=test_ephemeral_dir_env)
    assert result.returncode == 0, result
    assert "Collection 'acme.goodies' detected" in result.stderr


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

    op = base.get_configs({}, {}, glob_str="**/molecule/*/molecule.yml")

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
    assert run(command).returncode == 0


@mac_on_gh
def test_native_inventory(monkeypatch: pytest.MonkeyPatch, test_fixture_dir: Path) -> None:
    """Execute Native inventory scenario.

    Args:
        monkeypatch: Pytest fixture.
        test_fixture_dir: Path to the test fixture directory.
    """
    monkeypatch.chdir(test_fixture_dir)
    command = ["molecule", "test", "--scenario-name", "native_inventory"]
    assert run(command).returncode == 0


@mac_on_gh
@pytest.mark.skipif(
    not has_pure_docker(),
    reason="Bug https://github.com/ansible-collections/community.docker/issues/660",
)
def test_docker(monkeypatch: pytest.MonkeyPatch, test_fixture_dir: Path) -> None:
    """Execute Docker scenario.

    Args:
        monkeypatch: Pytest fixture.
        test_fixture_dir: Path to the test fixture directory.
    """
    monkeypatch.chdir(test_fixture_dir)
    # This trick should force Docker to use its own backend on macOS even with Podman's Docker Extensions enabled,
    # but community.docker collection is not yet able to read it due:
    # https://github.com/ansible-collections/community.docker/issues/660
    docker_socket = Path("~/Library/Containers/com.docker.docker/Data/docker-cli.sock").expanduser()
    if docker_socket.exists():
        monkeypatch.setenv("DOCKER_SOCKET", docker_socket.as_posix())

    command = ["molecule", "test", "--scenario-name", "docker"]
    proc = subprocess.run(command, capture_output=True, text=True, check=False)
    assert proc.returncode == 0


def test_smoke(monkeypatch: pytest.MonkeyPatch, test_fixture_dir: Path) -> None:
    """Execute smoke-test scenario that should spot potentially breaking changes.

    Args:
        monkeypatch: Pytest fixture.
        test_fixture_dir: Path to the test fixture directory.
    """
    monkeypatch.chdir(test_fixture_dir)
    command = ["molecule", "test", "--scenario-name", "smoke"]
    result = run(command)
    assert result.returncode == 0, result


def test_with_backend_as_ansible_playbook(
    monkeypatch: pytest.MonkeyPatch,
    test_fixture_dir: Path,
) -> None:
    """Execute test-scenario (smoke test) that should spot potentially breaking changes.

    Args:
        monkeypatch: Pytest fixture.
        test_fixture_dir: Path to the test fixture directory.
    """
    monkeypatch.chdir(test_fixture_dir)
    command = ["molecule", "test", "--scenario-name", "test-scenario"]
    result = run(command)
    assert result.returncode == 0, result


@mac_on_gh
def test_with_backend_as_ansible_navigator(
    monkeypatch: pytest.MonkeyPatch,
    test_fixture_dir: Path,
) -> None:
    """Execute test-scenario-for-nav (smoke test) that should spot potentially breaking changes.

    Args:
        monkeypatch: Pytest fixture.
        test_fixture_dir: Path to the test fixture directory.
    """
    monkeypatch.chdir(test_fixture_dir)
    command = ["molecule", "test", "--scenario-name", "test-scenario-for-nav"]
    result = run(command)
    assert result.returncode == 0, result


def _sanitize_molecule_output(output: str) -> str:
    """Sanitize dynamic parts of molecule output for consistent comparison.

    Args:
        output: Raw molecule output with ANSI codes

    Returns:
        Sanitized output with dynamic parts replaced by REDACTED and warnings filtered out
        and trailing whitespace removed except for the last line which is always a newline
    """
    clean = strip_ansi_escape(output)
    clean = re.sub(r'([\s=\'"]|^)(/[^\s]+)', r"\1REDACTED", clean, flags=re.MULTILINE)
    clean_lines = []
    for line in clean.splitlines():
        if "WARNING" in line:
            continue
        clean_lines.append(line.rstrip())

    return "\n".join(clean_lines).rstrip() + "\n"


def test_full_output(
    monkeypatch: pytest.MonkeyPatch,
    test_fixture_dir: Path,
    tmp_path: Path,
) -> None:
    """Test complete molecule workflow with command borders and shared state.

    This comprehensive test replaces multiple individual command border tests
    and validates the entire molecule workflow output against a golden file.
    It tests:
    - Command border formatting for all external commands
    - Shared state behavior across multiple scenarios
    - Complete test lifecycle (dependency → syntax → converge → idempotence → verify)
    - Report generation with proper formatting

    To regenerate the fixture (when molecule output format changes):
        MOLECULE_UPDATE_FIXTURES=1 python -m pytest tests/integration/test_command.py::test_full_output -v

    Args:
        monkeypatch: Pytest fixture for environment manipulation
        test_fixture_dir: Path to the test fixture directory
        tmp_path: Pytest fixture providing an isolated temporary directory
    """
    monkeypatch.chdir(test_fixture_dir)

    monkeypatch.setenv("MOLECULE_EPHEMERAL_DIRECTORY", str(tmp_path))
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")
    monkeypatch.setenv("COLUMNS", "200")
    monkeypatch.setenv("LINES", "50")
    monkeypatch.setenv("TERM", "xterm-256color")
    monkeypatch.setenv("ANSIBLE_FORCE_COLOR", "1")
    monkeypatch.setenv("ANSIBLE_STDOUT_CALLBACK", "default")
    monkeypatch.setenv("ANSIBLE_DEPRECATION_WARNINGS", "false")
    monkeypatch.setenv("ANSIBLE_COMMAND_WARNINGS", "false")
    monkeypatch.setenv("ANSIBLE_ACTION_WARNINGS", "false")

    # Run comprehensive molecule test with command borders and shared state
    # First reset all scenarios to ensure clean state and avoid warning messages about modified scenario config files
    for scenario in ["default", "test-scenario", "smoke"]:
        reset_cmd = ["molecule", "reset", "-s", scenario]
        _reset_result = run(cmd=reset_cmd)

    cmd = [
        "molecule",
        "test",
        "--shared-state",
        "--command-borders",
        "-s",
        "test-scenario",
        "-s",
        "smoke",
        "--report",
    ]
    result = run(cmd=cmd)
    assert result.returncode == 0, result

    actual_output = _sanitize_molecule_output(result.stderr)

    # Update fixture if requested via environment variable
    fixture_file = test_fixture_dir / "comprehensive_output.txt"
    if os.getenv("MOLECULE_UPDATE_FIXTURES"):
        fixture_file.write_text(actual_output)
        print(f"Updated fixture: {fixture_file}")

    assert fixture_file.exists(), f"Fixture file not found: {fixture_file}"
    expected_output = fixture_file.read_text()

    if actual_output != expected_output:
        diff = "\n".join(
            difflib.unified_diff(
                expected_output.splitlines(keepends=True),
                actual_output.splitlines(keepends=True),
                fromfile="expected (fixture)",
                tofile="actual (molecule output)",
                lineterm="",
            ),
        )
        pytest.fail(
            f"Comprehensive molecule output differs from expected fixture.\n\n"
            f"Unified diff:\n{diff}\n\n"
            f"Expected output length: {len(expected_output)} chars\n"
            f"Actual output length: {len(actual_output)} chars",
        )

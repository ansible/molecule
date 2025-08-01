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
import shutil
import subprocess
import warnings

from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict

import pytest

from pytest import FixtureRequest  # noqa: PT013

from molecule.command import base
from molecule.text import strip_ansi_escape
from tests.conftest import mac_on_gh  # pylint:disable=C0411


if TYPE_CHECKING:
    from molecule.app import App


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
    app: App,
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
    app: App,
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
    app: App,
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
    app: App,
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
    app: App,
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
    """Test the sample collection.

    Args:
        monkeypatch: Pytest fixture.
        resources_folder_path: Path to the resources folder.
        test_ephemeral_dir_env: The ephemeral directory env.
    """
    monkeypatch.chdir(resources_folder_path / "sample-collection")
    cmd = ["molecule", "test"]
    assert run(cmd=cmd, env=test_ephemeral_dir_env).returncode == 0


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
def test_podman(monkeypatch: pytest.MonkeyPatch, test_fixture_dir: Path, app: App) -> None:
    """Execute Podman scenario.

    Args:
        monkeypatch: Pytest fixture.
        test_fixture_dir: Path to the test fixture directory.
    """
    monkeypatch.chdir(test_fixture_dir)
    command = ["molecule", "test", "--scenario-name", "podman"]
    assert run(command).returncode == 0


@mac_on_gh
@pytest.mark.skipif(
    not has_pure_docker(),
    reason="Bug https://github.com/ansible-collections/community.docker/issues/660",
)
def test_docker(monkeypatch: pytest.MonkeyPatch, test_fixture_dir: Path, app: App) -> None:
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


def test_smoke(monkeypatch: pytest.MonkeyPatch, test_fixture_dir: Path, app: App) -> None:
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


def test_shared_actions(
    monkeypatch: pytest.MonkeyPatch,
    test_fixture_dir: Path,
) -> None:
    """Test that shared-state properly threads scenarios.

    Args:
        monkeypatch: Pytest fixture.
        test_fixture_dir: Path to the test fixture directory.
    """
    monkeypatch.chdir(test_fixture_dir)

    # Ensure consistent output format by removing GitHub-specific environment variables
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("CI", raising=False)

    # Override the autouse _no_color fixture to enable markup for this test
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")

    cmd = [
        "molecule",
        "test",
        "--shared-state",
        "-s",
        "test-scenario",
        "-s",
        "smoke",
        "--report",
    ]
    result = run(cmd=cmd)
    assert result.returncode == 0, result

    # Capture both stdout and stderr - this is what users actually see
    stdout_output = result.stdout
    stderr_output = result.stderr

    # Strip ANSI escape codes for assertions
    clean_stdout = strip_ansi_escape(stdout_output)
    clean_stderr = strip_ansi_escape(stderr_output)

    # Verify proper shared-state behavior - test scenarios should not create/destroy
    assert "test-scenario ➜ create" not in clean_stdout, (
        "test-scenario should not create (shared-state)"
    )
    assert "test-scenario ➜ destroy" not in clean_stdout, (
        "test-scenario should not destroy (shared-state)"
    )
    assert "smoke ➜ create" not in clean_stdout, "smoke should not create (shared-state)"
    assert "smoke ➜ destroy" not in clean_stdout, "smoke should not destroy (shared-state)"

    # === VALIDATE REPORT OUTPUT (what users see at the end) ===

    # Extract the Details section (everything after "DETAILS") and strip ANSI codes
    details_start = clean_stderr.find("DETAILS")
    details_section = clean_stderr[details_start:] if details_start != -1 else ""

    # Expected report format - exact match what users see
    expected_report = """DETAILS
default ➜ create: Completed: Successful

test-scenario ➜ dependency: Completed: 2 missing (Remove from test_sequence to suppress)
test-scenario ➜ cleanup: Completed: Missing playbook (Remove from test_sequence to suppress)
test-scenario ➜ syntax: Completed: Successful
test-scenario ➜ prepare: Completed: Missing playbook (Remove from test_sequence to suppress)
test-scenario ➜ converge: Completed: Successful
test-scenario ➜ idempotence: Completed: Successful
test-scenario ➜ side_effect: Completed: Missing playbook (Remove from test_sequence to suppress)
test-scenario ➜ verify: Completed: Missing playbook (Remove from test_sequence to suppress)
test-scenario ➜ cleanup: Completed: Missing playbook (Remove from test_sequence to suppress)

smoke ➜ dependency: Completed: 2 missing (Remove from test_sequence to suppress)
smoke ➜ cleanup: Completed: Missing playbook (Remove from test_sequence to suppress)
smoke ➜ syntax: Completed: Successful
smoke ➜ prepare: Completed: Missing playbook (Remove from test_sequence to suppress)
smoke ➜ converge: Completed: Successful
smoke ➜ idempotence: Completed: Successful
smoke ➜ side_effect: Completed: Missing playbook (Remove from test_sequence to suppress)
smoke ➜ verify: Completed: Missing playbook (Remove from test_sequence to suppress)
smoke ➜ cleanup: Completed: Missing playbook (Remove from test_sequence to suppress)

default ➜ destroy: Completed: Successful

SCENARIO RECAP
default                   : actions=1  successful=1  disabled=0  skipped=0  missing=0  failed=0
test-scenario             : actions=9  successful=3  disabled=0  skipped=0  missing=7  failed=0
smoke                     : actions=9  successful=3  disabled=0  skipped=0  missing=7  failed=0
default                   : actions=1  successful=1  disabled=0  skipped=0  missing=0  failed=0

"""

    # Direct string comparison - exact match
    normalized_details = normalize_report_whitespace(details_section)
    normalized_expected = normalize_report_whitespace(expected_report)

    if normalized_details != normalized_expected:
        # Provide detailed diff for easier debugging
        diff_lines = list(
            difflib.unified_diff(
                normalized_expected.splitlines(keepends=True),
                normalized_details.splitlines(keepends=True),
                fromfile="expected",
                tofile="actual",
                lineterm="",
            ),
        )
        diff_text = "".join(diff_lines)

        pytest.fail(
            f"Report content mismatch:\n\n"
            f"=== UNIFIED DIFF ===\n{diff_text}\n\n"
            f"=== RAW COMPARISON ===\n"
            f"Expected ({len(normalized_expected)} chars):\n{normalized_expected!r}\n\n"
            f"Actual ({len(normalized_details)} chars):\n{normalized_details!r}",
        )


def test_ui_formatting(
    monkeypatch: pytest.MonkeyPatch,
    test_fixture_dir: Path,
) -> None:
    """Test that UI formatting shows clear starting and completion messages.

    Args:
        monkeypatch: Pytest fixture.
        test_fixture_dir: Path to the test fixture directory.
    """
    monkeypatch.chdir(test_fixture_dir)

    # Ensure consistent output format by removing GitHub-specific environment variables
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("CI", raising=False)

    # Override the autouse _no_color fixture to enable markup for this test
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")

    cmd = [
        "molecule",
        "test",
        "-s",
        "smoke",
        "--report",
    ]
    result = run(cmd=cmd)
    assert result.returncode == 0, result

    _stdout_output = result.stdout
    stderr_output = result.stderr

    # Strip ANSI escape codes for assertions
    clean_stderr = strip_ansi_escape(stderr_output)

    # === VALIDATE STARTING MESSAGES ===

    # Check for clear starting indicators that users see (in stderr)
    assert "INFO     smoke ➜ dependency: Starting" in clean_stderr, (
        "Should show dependency starting message"
    )
    assert "INFO     smoke ➜ create: Starting" in clean_stderr, (
        "Should show create starting message"
    )
    assert "INFO     smoke ➜ prepare: Starting" in clean_stderr, (
        "Should show prepare starting message"
    )
    assert "INFO     smoke ➜ converge: Starting" in clean_stderr, (
        "Should show converge starting message"
    )
    assert "INFO     smoke ➜ verify: Starting" in clean_stderr, (
        "Should show verify starting message"
    )
    assert "INFO     smoke ➜ destroy: Starting" in clean_stderr, (
        "Should show destroy starting message"
    )

    # === VALIDATE COMPLETION MESSAGES ===

    # Check for completion messages that users see during execution (in stderr)
    assert "smoke ➜ dependency: Completed:" in clean_stderr, "Should show dependency completion"
    assert "smoke ➜ create: Completed:" in clean_stderr, "Should show create completion"
    assert "smoke ➜ prepare: Completed:" in clean_stderr, "Should show prepare completion"
    assert "smoke ➜ converge: Completed:" in clean_stderr, "Should show converge completion"
    assert "smoke ➜ verify: Completed:" in clean_stderr, "Should show verify completion"
    assert "smoke ➜ destroy: Completed:" in clean_stderr, "Should show destroy completion"

    # === VALIDATE REPORT SUMMARY ===

    # Extract the Details section from stderr and strip ANSI codes
    details_start = clean_stderr.find("DETAILS")
    details_section = clean_stderr[details_start:] if details_start != -1 else ""

    # Expected report shows final status
    expected_report = """DETAILS
smoke ➜ dependency: Completed: 2 missing (Remove from test_sequence to suppress)
smoke ➜ cleanup: Completed: Missing playbook (Remove from test_sequence to suppress)
smoke ➜ destroy: Completed: Missing playbook (Remove from test_sequence to suppress)
smoke ➜ syntax: Completed: Successful
smoke ➜ create: Completed: Missing playbook (Remove from test_sequence to suppress)
smoke ➜ prepare: Completed: Missing playbook (Remove from test_sequence to suppress)
smoke ➜ converge: Completed: Successful
smoke ➜ idempotence: Completed: Successful
smoke ➜ side_effect: Completed: Missing playbook (Remove from test_sequence to suppress)
smoke ➜ verify: Completed: Missing playbook (Remove from test_sequence to suppress)
smoke ➜ cleanup: Completed: Missing playbook (Remove from test_sequence to suppress)
smoke ➜ destroy: Completed: Missing playbook (Remove from test_sequence to suppress)

SCENARIO RECAP
smoke                     : actions=12  successful=3  disabled=0  skipped=0  missing=10  failed=0

"""

    # Validate final report matches execution
    normalized_details = normalize_report_whitespace(details_section)
    normalized_expected = normalize_report_whitespace(expected_report)

    if normalized_details != normalized_expected:
        # Provide detailed diff for easier debugging
        diff_lines = list(
            difflib.unified_diff(
                normalized_expected.splitlines(keepends=True),
                normalized_details.splitlines(keepends=True),
                fromfile="expected",
                tofile="actual",
                lineterm="",
            ),
        )
        diff_text = "".join(diff_lines)

        pytest.fail(
            f"Report summary mismatch:\n\n"
            f"=== UNIFIED DIFF ===\n{diff_text}\n\n"
            f"=== RAW COMPARISON ===\n"
            f"Expected ({len(normalized_expected)} chars):\n{normalized_expected!r}\n\n"
            f"Actual ({len(normalized_details)} chars):\n{normalized_details!r}",
        )

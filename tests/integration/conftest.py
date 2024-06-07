#  Copyright (c) 2015-2018 Cisco Systems, Inc.  # noqa: D100
#  Copyright (c) 2018 Red Hat, Inc.
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
import shutil
import subprocess

from subprocess import PIPE
from typing import TYPE_CHECKING

import pexpect
import pytest

from ansible_compat.ports import cache
from packaging.version import Version

import molecule

from molecule import logger, util
from molecule.app import app
from molecule.text import strip_ansi_color
from molecule.util import run_command
from tests.conftest import change_dir_to, molecule_directory  # pylint:disable=C0411


if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


LOG = logger.get_logger(__name__)

IS_TRAVIS = os.getenv("TRAVIS") and os.getenv("CI")
# requires >=1.5.1 due to missing cp command, we tested with 1.4.2-stable3 and
# it failed, see https://bugzilla.redhat.com/show_bug.cgi?id=1759713
MIN_PODMAN_VERSION = "1.5.1"


@pytest.fixture(scope="session", autouse=True)
def require_installed_package():  # type: ignore[no-untyped-def]  # noqa: ANN201, PT004, D103
    try:
        molecule.__version__  # noqa: B018
    except Exception as e:  # noqa: BLE001
        pytest.fail(f"Functional tests require molecule package to be installed: {e}")


def _env_vars_exposed(env_vars, env=os.environ):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN202, ARG001
    """Check if environment variables are exposed and populated."""
    for env_var in env_vars:
        if env_var not in os.environ:
            return False
        return bool(os.environ[env_var])
    return None


@pytest.fixture(name="with_scenario")
def _with_scenario(
    scenario_to_test: str,
    driver_name: str,
    scenario_name: str,
    skip_test: bool,  # noqa: ARG001, FBT001
    test_fixture_dir: Path,
) -> Iterator[None]:
    """Yield to test with a scenario, changes dir and does cleanup.

    Args:
        scenario_to_test: The scenario to test.
        driver_name: The driver name.
        scenario_name: The scenario name.
        skip_test: Skip the test.
        test_fixture_dir: The test fixture directory.

    Yields:
        None:
    """
    scenario_directory = test_fixture_dir / "scenarios" / scenario_to_test

    with change_dir_to(scenario_directory):
        yield
        if scenario_name:
            msg = "CLEANUP: Destroying instances for all scenario(s)"
            LOG.info(msg)
            cmd = ["molecule", "destroy", "--driver-name", driver_name, "--all"]
            assert run_command(cmd).returncode == 0


@pytest.fixture(name="skip_test")
def fixture_skip_test(request, driver_name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT004, ARG001, D103
    msg_tmpl = "Skipped '{}' not supported"
    support_checks_map = {
        "default": lambda: True,
    }
    try:
        check_func = support_checks_map[driver_name]
        if not check_func():  # type: ignore[no-untyped-call]
            pytest.skip(msg_tmpl.format(driver_name))
    except KeyError:
        pass


def idempotence(scenario_name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    cmd = ["molecule", "create", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0

    cmd = ["molecule", "converge", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0

    cmd = ["molecule", "idempotence", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0


def init_scenario(temp_dir, driver_name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    with change_dir_to(temp_dir.strpath):
        # Create scenario
        molecule_dir = molecule_directory()
        scenario_directory = os.path.join(molecule_dir, "test-scenario")  # noqa: PTH118

        cmd = [
            "molecule",
            "init",
            "scenario",
            "test-scenario",
            "--driver-name",
            driver_name,
        ]
        assert run_command(cmd).returncode == 0

        assert os.path.isdir(scenario_directory)  # noqa: PTH112

        cmd = ["molecule", "test", "--scenario-name", "test-scenario", "--all"]
        assert run_command(cmd).returncode == 0


def metadata_lint_update(role_directory: str) -> None:  # noqa: D103
    # By default, ansible-lint will fail on newly-created roles because the
    # fields in this file have not been changed from their defaults. This is
    # good because molecule should create this file using the defaults, and
    # users should receive feedback to change these defaults. However, this
    # blocks the testing of 'molecule init' itself, so ansible-lint should
    # be configured to ignore these metadata lint errors.
    dirname = os.path.dirname(os.path.abspath(__file__))  # noqa: PTH100, PTH120
    ansible_lint_src = os.path.join(dirname, ".ansible-lint")  # noqa: PTH118
    shutil.copy(ansible_lint_src, role_directory)

    # Explicitly lint here to catch any unexpected lint errors before
    # continuing functional testing. Ansible lint is run at the root
    # of the role directory and pointed at the role directory to ensure
    # the customize ansible-lint config is used.
    with change_dir_to(role_directory):
        cmd = ["ansible-lint", "."]
        result = run_command(cmd)
    assert result.returncode == 0


def list_cmd(x):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    cmd = ["molecule", "list"]
    result = run_command(cmd)
    assert result.returncode == 0
    out = util.strip_ansi_color(result.stdout)  # type: ignore[attr-defined] # pylint:disable=no-member

    for l in x.splitlines():  # noqa: E741
        assert l in out


def list_with_format_plain(x):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    cmd = ["molecule", "list", "--format", "plain"]
    result = util.run_command(cmd)
    out = strip_ansi_color(result.stdout)  # type: ignore[no-untyped-call]

    for l in x.splitlines():  # noqa: E741
        assert l in out


def login(login_args, scenario_name="default"):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    cmd = ["molecule", "destroy", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0

    cmd = ["molecule", "create", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0

    for instance, regexp in login_args:
        if len(login_args) > 1:
            child_cmd = f"molecule login --host {instance} --scenario-name {scenario_name}"
        else:
            child_cmd = f"molecule login --scenario-name {scenario_name}"
        child = pexpect.spawn(child_cmd)
        child.expect(regexp)
        # If the test returns and doesn't hang it succeeded.
        child.sendline("exit")


def run_test(driver_name, scenario_name="default", parallel=False):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, FBT002, D103
    cmd = ["molecule", "test", "--scenario-name", scenario_name]
    if driver_name != "default":
        if scenario_name is None:
            cmd.append("--all")
        if parallel:
            cmd.append("--parallel")

    assert run_command(cmd).returncode == 0


def verify(scenario_name="default"):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    cmd = ["molecule", "create", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0

    cmd = ["molecule", "converge", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0

    cmd = ["molecule", "verify", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0


def get_docker_executable() -> str | None:  # noqa: D103
    return shutil.which("docker")


def get_virtualbox_executable():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    return shutil.which("VBoxManage")


@cache
def supports_docker() -> bool:  # noqa: D103
    docker = get_docker_executable()
    if docker:
        result = subprocess.run(
            [docker, "info"],  # noqa: S603
            stdout=PIPE,
            text=True,
            check=True,
        )  # Explicitly set check=True
        if result.returncode != 0:
            LOG.error(
                "Error %s returned from `docker info`: %s",
                result.returncode,
                result.stdout,
            )
            return False
        if "BuildahVersion" in result.stdout:
            LOG.error(
                "podman-docker is unsupported, see https://github.com/ansible-community/molecule/issues/2456",
            )
            return False
    return True


def min_ansible(version: str) -> bool:
    """Ensure current Ansible is newer than a given a minimal one."""
    return bool(app.runtime.version >= Version(version))

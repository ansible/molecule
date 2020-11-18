#  Copyright (c) 2015-2018 Cisco Systems, Inc.
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

import os
import shutil
import subprocess
from subprocess import PIPE

import pexpect
import pkg_resources
import pytest

from molecule import logger, util
from molecule.config import ansible_version
from molecule.test.conftest import change_dir_to
from molecule.text import strip_ansi_color
from molecule.util import run_command

LOG = logger.get_logger(__name__)

IS_TRAVIS = os.getenv("TRAVIS") and os.getenv("CI")
# requires >=1.5.1 due to missing cp command, we tested with 1.4.2-stable3 and
# it failed, see https://bugzilla.redhat.com/show_bug.cgi?id=1759713
MIN_PODMAN_VERSION = "1.5.1"


@pytest.fixture(scope="session", autouse=True)
def require_installed_package():
    try:
        pkg_resources.require("molecule")
    except pkg_resources.DistributionNotFound as e:
        pytest.fail(
            "Functional tests require molecule package to be installed: {}".format(e)
        )


def _env_vars_exposed(env_vars, env=os.environ):
    """Check if environment variables are exposed and populated."""
    for env_var in env_vars:
        if env_var not in os.environ:
            return False
        return os.environ[env_var] != ""


@pytest.fixture
def with_scenario(request, scenario_to_test, driver_name, scenario_name, skip_test):
    scenario_directory = os.path.join(
        os.path.dirname(util.abs_path(__file__)),
        os.path.pardir,
        "scenarios",
        scenario_to_test,
    )

    with change_dir_to(scenario_directory):
        yield
        if scenario_name:
            msg = "CLEANUP: Destroying instances for all scenario(s)"
            LOG.info(msg)
            cmd = ["molecule", "destroy", "--driver-name", driver_name, "--all"]
            assert run_command(cmd).returncode == 0


@pytest.fixture
def skip_test(request, driver_name):
    msg_tmpl = "Skipped '{}' not supported"
    support_checks_map = {
        "delegated": lambda: True,
    }
    try:
        check_func = support_checks_map[driver_name]
        if not check_func():
            pytest.skip(msg_tmpl.format(driver_name))
    except KeyError:
        pass


@pytest.helpers.register
def idempotence(scenario_name):
    cmd = ["molecule", "create", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0

    cmd = ["molecule", "converge", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0

    cmd = ["molecule", "idempotence", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0


@pytest.helpers.register
def init_role(temp_dir, driver_name):
    role_directory = os.path.join(temp_dir.strpath, "test-init")

    cmd = ["molecule", "init", "role", "test-init", "--driver-name", driver_name]
    assert run_command(cmd).returncode == 0
    pytest.helpers.metadata_lint_update(role_directory)

    with change_dir_to(role_directory):
        cmd = ["molecule", "test", "--all"]
        assert run_command(cmd).returncode == 0


@pytest.helpers.register
def init_scenario(temp_dir, driver_name):
    # Create role
    role_directory = os.path.join(temp_dir.strpath, "test-init")
    cmd = ["molecule", "init", "role", "test-init", "--driver-name", driver_name]
    assert run_command(cmd).returncode == 0
    pytest.helpers.metadata_lint_update(role_directory)

    with change_dir_to(role_directory):
        # Create scenario
        molecule_directory = pytest.helpers.molecule_directory()
        scenario_directory = os.path.join(molecule_directory, "test-scenario")

        cmd = [
            "molecule",
            "init",
            "scenario",
            "test-scenario",
            "--role-name",
            "test-init",
            "--driver-name",
            driver_name,
        ]
        assert run_command(cmd).returncode == 0

        assert os.path.isdir(scenario_directory)

        cmd = ["molecule", "test", "--scenario-name", "test-scenario", "--all"]
        assert run_command(cmd).returncode == 0


@pytest.helpers.register
def metadata_lint_update(role_directory):
    # By default, ansible-lint will fail on newly-created roles because the
    # fields in this file have not been changed from their defaults. This is
    # good because molecule should create this file using the defaults, and
    # users should receive feedback to change these defaults. However, this
    # blocks the testing of 'molecule init' itself, so ansible-lint should
    # be configured to ignore these metadata lint errors.
    ansible_lint_src = os.path.join(
        os.path.dirname(util.abs_path(__file__)), ".ansible-lint"
    )
    shutil.copy(ansible_lint_src, role_directory)

    # Explicitly lint here to catch any unexpected lint errors before
    # continuining functional testing. Ansible lint is run at the root
    # of the role directory and pointed at the role directory to ensure
    # the customize ansible-lint config is used.
    with change_dir_to(role_directory):
        cmd = ["ansible-lint", "."]
    assert run_command(cmd).returncode == 0


@pytest.helpers.register
def list(x):
    cmd = ["molecule", "list"]
    result = run_command(cmd)
    assert result.returncode == 0
    out = util.strip_ansi_color(result.stdout)

    for l in x.splitlines():
        assert l in out


@pytest.helpers.register
def list_with_format_plain(x):
    cmd = ["molecule", "list", "--format", "plain"]
    result = util.run_command(cmd)
    out = strip_ansi_color(result.stdout)

    for l in x.splitlines():
        assert l in out


@pytest.helpers.register
def login(login_args, scenario_name="default"):
    cmd = ["molecule", "destroy", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0

    cmd = ["molecule", "create", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0

    for instance, regexp in login_args:
        if len(login_args) > 1:
            child_cmd = "molecule login --host {} --scenario-name {}".format(
                instance, scenario_name
            )
        else:
            child_cmd = "molecule login --scenario-name {}".format(scenario_name)
        child = pexpect.spawn(child_cmd)
        child.expect(regexp)
        # If the test returns and doesn't hang it succeeded.
        child.sendline("exit")


@pytest.helpers.register
def test(driver_name, scenario_name="default", parallel=False):
    cmd = ["molecule", "test", "--scenario-name", scenario_name]
    if driver_name != "delegated":
        if scenario_name is None:
            cmd.append("--all")
        if parallel:
            cmd.append("--parallel")

    assert run_command(cmd).returncode == 0


@pytest.helpers.register
def verify(scenario_name="default"):
    cmd = ["molecule", "create", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0

    cmd = ["molecule", "converge", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0

    cmd = ["molecule", "verify", "--scenario-name", scenario_name]
    assert run_command(cmd).returncode == 0


def get_docker_executable():
    return shutil.which("docker")


def get_virtualbox_executable():
    return shutil.which("VBoxManage")


@pytest.helpers.register
@util.lru_cache()
def supports_docker():
    docker = get_docker_executable()
    if docker:
        result = subprocess.run([docker, "info"], stdout=PIPE, universal_newlines=True)
        if result.returncode != 0:
            LOG.error(
                "Error %s returned from `docker info`: %s",
                result.returncode,
                result.stdout,
            )
            return False
        if "BuildahVersion" in result.stdout:
            LOG.error(
                "podman-docker is unsupported, see https://github.com/ansible-community/molecule/issues/2456"
            )
            return False
    return True


def min_ansible(version: str) -> bool:
    """Ensure current Ansible is newer than a given a minimal one."""
    return ansible_version() >= ansible_version(version)

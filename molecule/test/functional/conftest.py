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

import distutils.spawn
import os
import pkg_resources
import shutil

import pexpect
import pytest
import sh

from molecule import logger
from molecule import util

from ..conftest import change_dir_to

LOG = logger.get_logger(__name__)

IS_TRAVIS = os.getenv('TRAVIS') and os.getenv('CI')


def _env_vars_exposed(env_vars, env=os.environ):
    """Check if environment variables are exposed and populated."""
    for env_var in env_vars:
        if env_var not in os.environ:
            return False
        return os.environ[env_var] != ''


@pytest.fixture
def with_scenario(request, scenario_to_test, driver_name, scenario_name, skip_test):
    scenario_directory = os.path.join(
        os.path.dirname(util.abs_path(__file__)),
        os.path.pardir,
        'scenarios',
        scenario_to_test,
    )

    with change_dir_to(scenario_directory):
        yield
        if scenario_name:
            msg = 'CLEANUP: Destroying instances for all scenario(s)'
            LOG.out(msg)
            options = {'driver_name': driver_name, 'all': True}
            cmd = sh.molecule.bake('destroy', **options)
            pytest.helpers.run_command(cmd)


@pytest.fixture
def skip_test(request, driver_name):
    msg_tmpl = (
        "Ignoring '{}' tests for now"
        if driver_name == 'delegated'
        else "Skipped '{}' not supported"
    )
    support_checks_map = {
        'docker': supports_docker,
        'podman': lambda: min_ansible("2.8.6"),
        'vagrant': supports_vagrant_virtualbox,
        'delegated': demands_delegated,
    }
    try:
        check_func = support_checks_map[driver_name]
        if not check_func():
            pytest.skip(msg_tmpl.format(driver_name))
    except KeyError:
        pass


@pytest.helpers.register
def idempotence(scenario_name):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('create', **options)
    pytest.helpers.run_command(cmd)

    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('converge', **options)
    pytest.helpers.run_command(cmd)

    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('idempotence', **options)
    pytest.helpers.run_command(cmd)


@pytest.helpers.register
def init_role(temp_dir, driver_name):
    role_directory = os.path.join(temp_dir.strpath, 'test-init')

    cmd = sh.molecule.bake(
        'init', 'role', {'driver-name': driver_name, 'role-name': 'test-init'}
    )
    pytest.helpers.run_command(cmd)
    pytest.helpers.metadata_lint_update(role_directory)

    with change_dir_to(role_directory):
        options = {'all': True}
        cmd = sh.molecule.bake('test', **options)
        pytest.helpers.run_command(cmd)


@pytest.helpers.register
def init_scenario(temp_dir, driver_name):
    # Create role
    role_directory = os.path.join(temp_dir.strpath, 'test-init')
    cmd = sh.molecule.bake(
        'init', 'role', {'driver-name': driver_name, 'role-name': 'test-init'}
    )
    pytest.helpers.run_command(cmd)
    pytest.helpers.metadata_lint_update(role_directory)

    with change_dir_to(role_directory):
        # Create scenario
        molecule_directory = pytest.helpers.molecule_directory()
        scenario_directory = os.path.join(molecule_directory, 'test-scenario')

        options = {'scenario_name': 'test-scenario', 'role_name': 'test-init'}
        cmd = sh.molecule.bake('init', 'scenario', **options)
        pytest.helpers.run_command(cmd)

        assert os.path.isdir(scenario_directory)

        options = {'scenario_name': 'test-scenario', 'all': True}
        cmd = sh.molecule.bake('test', **options)
        pytest.helpers.run_command(cmd)


@pytest.helpers.register
def metadata_lint_update(role_directory):
    # By default, ansible-lint will fail on newly-created roles because the
    # fields in this file have not been changed from their defaults. This is
    # good because molecule should create this file using the defaults, and
    # users should receive feedback to change these defaults. However, this
    # blocks the testing of 'molecule init' itself, so ansible-lint should
    # be configured to ignore these metadata lint errors.
    ansible_lint_src = os.path.join(
        os.path.dirname(util.abs_path(__file__)), '.ansible-lint'
    )
    shutil.copy(ansible_lint_src, role_directory)

    # Explicitly lint here to catch any unexpected lint errors before
    # continuining functional testing. Ansible lint is run at the root
    # of the role directory and pointed at the role directory to ensure
    # the customize ansible-lint config is used.
    with change_dir_to(role_directory):
        cmd = sh.ansible_lint.bake('.')
    pytest.helpers.run_command(cmd)


@pytest.helpers.register
def list(x):
    cmd = sh.molecule.bake('list')
    out = pytest.helpers.run_command(cmd, log=False)
    out = out.stdout.decode('utf-8')
    out = util.strip_ansi_color(out)

    for l in x.splitlines():
        assert l in out


@pytest.helpers.register
def list_with_format_plain(x):
    cmd = sh.molecule.bake('list', {'format': 'plain'})
    out = pytest.helpers.run_command(cmd, log=False)
    out = out.stdout.decode('utf-8')
    out = util.strip_ansi_color(out)

    for l in x.splitlines():
        assert l in out


@pytest.helpers.register
def login(login_args, scenario_name='default'):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('destroy', **options)
    pytest.helpers.run_command(cmd)

    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('create', **options)
    pytest.helpers.run_command(cmd)

    for instance, regexp in login_args:
        if len(login_args) > 1:
            child_cmd = 'molecule login --host {} --scenario-name {}'.format(
                instance, scenario_name
            )
        else:
            child_cmd = 'molecule login --scenario-name {}'.format(scenario_name)
        child = pexpect.spawn(child_cmd)
        child.expect(regexp)
        # If the test returns and doesn't hang it succeeded.
        child.sendline('exit')


@pytest.helpers.register
def test(driver_name, scenario_name='default', parallel=False):
    options = {
        'scenario_name': scenario_name,
        'all': scenario_name is None,
        'parallel': parallel,
    }

    if driver_name == 'delegated':
        options = {'scenario_name': scenario_name}

    cmd = sh.molecule.bake('test', **options)
    pytest.helpers.run_command(cmd)


@pytest.helpers.register
def verify(scenario_name='default'):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('create', **options)
    pytest.helpers.run_command(cmd)

    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('converge', **options)
    pytest.helpers.run_command(cmd)

    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('verify', **options)
    pytest.helpers.run_command(cmd)


def get_docker_executable():
    return distutils.spawn.find_executable('docker')


def get_vagrant_executable():
    return distutils.spawn.find_executable('vagrant')


def get_virtualbox_executable():
    return distutils.spawn.find_executable('VBoxManage')


@pytest.helpers.register
def supports_docker():
    return get_docker_executable()


def min_ansible(version):
    """Ensure current Ansible is newer than a given a minimal one."""
    try:
        from ansible.release import __version__

        return pkg_resources.parse_version(__version__) >= pkg_resources.parse_version(
            version
        )
    except ImportError as exception:
        LOG.error('Unable to parse Ansible version', exc_info=exception)
        return False


@pytest.helpers.register
def supports_vagrant_virtualbox():
    return get_vagrant_executable() or get_virtualbox_executable()


@pytest.helpers.register
def demands_delegated():
    return pytest.config.getoption('--delegated')

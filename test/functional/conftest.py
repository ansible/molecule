#  Copyright (c) 2015-2017 Cisco Systems, Inc.
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

import pexpect
import pytest
import sh

from molecule import logger
from molecule import util

LOG = logger.get_logger(__name__)


@pytest.fixture
def with_scenario(request, scenario_to_test, driver_name, scenario_name,
                  skip_test):
    scenario_directory = os.path.join(
        os.path.dirname(util.abs_path(__file__)), os.path.pardir, 'scenarios',
        scenario_to_test)

    os.chdir(scenario_directory)

    def cleanup():
        if scenario_name:
            msg = 'CLEANUP: Destroying instances for all scenario(s)'
            LOG.out(msg)
            options = {
                'driver_name': driver_name,
                'all': True,
            }
            cmd = sh.molecule.bake('destroy', **options)
            run_command(cmd)

    request.addfinalizer(cleanup)


@pytest.fixture
def skip_test(request, driver_name):
    if (driver_name == 'docker' and not supports_docker()):
        pytest.skip("Skipped '{}' not supported".format(driver_name))
    elif (driver_name == 'lxc' and not supports_lxc()):
        pytest.skip("skipped '{}' not supported".format(driver_name))
    elif (driver_name == 'lxd' and not supports_lxd()):
        pytest.skip("Skipped '{}' not supported".format(driver_name))
    elif (driver_name == 'vagrant' and not supports_vagrant_virtualbox()):
        pytest.skip("Skipped '{}' not supported".format(driver_name))
    elif driver_name == 'delegated':
        if not pytest.config.getoption('--delegated'):
            pytest.skip("Ignoring '{}' tests for now".format(driver_name))


@pytest.helpers.register
def idempotence(scenario_name):
    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('create', **options)
    run_command(cmd)

    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('converge', **options)
    run_command(cmd)

    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('idempotence', **options)
    run_command(cmd)


@pytest.helpers.register
def init_role(temp_dir, driver_name):
    role_directory = os.path.join(temp_dir.strpath, 'test-init')

    cmd = sh.molecule.bake(
        'init', 'role', {'driver-name': driver_name,
                         'role-name': 'test-init'})
    run_command(cmd)

    os.chdir(role_directory)
    options = {
        'all': True,
    }
    cmd = sh.molecule.bake('test', **options)
    run_command(cmd)


@pytest.helpers.register
def init_scenario(temp_dir, driver_name):
    # Create role
    role_directory = os.path.join(temp_dir.strpath, 'test-init')
    cmd = sh.molecule.bake(
        'init', 'role', {'driver-name': driver_name,
                         'role-name': 'test-init'})
    run_command(cmd)
    os.chdir(role_directory)

    # Create scenario
    molecule_directory = pytest.helpers.molecule_directory()
    scenario_directory = os.path.join(molecule_directory, 'test-scenario')

    options = {
        'scenario_name': 'test-scenario',
        'role_name': 'test-init',
    }
    cmd = sh.molecule.bake('init', 'scenario', **options)
    run_command(cmd)

    assert os.path.isdir(scenario_directory)

    options = {
        'scenario_name': 'test-scenario',
        'all': True,
    }
    cmd = sh.molecule.bake('test', **options)
    run_command(cmd)


@pytest.helpers.register
def list(x):
    cmd = sh.molecule.bake('list')
    out = run_command(cmd, log=False)
    out = out.stdout
    out = util.strip_ansi_color(out)

    assert x in out


@pytest.helpers.register
def list_with_format_plain(x):
    cmd = sh.molecule.bake('list', {'format': 'plain'})
    out = run_command(cmd, log=False)
    out = out.stdout
    out = util.strip_ansi_color(out)

    assert x in out


@pytest.helpers.register
def login(login_args, scenario_name='default'):
    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('destroy', **options)
    run_command(cmd)

    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('create', **options)
    run_command(cmd)

    for instance, regexp in login_args:
        if len(login_args) > 1:
            child_cmd = 'molecule login --host {} --scenario-name {}'.format(
                instance, scenario_name)
        else:
            child_cmd = 'molecule login --scenario-name {}'.format(
                scenario_name)
        child = pexpect.spawn(child_cmd)
        child.expect(regexp)
        # If the test returns and doesn't hang it succeeded.
        child.sendline('exit')


@pytest.helpers.register
def test(driver_name, scenario_name='default'):
    options = {
        'scenario_name': scenario_name,
        'all': True,
    }

    if driver_name == 'delegated':
        options = {
            'scenario_name': scenario_name,
        }

    cmd = sh.molecule.bake('test', **options)
    run_command(cmd)


@pytest.helpers.register
def verify(scenario_name='default'):
    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('create', **options)
    run_command(cmd)

    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('converge', **options)
    run_command(cmd)

    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('verify', **options)
    run_command(cmd)


@pytest.helpers.register
def run_command(cmd, env=os.environ, log=True):
    if log:
        cmd = _rebake_command(cmd, env)

    return util.run_command(cmd)


def _rebake_command(cmd, env, out=LOG.out, err=LOG.error):
    return cmd.bake(_env=env, _out=out, _err=err)


def get_docker_executable():
    return distutils.spawn.find_executable('docker')


def get_lxc_executable():
    return distutils.spawn.find_executable('lxc-start')


def get_lxd_executable():
    return distutils.spawn.find_executable('lxd')


def get_vagrant_executable():
    return distutils.spawn.find_executable('vagrant')


def get_virtualbox_executable():
    return distutils.spawn.find_executable('VBoxManage')


@pytest.helpers.register
def supports_docker():
    return get_docker_executable()


@pytest.helpers.register
def supports_lxc():
    return get_lxc_executable()


@pytest.helpers.register
def supports_lxd():
    return get_lxd_executable()


@pytest.helpers.register
def supports_vagrant_virtualbox():
    return (get_vagrant_executable() or get_virtualbox_executable())

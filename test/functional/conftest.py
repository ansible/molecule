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

import os

import pexpect
import pytest
import sh

from molecule import config
from molecule import logger
from molecule import util

LOG = logger.get_logger(__name__)


@pytest.fixture()
def with_scenario(request):
    scenario = request.param
    scenario_directory = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), os.path.pardir,
        'scenarios', scenario)

    os.chdir(scenario_directory)

    # Cleanup only running instances.
    def cleanup():
        out = sh.molecule('list', '--format', 'yaml')
        out = out.stdout
        out = util.strip_ansi_color(out)
        results = util.safe_load(out)

        instances_dict = [
            result for result in results if result['Created'] == 'True'
        ]
        for scenario_name in {
                instance_dict['Scenario Name']
                for instance_dict in instances_dict
        }:
            msg = "CLEANUP: Destroying instances for '{}' scenario".format(
                scenario_name)
            LOG.out(msg)
            sh.molecule('destroy', '--scenario-name', scenario_name)

    request.addfinalizer(cleanup)


@pytest.helpers.register
def check(scenario_name='default'):
    cmd = sh.molecule.bake('check', '--scenario-name', scenario_name)
    run_command(cmd)


@pytest.helpers.register
def converge(scenario_name='default'):
    cmd = sh.molecule.bake('converge', '--scenario-name', scenario_name)
    run_command(cmd)


@pytest.helpers.register
def create(scenario_name='default'):
    cmd = sh.molecule.bake('create', '--scenario-name', scenario_name)
    run_command(cmd)


@pytest.helpers.register
def dependency_ansible_galaxy(scenario_name='default'):
    cmd = sh.molecule.bake('dependency', '--scenario-name', 'ansible-galaxy')
    run_command(cmd)

    dependency_role = os.path.join('molecule', 'ansible-galaxy', '.molecule',
                                   'roles', 'timezone')
    assert os.path.isdir(dependency_role)


@pytest.helpers.register
def dependency_gilt(scenario_name='default'):
    cmd = sh.molecule.bake('dependency', '--scenario-name', 'gilt')
    run_command(cmd)

    dependency_role = os.path.join('molecule', 'ansible-galaxy', '.molecule',
                                   'roles', 'timezone')
    assert os.path.isdir(dependency_role)


@pytest.helpers.register
def destroy(scenario_name='default'):
    cmd = sh.molecule.bake('destroy', '--scenario-name', scenario_name)
    run_command(cmd)


@pytest.helpers.register
def idempotence(scenario_name='default'):
    cmd = sh.molecule.bake('create', '--scenario-name', scenario_name)
    run_command(cmd)

    cmd = sh.molecule.bake('converge', '--scenario-name', scenario_name)
    run_command(cmd)

    cmd = sh.molecule.bake('idempotence', '--scenario-name', scenario_name)
    run_command(cmd)


@pytest.helpers.register
def init_role(temp_dir, scenario_name='default'):
    role_directory = os.path.join(temp_dir.strpath, 'test-init')

    cmd = sh.molecule.bake('init', 'role', '--role-name', 'test-init')
    run_command(cmd)

    os.chdir(role_directory)
    cmd = sh.molecule.bake('test')
    run_command(cmd)


@pytest.helpers.register
def init_scenario(temp_dir, scenario_name='default'):
    # Create role
    role_directory = os.path.join(temp_dir.strpath, 'test-init')
    cmd = sh.molecule.bake('init', 'role', '--role-name', 'test-init')
    run_command(cmd)
    os.chdir(role_directory)

    # Create scenario
    molecule_directory = config.molecule_directory(role_directory)
    scenario_directory = os.path.join(molecule_directory, 'test-scenario')

    cmd = sh.molecule.bake('init', 'scenario', '--scenario-name',
                           'test-scenario', '--role-name', 'test-init')
    run_command(cmd)

    assert os.path.isdir(scenario_directory)

    cmd = sh.molecule.bake('test', '--scenario-name', 'test-scenario')
    run_command(cmd)


@pytest.helpers.register
def lint(scenario_name='default'):
    cmd = sh.molecule.bake('lint', '--scenario-name', scenario_name)
    run_command(cmd)


@pytest.helpers.register
def list(x, scenario_name='default'):
    cmd = sh.molecule.bake('list')
    out = run_command(cmd, False)
    out = out.stdout
    out = util.strip_ansi_color(out)

    assert x in out


@pytest.helpers.register
def list_with_format_plain(x, scenario_name='default'):
    cmd = sh.molecule.bake('list', '--format', 'plain')
    out = run_command(cmd, False)
    out = out.stdout
    out = util.strip_ansi_color(out)

    assert x in out


@pytest.helpers.register
def login(instance, regexp, scenario_name='default'):
    cmd = sh.molecule.bake('create', '--scenario-name', scenario_name)
    run_command(cmd)

    child_cmd = 'molecule login --host {} --scenario-name {}'.format(
        instance, scenario_name)
    child = pexpect.spawn(child_cmd)
    child.expect(regexp)
    # If the test returns and doesn't hang it succeeded.
    child.sendline('exit')


@pytest.helpers.register
def syntax(scenario_name='default'):
    cmd = sh.molecule.bake('syntax', '--scenario-name', scenario_name)
    run_command(cmd)


@pytest.helpers.register
def test(scenario_name='default'):
    cmd = sh.molecule.bake('test')
    run_command(cmd)


@pytest.helpers.register
def verify(scenario_name='default'):
    cmd = sh.molecule.bake('create', '--scenario-name', scenario_name)
    run_command(cmd)

    cmd = sh.molecule.bake('converge', '--scenario-name', scenario_name)
    run_command(cmd)

    cmd = sh.molecule.bake('verify', '--scenario-name', scenario_name)
    run_command(cmd)


def run_command(cmd, log=True):
    if log:
        cmd = _rebake_command(cmd)

    return util.run_command(cmd)


def _rebake_command(cmd, out=LOG.out, err=LOG.error, env=os.environ):
    return cmd.bake(_out=out, _err=err, _env=env)

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
from molecule import util


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
            # TODO(retr0h): Remove or properly log.
            print "Calling destroy on '{}' scenario".format(scenario_name)
            sh.molecule('destroy', '--scenario-name', scenario_name)

    request.addfinalizer(cleanup)


@pytest.helpers.register
def check(scenario_name='default'):
    sh.molecule('check', '--scenario-name', scenario_name)


@pytest.helpers.register
def converge(scenario_name='default'):
    sh.molecule('converge', '--scenario-name', scenario_name)


@pytest.helpers.register
def create(scenario_name='default'):
    sh.molecule('create', '--scenario-name', scenario_name)


@pytest.helpers.register
def dependency_ansible_galaxy(scenario_name='default'):
    sh.molecule('dependency', '--scenario-name', 'ansible-galaxy')
    dependency_role = os.path.join('molecule', 'ansible-galaxy', '.molecule',
                                   'roles', 'timezone')
    assert os.path.isdir(dependency_role)


@pytest.helpers.register
def dependency_gilt(scenario_name='default'):
    sh.molecule('dependency', '--scenario-name', 'gilt')

    dependency_role = os.path.join('molecule', 'ansible-galaxy', '.molecule',
                                   'roles', 'timezone')
    assert os.path.isdir(dependency_role)


@pytest.helpers.register
def destroy(scenario_name='default'):
    sh.molecule('destroy', '--scenario-name', scenario_name)


@pytest.helpers.register
def idempotence(scenario_name='default'):
    sh.molecule('create', '--scenario-name', scenario_name)
    sh.molecule('converge', '--scenario-name', scenario_name)
    sh.molecule('idempotence', '--scenario-name', scenario_name)


@pytest.helpers.register
def init_role(temp_dir, scenario_name='default'):
    role_directory = os.path.join(temp_dir.strpath, 'test-init')
    sh.molecule('init', 'role', '--role-name', 'test-init')
    os.chdir(role_directory)

    sh.molecule('test')


@pytest.helpers.register
def init_scenario(temp_dir, scenario_name='default'):
    molecule_directory = config.molecule_directory(temp_dir.strpath)
    scenario_directory = os.path.join(molecule_directory, 'test-scenario')
    sh.molecule('init', 'scenario', '--scenario-name', 'test-scenario',
                '--role-name', 'test-init')

    assert os.path.isdir(scenario_directory)


@pytest.helpers.register
def lint(scenario_name='default'):
    sh.molecule('lint', '--scenario-name', scenario_name)


@pytest.helpers.register
def list(x, scenario_name='default'):
    out = sh.molecule('list')
    out = out.stdout
    out = util.strip_ansi_color(out)

    assert x in out


@pytest.helpers.register
def list_with_format_plain(x, scenario_name='default'):
    out = sh.molecule('list', '--format', 'plain')
    out = out.stdout
    out = util.strip_ansi_color(out)

    assert x in out


@pytest.helpers.register
def login(instance, regexp, scenario_name='default'):
    sh.molecule('create', '--scenario-name', scenario_name)
    child_cmd = 'molecule login --host {} --scenario-name {}'.format(
        instance, scenario_name)
    child = pexpect.spawn(child_cmd)
    child.expect(regexp)
    # If the test returns and doesn't hang it succeeded.
    child.sendline('exit')


@pytest.helpers.register
def syntax(scenario_name='default'):
    sh.molecule('syntax', '--scenario-name', scenario_name)


@pytest.helpers.register
def test(scenario_name='default'):
    sh.molecule('test')


@pytest.helpers.register
def verify(scenario_name='default'):
    sh.molecule('create', '--scenario-name', scenario_name)
    sh.molecule('converge', '--scenario-name', scenario_name)
    sh.molecule('verify', '--scenario-name', scenario_name)

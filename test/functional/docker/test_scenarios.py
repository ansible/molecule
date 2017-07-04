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
import re

import pytest
import sh

from molecule import util


@pytest.fixture
def scenario_to_test(request):
    return request.param


@pytest.fixture
def scenario_name(request):
    try:
        return request.param
    except AttributeError:
        return False


@pytest.fixture
def driver_name(request):
    return request.param


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name', [
        ('destruct', 'docker', 'default'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_destruct(scenario_to_test, with_scenario, scenario_name):
    options = {
        'driver_name': 'docker',
    }
    cmd = sh.molecule.bake('test', **options)
    pytest.helpers.run_command(cmd)


def test_command_init_role_goss(temp_dir):
    role_directory = os.path.join(temp_dir.strpath, 'test-init')
    options = {
        'role_name': 'test-init',
        'verifier_name': 'goss',
    }
    cmd = sh.molecule.bake('init', 'role', **options)
    pytest.helpers.run_command(cmd)

    os.chdir(role_directory)

    sh.molecule('test')


def test_command_init_scenario_goss(temp_dir):
    molecule_directory = pytest.helpers.molecule_directory()
    scenario_directory = os.path.join(molecule_directory, 'test-scenario')
    options = {
        'scenario_name': 'test-scenario',
        'role_name': 'test-init',
        'verifier_name': 'goss',
    }
    cmd = sh.molecule.bake('init', 'scenario', **options)
    pytest.helpers.run_command(cmd)

    assert os.path.isdir(scenario_directory)


def test_command_init_role_with_template(temp_dir):
    role_name = 'test-init'
    role_directory = os.path.join(temp_dir.strpath, role_name)

    options = {
        'url': 'https://github.com/retr0h/cookiecutter-molecule.git',
        'no_input': True,
        'role_name': role_name
    }
    cmd = sh.molecule.bake('init', 'template', **options)
    pytest.helpers.run_command(cmd)

    os.chdir(role_directory)

    sh.molecule('test')


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name', [
        ('overrride_driver', 'docker', 'default'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_test_overrides_driver(scenario_to_test, with_scenario,
                                       driver_name, scenario_name):
    options = {
        'driver_name': driver_name,
    }
    cmd = sh.molecule.bake('test', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name', [
        ('host_group_vars', 'docker', 'default'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_host_group_vars(scenario_to_test, with_scenario, scenario_name):
    cmd = sh.molecule.bake('test')
    out = pytest.helpers.run_command(cmd, log=False)
    out = util.strip_ansi_escape(out.stdout)

    assert re.search('\[all\].*?ok: \[instance\]', out, re.DOTALL)
    assert re.search('\[example\].*?ok: \[instance\]', out, re.DOTALL)
    assert re.search('\[example_1\].*?ok: \[instance\]', out, re.DOTALL)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name', [
        ('idempotence', 'docker', 'raises'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_idempotence_raises(scenario_to_test, with_scenario, scenario_name):
    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('test', **options)
    with pytest.raises(sh.ErrorReturnCode_2) as e:
        pytest.helpers.run_command(cmd)

    assert 2 == e.value.exit_code


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name', [
        ('interpolation', 'docker', 'default'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_interpolation(scenario_to_test, with_scenario, scenario_name):
    # Modify global environment so cleanup inherits our environment.
    env = os.environ
    env.update({'DRIVER_NAME': 'docker'})

    cmd = sh.molecule.bake('test')
    pytest.helpers.run_command(cmd, env=env)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name', [
        ('verifier', 'docker', 'testinfra'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_verify_testinfra(scenario_to_test, with_scenario,
                                  scenario_name):
    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('create', **options)
    pytest.helpers.run_command(cmd)

    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('converge', **options)
    pytest.helpers.run_command(cmd)

    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('verify', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name', [
        ('verifier', 'docker', 'goss'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_verify_goss(scenario_to_test, with_scenario, scenario_name):
    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('create', **options)
    pytest.helpers.run_command(cmd)

    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('converge', **options)
    pytest.helpers.run_command(cmd)

    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('verify', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name', [
        ('plugins', 'docker', 'default'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_plugins(scenario_to_test, with_scenario, scenario_name):
    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('test', **options)
    pytest.helpers.run_command(cmd)

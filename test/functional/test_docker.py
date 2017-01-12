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

import pexpect
import pytest
import sh

from molecule import config


@pytest.mark.parametrize(
    'with_scenario', ['docker'], indirect=['with_scenario'])
def test_command_check(with_scenario):
    sh.molecule('check')


@pytest.mark.parametrize(
    'with_scenario', ['docker'], indirect=['with_scenario'])
def test_command_converge(with_scenario):
    sh.molecule('converge')


@pytest.mark.parametrize(
    'with_scenario', ['docker'], indirect=['with_scenario'])
def test_command_create(with_scenario):
    sh.molecule('create')


@pytest.mark.parametrize(
    'with_scenario', ['ansible-galaxy'], indirect=['with_scenario'])
def test_command_dependency(with_scenario):
    sh.molecule('dependency')


@pytest.mark.parametrize(
    'with_scenario', ['docker'], indirect=['with_scenario'])
def test_command_destroy(with_scenario):
    sh.molecule('destroy')


@pytest.mark.parametrize(
    'with_scenario', ['docker'], indirect=['with_scenario'])
def test_command_idempotence(with_scenario):
    sh.molecule('create')
    sh.molecule('converge')
    sh.molecule('idempotence')


def test_command_init_role(temp_dir):
    role_directory = os.path.join(temp_dir.strpath, 'test-init')
    sh.molecule('init', 'role', '--role-name', 'test-init')
    os.chdir(role_directory)

    sh.molecule('test')


def test_command_init_scenario(temp_dir):
    molecule_directory = config.molecule_directory(temp_dir.strpath)
    scenario_directory = os.path.join(molecule_directory, 'test-scenario')
    sh.molecule('init', 'scenario', '--scenario-name', 'test-scenario',
                '--role-name', 'test-init')

    assert os.path.isdir(scenario_directory)


@pytest.mark.parametrize(
    'with_scenario', ['docker'], indirect=['with_scenario'])
def test_command_lint(with_scenario):
    sh.molecule('lint')


@pytest.mark.parametrize(
    'with_scenario', ['docker'], indirect=['with_scenario'])
def test_command_login(with_scenario):
    sh.molecule('create')

    child = pexpect.spawn(
        'molecule login --host instance  --scenario-name default')
    child.expect('.*instance-[12].*')
    # If the test returns and doesn't hang it succeeded.
    child.sendline('exit')


@pytest.mark.parametrize(
    'with_scenario', ['docker'], indirect=['with_scenario'])
def test_command_status(with_scenario):
    out = sh.molecule('status', '--scenario-name', 'default')
    assert re.search('instance-1-default.*Not Created.*Docker', out.stdout)

    out = sh.molecule('status', '--scenario-name', 'multi-node')
    assert re.search('instance-1-multi-node', out.stdout)
    assert re.search('instance-2-multi-node', out.stdout)


@pytest.mark.parametrize(
    'with_scenario', ['docker'], indirect=['with_scenario'])
def test_command_syntax(with_scenario):
    sh.molecule('syntax')


@pytest.mark.parametrize(
    'with_scenario', ['docker'], indirect=['with_scenario'])
def test_command_test(with_scenario):
    sh.molecule('test')


@pytest.mark.parametrize(
    'with_scenario', ['host_group_vars'], indirect=['with_scenario'])
def test_command_test_with_host_group_vars(with_scenario):
    sh.molecule('test')


@pytest.mark.parametrize(
    'with_scenario', ['docker'], indirect=['with_scenario'])
def test_command_verify(with_scenario):
    sh.molecule('create')
    sh.molecule('converge')
    sh.molecule('verify')

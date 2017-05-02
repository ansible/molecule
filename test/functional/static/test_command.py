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

import re

import pexpect
import pytest
import sh

pytestmark = pytest.helpers.supports_docker()


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_check(with_scenario):
    sh.molecule('check', '--scenario-name', 'docker')
    sh.molecule('check', '--scenario-name', 'vagrant')


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_converge(with_scenario):
    sh.molecule('converge', '--scenario-name', 'docker')
    sh.molecule('converge', '--scenario-name', 'vagrant')


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_create(with_scenario):
    sh.molecule('create', '--scenario-name', 'docker')
    sh.molecule('create', '--scenario-name', 'vagrant')


@pytest.mark.parametrize(
    'with_scenario', ['dependency'], indirect=['with_scenario'])
def test_command_dependency_ansible_galaxy(with_scenario):
    pass


@pytest.mark.parametrize(
    'with_scenario', ['dependency'], indirect=['with_scenario'])
def test_command_dependency_gilt(with_scenario):
    pass


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_destroy(with_scenario):
    sh.molecule('destroy', '--scenario-name', 'docker')
    sh.molecule('destroy', '--scenario-name', 'vagrant')


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_idempotence(with_scenario):
    sh.molecule('create', '--scenario-name', 'docker')
    sh.molecule('converge', '--scenario-name', 'docker')
    sh.molecule('idempotence', '--scenario-name', 'docker')

    sh.molecule('create', '--scenario-name', 'vagrant')
    sh.molecule('converge', '--scenario-name', 'vagrant')
    sh.molecule('idempotence', '--scenario-name', 'vagrant')


def test_command_init_role(temp_dir):
    pass


def test_command_init_scenario(temp_dir):
    pass


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_lint(with_scenario):
    sh.molecule('lint', '--scenario-name', 'docker')
    sh.molecule('lint', '--scenario-name', 'vagrant')


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_list(with_scenario):
    sh.molecule('destroy', '--scenario-name', 'docker')
    out = sh.molecule('list', '--scenario-name', 'docker')

    assert re.search(
        'static-instance-docker.*Static.*Ansible.*docker.*False.*True',
        out.stdout)

    sh.molecule('destroy', '--scenario-name', 'vagrant')
    out = sh.molecule('list', '--scenario-name', 'vagrant')

    assert re.search(
        'static-instance-vagrant.*Static.*Ansible.*vagrant.*False.*True',
        out.stdout)


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_login(with_scenario):
    child = pexpect.spawn(
        'molecule login --host static-instance --scenario-name docker')
    child.expect('.*static-instance-docker.*')
    # If the test returns and doesn't hang it succeeded.
    child.sendline('exit')

    child = pexpect.spawn(
        'molecule login --host static-instance --scenario-name vagrant')
    child.expect('.*static-instance-vagrant.*')
    # If the test returns and doesn't hang it succeeded.
    child.sendline('exit')


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_syntax(with_scenario):
    sh.molecule('syntax', '--scenario-name', 'docker')
    sh.molecule('syntax', '--scenario-name', 'vagrant')


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_test(with_scenario):
    sh.molecule('test', '--scenario-name', 'docker')
    sh.molecule('test', '--scenario-name', 'vagrant')


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_verify(with_scenario):
    sh.molecule('create', '--scenario-name', 'docker')
    sh.molecule('converge', '--scenario-name', 'docker')
    sh.molecule('verify', '--scenario-name', 'docker')

    sh.molecule('create', '--scenario-name', 'vagrant')
    sh.molecule('converge', '--scenario-name', 'vagrant')
    sh.molecule('verify', '--scenario-name', 'vagrant')

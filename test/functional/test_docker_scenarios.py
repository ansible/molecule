#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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

import os
import pytest
import sh

pytestmark = pytest.helpers.supports_docker()


def ansi_escape(s):
    ansi_escape = re.compile(r'\x1b[^m]*m')

    return ansi_escape.sub('', s)


@pytest.mark.parametrize(
    'scenario_setup', ['command_check'], indirect=['scenario_setup'])
def test_command_check(scenario_setup):
    sh.molecule('create')
    out = sh.molecule('check')
    sh.molecule('verify')

    assert re.search('changed=1', ansi_escape(out.stdout))


@pytest.mark.parametrize(
    'scenario_setup', ['command_converge'], indirect=['scenario_setup'])
def test_command_converge(scenario_setup):
    sh.molecule('converge')


@pytest.mark.parametrize(
    'scenario_setup', ['command_converge'], indirect=['scenario_setup'])
def test_command_converge_with_debug(scenario_setup):
    sh.molecule('--debug', 'converge')


@pytest.mark.parametrize(
    'scenario_setup', ['command_idempotence'], indirect=['scenario_setup'])
def test_command_idempotence(scenario_setup):
    try:
        sh.molecule('test')
    except sh.ErrorReturnCode_1 as e:
        assert re.search('Idempotence test failed.', e.message)


def test_command_init(temp_dir):
    d = os.path.join(temp_dir, 'command-test')
    sh.molecule('init', '--role', 'command-test', '--driver', 'docker')
    os.chdir(d)
    sh.molecule('test')


@pytest.mark.skip(reason=(
    'Determine how to better test this. '
    'Receive py.error.ENOENT: [No such file or directory]: getcwd()'))
def test_command_init_verifier_goss(temp_dir):
    d = os.path.join(temp_dir, 'command-test-goss')
    sh.molecule('init', '--role', 'command-test-goss', '--driver', 'docker',
                '--verifier', 'goss')
    os.chdir(d)
    sh.molecule('test')


def test_command_init_verifier_serverspec(temp_dir):
    d = os.path.join(temp_dir, 'command-test-serverspec')
    sh.molecule('init', '--role', 'command-test-serverspec', '--driver',
                'docker', '--verifier', 'serverspec')
    os.chdir(d)
    sh.bundle('install')
    sh.molecule('test')


@pytest.mark.parametrize(
    'scenario_setup', ['command_status'], indirect=['scenario_setup'])
def test_command_status(scenario_setup):
    out = sh.molecule('status', '--porcelain')

    assert re.search('status-scenario-01 .*not_created .*docker', out.stdout)
    assert re.search('status-scenario-02 .*not_created .*docker', out.stdout)


@pytest.mark.parametrize(
    'scenario_setup', ['command_test'], indirect=['scenario_setup'])
def test_command_test(scenario_setup):
    sh.molecule('test')


@pytest.mark.parametrize(
    'scenario_setup', ['command_verify'], indirect=['scenario_setup'])
def test_command_verify(scenario_setup):
    sh.molecule('verify')


@pytest.mark.parametrize(
    'scenario_setup', ['command_verify_trailing_newline'],
    indirect=['scenario_setup'])
def test_command_verify_trailing_newline(scenario_setup):
    try:
        sh.molecule('verify')
    except sh.ErrorReturnCode_1 as e:
        assert re.search('Trailing newline found at the end of ./playbook.yml',
                         e.message)


@pytest.mark.parametrize(
    'scenario_setup', ['command_verify_trailing_whitespace'],
    indirect=['scenario_setup'])
def test_command_verify_trailing_whitespace(scenario_setup):
    try:
        sh.molecule('verify')
    except sh.ErrorReturnCode_1 as e:
        message = ansi_escape(e.message)

        assert re.search('\[ANSIBLE0002\] Trailing whitespace', message)
        assert re.search('playbook.yml:5', message)


@pytest.mark.parametrize(
    'scenario_setup', ['custom_ansible_cfg'], indirect=['scenario_setup'])
def test_custom_ansible_cfg(scenario_setup):
    sh.molecule('create')
    assert os.path.exists('.molecule/ansible.cfg')

    sh.molecule('destroy')
    assert os.path.exists('.molecule/ansible.cfg')
    assert os.path.exists('ansible.cfg')


@pytest.mark.parametrize(
    'scenario_setup', ['dockerfile'], indirect=['scenario_setup'])
def test_dockerfile(scenario_setup):
    sh.molecule('test')


@pytest.mark.parametrize(
    'scenario_setup', ['group_host_vars'], indirect=['scenario_setup'])
def test_group_host_vars(scenario_setup):
    sh.molecule('test')


@pytest.mark.parametrize(
    'scenario_setup', ['requirements_file'], indirect=['scenario_setup'])
def test_requirements_file(scenario_setup):
    sh.molecule('test')

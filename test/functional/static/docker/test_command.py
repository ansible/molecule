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

import pytest

pytestmark = pytest.helpers.supports_docker()


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_check(with_scenario):
    pytest.helpers.check('docker')


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_converge(with_scenario):
    pytest.helpers.converge('docker')


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_create(with_scenario):
    pytest.helpers.create('docker')


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
    pytest.helpers.destroy('docker')


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_idempotence(with_scenario):
    pytest.helpers.idempotence('docker')


def test_command_init_role(temp_dir):
    pass


def test_command_init_scenario(temp_dir):
    pass


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_lint(with_scenario):
    pytest.helpers.lint('docker')


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_list(with_scenario):
    regexps = [
        'static-instance-docker.*Static.*Ansible.*docker.*False.*True',
    ]
    pytest.helpers.list(regexps, 'docker')


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_login(with_scenario):
    pytest.helpers.login('static-instance-docker',
                         '.*static-instance-docker.*', 'docker')


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_syntax(with_scenario):
    pytest.helpers.syntax('docker')


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_test(with_scenario):
    pytest.helpers.test('docker')


@pytest.mark.parametrize(
    'with_scenario', ['driver/static'], indirect=['with_scenario'])
def test_command_verify(with_scenario):
    pytest.helpers.verify('docker')

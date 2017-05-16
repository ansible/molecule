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


@pytest.fixture()
def scenario_name():
    return 'openstack'


@pytest.mark.parametrize(
    'with_scenario', ['driver/openstack'], indirect=['with_scenario'])
def test_command_check(with_scenario):
    pytest.helpers.check()


@pytest.mark.parametrize(
    'with_scenario', ['driver/openstack'], indirect=['with_scenario'])
def test_command_converge(with_scenario):
    pytest.helpers.converge()


@pytest.mark.parametrize(
    'with_scenario', ['driver/openstack'], indirect=['with_scenario'])
def test_command_create(with_scenario):
    pytest.helpers.create()


@pytest.mark.parametrize(
    'with_scenario', ['dependency'], indirect=['with_scenario'])
def test_command_dependency_ansible_galaxy(with_scenario):
    pytest.helpers.dependency_ansible_galaxy()


@pytest.mark.parametrize(
    'with_scenario', ['dependency'], indirect=['with_scenario'])
def test_command_dependency_gilt(with_scenario):
    pytest.helpers.dependency_gilt()


@pytest.mark.parametrize(
    'with_scenario', ['driver/openstack'], indirect=['with_scenario'])
def test_command_destroy(with_scenario):
    pytest.helpers.destroy()


@pytest.mark.parametrize(
    'with_scenario', ['driver/openstack'], indirect=['with_scenario'])
def test_command_idempotence(with_scenario):
    pytest.helpers.idempotence()


def test_command_init_role(temp_dir, scenario_name):
    pytest.helpers.init_role(temp_dir, scenario_name)


def test_command_init_scenario(temp_dir, scenario_name):
    pytest.helpers.init_scenario(temp_dir, scenario_name)


@pytest.mark.parametrize(
    'with_scenario', ['driver/openstack'], indirect=['with_scenario'])
def test_command_lint(with_scenario):
    pytest.helpers.lint()


@pytest.mark.parametrize(
    'with_scenario', ['driver/openstack'], indirect=['with_scenario'])
def test_command_list(with_scenario):
    x = """
Instance Name          Driver Name    Provisioner Name    Scenario Name    Created    Converged
---------------------  -------------  ------------------  ---------------  ---------  -----------
instance-1-default     Openstack      Ansible             default          False      False
instance-1-multi-node  Openstack      Ansible             multi-node       False      False
instance-2-multi-node  Openstack      Ansible             multi-node       False      False
""".strip()  # noqa

    pytest.helpers.list(x)


@pytest.mark.parametrize(
    'with_scenario', ['driver/openstack'], indirect=['with_scenario'])
def test_command_list_with_format_plain(with_scenario):
    x = """
instance-1-default     Openstack  Ansible  default     False  False
instance-1-multi-node  Openstack  Ansible  multi-node  False  False
instance-2-multi-node  Openstack  Ansible  multi-node  False  False
""".strip()

    pytest.helpers.list_with_format_plain(x)


@pytest.mark.parametrize(
    'with_scenario', ['driver/openstack'], indirect=['with_scenario'])
def test_command_login(with_scenario):
    pytest.helpers.login('instance-1', '.*instance-1.*', 'multi-node')
    pytest.helpers.login('instance-2', '.*instance-2.*', 'multi-node')


@pytest.mark.parametrize(
    'with_scenario', ['driver/openstack'], indirect=['with_scenario'])
def test_command_syntax(with_scenario):
    pytest.helpers.syntax()


@pytest.mark.parametrize(
    'with_scenario', ['driver/openstack'], indirect=['with_scenario'])
def test_command_test(with_scenario):
    pytest.helpers.test('all')


@pytest.mark.parametrize(
    'with_scenario', ['driver/openstack'], indirect=['with_scenario'])
def test_command_verify(with_scenario):
    pytest.helpers.verify()

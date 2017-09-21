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


@pytest.fixture
def patched_ansible_check(mocker):
    return mocker.patch('molecule.provisioner.ansible.Ansible.check')


@pytest.fixture
def patched_ansible_destroy(mocker):
    return mocker.patch('molecule.provisioner.ansible.Ansible.destroy')


@pytest.fixture
def patched_ansible_side_effect(mocker):
    return mocker.patch('molecule.provisioner.ansible.Ansible.side_effect')


@pytest.fixture
def patched_ansible_lint(mocker):
    return mocker.patch(
        'molecule.provisioner.lint.ansible_lint.AnsibleLint.execute')


@pytest.fixture
def patched_ansible_create(mocker):
    return mocker.patch('molecule.provisioner.ansible.Ansible.create')


@pytest.fixture
def patched_ansible_prepare(mocker):
    return mocker.patch('molecule.provisioner.ansible.Ansible.prepare')


@pytest.fixture
def patched_ansible_syntax(mocker):
    return mocker.patch('molecule.provisioner.ansible.Ansible.syntax')


@pytest.fixture
def patched_is_idempotent(mocker):
    return mocker.patch(
        'molecule.command.idempotence.Idempotence._is_idempotent')


@pytest.fixture
def patched_verify_configs(mocker):
    return mocker.patch('molecule.command.base._verify_configs')


@pytest.fixture
def patched_scenario_name(mocker):
    return mocker.patch('molecule.command.base._verify_scenario_name')


@pytest.fixture
def patched_base_setup(mocker):
    return mocker.patch('test.unit.command.test_base.ExtendedBase._setup')


@pytest.fixture
def patched_create_setup(mocker):
    return mocker.patch('molecule.command.create.Create._setup')


@pytest.fixture
def patched_destroy_setup(mocker):
    return mocker.patch('molecule.command.destroy.Destroy._setup')


@pytest.fixture
def patched_destroy_prune(mocker):
    return mocker.patch('molecule.command.destroy.Destroy.prune')


@pytest.fixture
def patched_write_config(mocker):
    return mocker.patch('molecule.provisioner.ansible.Ansible.write_config')


@pytest.fixture
def patched_manage_inventory(mocker):
    return mocker.patch(
        'molecule.provisioner.ansible.Ansible.manage_inventory')

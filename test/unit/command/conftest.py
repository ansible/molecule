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
# TODO(retr0h): patched_provisioner_coverge
def patched_ansible_converge(mocker):
    m = mocker.patch('molecule.provisioner.ansible.Ansible.converge')
    m.return_value = 'patched-ansible-converge-stdout'

    return m


@pytest.fixture
def patched_ansible_lint(mocker):
    return mocker.patch('molecule.lint.ansible_lint.AnsibleLint.execute')


@pytest.fixture
def patched_ansible_galaxy(mocker):
    return mocker.patch(
        'molecule.dependency.ansible_galaxy.AnsibleGalaxy.execute')


@pytest.fixture
def patched_ansible_syntax(mocker):
    return mocker.patch('molecule.provisioner.ansible.Ansible.syntax')


@pytest.fixture
def patched_command_idempotence_is_idempotent(mocker):
    return mocker.patch(
        'molecule.command.idempotence.Idempotence._is_idempotent')


@pytest.fixture
def patched_testinfra(mocker):
    return mocker.patch('molecule.verifier.testinfra.Testinfra.execute')


@pytest.fixture
def patched_verify_configs(mocker):
    return mocker.patch('molecule.command.base._verify_configs')


@pytest.fixture
def patched_provisioner_write_inventory(mocker):
    return mocker.patch('molecule.provisioner.ansible.Ansible.write_inventory')


@pytest.fixture
def patched_provisioner_write_config(mocker):
    return mocker.patch('molecule.provisioner.ansible.Ansible.write_config')

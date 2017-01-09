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

from molecule import config


@pytest.fixture
def command_data():
    return {}


@pytest.fixture
def config_instance(molecule_file, platforms_data, command_data):
    configs = [platforms_data, command_data]

    return config.Config(molecule_file, configs=configs)


@pytest.fixture
def patched_ansible_check(mocker):
    return mocker.patch('molecule.provisioner.Ansible.check')


@pytest.fixture
# TODO patched_provisioner_coverge
def patched_ansible_converge(mocker):
    m = mocker.patch('molecule.provisioner.Ansible.converge')
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
    return mocker.patch('molecule.provisioner.Ansible.syntax')


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

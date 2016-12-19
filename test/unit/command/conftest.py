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

import pytest


@pytest.fixture
def patched_check_main(mocker):
    return mocker.patch('molecule.command.check.Check.main')


@pytest.fixture
def patched_check(mocker):
    m = mocker.patch('molecule.command.check.Check.execute')
    m.return_value = 0, '', ''

    return m


@pytest.fixture
def patched_create(mocker):
    m = mocker.patch('molecule.command.create.Create.execute')
    m.return_value = 0, '', ''

    return m


@pytest.fixture
def patched_converge(mocker):
    m = mocker.patch('molecule.command.converge.Converge.execute')
    m.return_value = 0, '', ''

    return m


@pytest.fixture
def patched_dependency(mocker):
    m = mocker.patch('molecule.command.dependency.Dependency.execute')
    m.return_value = 0, '', ''

    return m


@pytest.fixture
def patched_destroy_main(mocker):
    return mocker.patch('molecule.command.destroy.Destroy.main')


@pytest.fixture
def patched_destroy(mocker):
    m = mocker.patch('molecule.command.destroy.Destroy.execute')
    m.return_value = 0, '', ''

    return m


@pytest.fixture
def patched_idempotence(mocker):
    m = mocker.patch('molecule.command.idempotence.Idempotence.execute')
    m.return_value = 0, '', ''

    return m


@pytest.fixture
def patched_syntax(mocker):
    m = mocker.patch('molecule.command.syntax.Syntax.execute')
    m.return_value = 0, '', ''

    return m


@pytest.fixture
def patched_verify(mocker):
    m = mocker.patch('molecule.command.verify.Verify.execute')
    m.return_value = 0, '', ''

    return m


@pytest.fixture
def patched_create_inventory(mocker):
    return mocker.patch('molecule.core.Molecule.create_inventory_file')


@pytest.fixture
def patched_remove_inventory(mocker):
    return mocker.patch('molecule.core.Molecule.remove_inventory_file')


@pytest.fixture
def patched_create_templates(mocker):
    return mocker.patch('molecule.core.Molecule.create_templates')


@pytest.fixture
def patched_remove_templates(mocker):
    return mocker.patch('molecule.core.Molecule.remove_templates')


@pytest.fixture
def patched_add_cli_arg(mocker):
    return mocker.patch(
        'molecule.ansible_playbook.AnsiblePlaybook.add_cli_arg')


@pytest.fixture
def patched_remove_cli_arg(mocker):
    return mocker.patch(
        'molecule.ansible_playbook.AnsiblePlaybook.remove_cli_arg')


@pytest.fixture
def patched_add_env_arg(mocker):
    return mocker.patch(
        'molecule.ansible_playbook.AnsiblePlaybook.add_env_arg')


@pytest.fixture
def patched_ansible_lint(mocker):
    return mocker.patch('molecule.verifier.ansible_lint.AnsibleLint')


@pytest.fixture
def patched_ansible_lint_execute(mocker):
    m =  mocker.patch(
        'molecule.verifier.ansible_lint.AnsibleLint.execute')
    m.return_value = (0, '', '')

    return m

@pytest.fixture
def patched_trailing(mocker):
    return mocker.patch('molecule.verifier.trailing.Trailing')


@pytest.fixture
def patched_trailing_execute(mocker):
    m = mocker.patch(
        'molecule.verifier.trailing.Trailing.execute')
    m.return_value = (0, '', '')

    return m

@pytest.fixture
def patched_ssh_config(mocker):
    return mocker.patch('molecule.core.Molecule.write_ssh_config')


@pytest.fixture
def patched_write_instances_state(mocker):
    return mocker.patch('molecule.core.Molecule.write_instances_state')


@pytest.fixture
def patched_driver_up(mocker):
    return mocker.patch('molecule.driver.vagrantdriver.VagrantDriver.up')


@pytest.fixture
def patched_driver_destroy(mocker):
    return mocker.patch('molecule.driver.vagrantdriver.VagrantDriver.destroy')


@pytest.fixture
def patched_shell(mocker):
    return mocker.patch('molecule.dependency.shell.Shell.execute')

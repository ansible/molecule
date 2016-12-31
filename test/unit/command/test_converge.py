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

from molecule.command import converge


def test_execute_creates_instances(
        mocker, patched_create, patched_ansible_playbook,
        patched_create_inventory, patched_print_info, molecule_instance):

    c = converge.Converge({}, {}, molecule_instance)
    result = c.execute()

    msg = 'Starting Ansible Run...'
    patched_print_info.assert_called_with(msg)

    patched_ansible_playbook.assert_called_once_with(hide_errors=True)
    assert (None, None) == result
    assert molecule_instance.state.converged


def test_execute_does_not_create_instances(
        patched_create, patched_ansible_playbook, patched_create_inventory,
        molecule_instance):
    molecule_instance.state.change_state('created', True)

    c = converge.Converge({}, {}, molecule_instance)
    c.execute()

    assert not patched_create.called


def test_execute_does_not_create_inventory(
        patched_create, patched_ansible_playbook, patched_create_inventory,
        molecule_instance):
    molecule_instance.state.change_state('converged', True)

    c = converge.Converge({}, {}, molecule_instance)
    c.execute()

    assert not patched_create_inventory.called


def test_execute_create_inventory_and_instances_with_platform_all(
        patched_create, patched_ansible_playbook, patched_create_inventory,
        molecule_instance):
    molecule_instance.state.change_state('created', True)
    command_args = {'platform': 'all'}

    c = converge.Converge({}, command_args, molecule_instance)
    c.execute()

    patched_create.assert_called_once_with()
    patched_create_inventory.assert_called_once_with()


def test_execute_create_inventory_and_instances_with_platform_all_state_file(
        patched_create, patched_ansible_playbook, patched_create_inventory,
        molecule_instance):
    molecule_instance.state.change_state('multiple_platforms', True)

    c = converge.Converge({}, {}, molecule_instance)
    c.execute()

    patched_create.assert_called_once_with()
    patched_create_inventory.assert_called_once_with()


def test_execute_installs_dependencies(
        patched_create, patched_ansible_playbook, patched_dependency,
        patched_create_inventory, molecule_instance):
    molecule_instance.config.config['dependency']['requirements_file'] = True

    c = converge.Converge({}, {}, molecule_instance)
    c.execute()

    patched_dependency.assert_called_once_with()


def test_execute_with_debug(patched_create, patched_ansible_playbook,
                            patched_create_inventory, patched_print_debug,
                            molecule_instance):
    args = {'debug': True}
    c = converge.Converge(args, {}, molecule_instance)
    c.execute()

    patched_ansible_playbook.assert_called_once()

    x = ("ANSIBLE_CONFIG: test/config_file\n"
         "ANSIBLE_FORCE_COLOR: 'true'\n"
         "ANSIBLE_HOST_KEY_CHECKING: 'false'\n"
         "ANSIBLE_SSH_ARGS: -o UserKnownHostsFile=/dev/null "
         "-o IdentitiesOnly=yes "
         "-o ControlMaster=auto\n  "
         "-o ControlPersist=60s\n")
    patched_print_debug.assert_called_with('ANSIBLE ENVIRONMENT', x)


def test_execute_raises_on_exit(patched_create, patched_ansible_playbook,
                                patched_create_inventory, molecule_instance):
    patched_ansible_playbook.return_value = (1, None)

    c = converge.Converge({}, {}, molecule_instance)
    with pytest.raises(SystemExit):
        result = c.execute()

        assert (1, None) == result


def test_execute_does_not_raise_on_exit(
        patched_create, patched_ansible_playbook, patched_create_inventory,
        molecule_instance):
    patched_ansible_playbook.return_value = (1, None)

    c = converge.Converge({}, {}, molecule_instance)
    result = c.execute(exit=False)

    assert (1, None) == result


def test_execute_adds_idempotency_flags(
        mocker, patched_create, patched_ansible_playbook,
        patched_create_inventory, patched_add_env_arg, patched_remove_cli_arg,
        molecule_instance):

    c = converge.Converge({}, {}, molecule_instance)
    c.execute(idempotent=True)

    expected = [mocker.call('_out'), mocker.call('_err'), mocker.call('diff')]
    assert expected == patched_remove_cli_arg.mock_calls

    assert mocker.call('ANSIBLE_NOCOLOR',
                       'true') in patched_add_env_arg.mock_calls
    assert mocker.call('ANSIBLE_FORCE_COLOR',
                       'false') in patched_add_env_arg.mock_calls

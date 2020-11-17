#  Copyright (c) 2015-2018 Cisco Systems, Inc.
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

from subprocess import CompletedProcess

import pytest

from molecule import config
from molecule.provisioner import ansible_playbook


@pytest.fixture
def _instance(config_instance):
    _instance = ansible_playbook.AnsiblePlaybook("playbook", config_instance)

    return _instance


@pytest.fixture
def _inventory_directory(_instance):
    return _instance._config.provisioner.inventory_directory


def test_ansible_command_private_member(_instance):
    assert _instance._ansible_command is None


def test_ansible_playbook_private_member(_instance):
    assert "playbook" == _instance._playbook


def test_config_private_member(_instance):
    assert isinstance(_instance._config, config.Config)


def test_bake(_inventory_directory, _instance):
    pb = _instance._config.provisioner.playbooks.converge
    _instance._playbook = pb
    _instance.bake()

    args = [
        "ansible-playbook",
        "--become",
        "--inventory",
        _inventory_directory,
        "--skip-tags",
        "molecule-notest,notest",
        pb,
    ]

    assert _instance._ansible_command.cmd == args


def test_bake_removes_non_interactive_options_from_non_converge_playbooks(
    _inventory_directory, _instance
):
    _instance.bake()

    args = [
        "ansible-playbook",
        "--inventory",
        _inventory_directory,
        "--skip-tags",
        "molecule-notest,notest",
        "playbook",
    ]

    assert _instance._ansible_command.cmd == args


def test_bake_has_ansible_args(_inventory_directory, _instance):
    _instance._config.ansible_args = ("foo", "bar")
    _instance._config.config["provisioner"]["ansible_args"] = ("frob", "nitz")
    _instance.bake()

    args = [
        "ansible-playbook",
        "--inventory",
        _inventory_directory,
        "--skip-tags",
        "molecule-notest,notest",
        "frob",
        "nitz",
        "foo",
        "bar",
        "playbook",
    ]

    assert _instance._ansible_command.cmd == args


def test_bake_does_not_have_ansible_args(_inventory_directory, _instance):
    for action in ["create", "destroy"]:
        _instance._config.ansible_args = ("foo", "bar")
        _instance._config.action = action
        _instance.bake()

        args = [
            "ansible-playbook",
            "--inventory",
            _inventory_directory,
            "--skip-tags",
            "molecule-notest,notest",
            "playbook",
        ]

        assert _instance._ansible_command.cmd == args


def test_bake_idem_does_have_skip_tag(_inventory_directory, _instance):
    _instance._config.action = "idempotence"
    _instance.bake()

    args = [
        "ansible-playbook",
        "--inventory",
        _inventory_directory,
        "--skip-tags",
        "molecule-notest,notest,molecule-idempotence-notest",
        "playbook",
    ]

    assert _instance._ansible_command.cmd == args


def test_execute(patched_run_command, _instance):
    _instance._ansible_command = "patched-command"
    result = _instance.execute()

    patched_run_command.assert_called_once_with("patched-command", debug=False)
    assert "patched-run-command-stdout" == result


def test_execute_bakes(_inventory_directory, patched_run_command, _instance):
    _instance.execute()

    assert _instance._ansible_command is not None

    args = [
        "ansible-playbook",
        "--inventory",
        _inventory_directory,
        "--skip-tags",
        "molecule-notest,notest",
        "playbook",
    ]

    # result = str(patched_run_command.mock_calls[0][1][0]).split()

    assert _instance._ansible_command.cmd == args


def test_execute_bakes_with_ansible_args(
    _inventory_directory, patched_run_command, _instance
):
    _instance._config.ansible_args = ("-o", "--syntax-check")
    _instance.execute()

    assert _instance._ansible_command is not None

    args = [
        "ansible-playbook",
        "--inventory",
        _inventory_directory,
        "--skip-tags",
        "molecule-notest,notest",
        # "--foo",
        # "--bar",
        "-o",
        "--syntax-check",
        "playbook",
    ]

    assert _instance._ansible_command.cmd == args


def test_executes_catches_and_exits_return_code(
    patched_run_command, patched_logger_critical, _instance
):
    patched_run_command.side_effect = [
        CompletedProcess(
            args="ansible-playbook", returncode=1, stdout="out", stderr="err"
        )
    ]
    with pytest.raises(SystemExit) as e:
        _instance.execute()

    assert 1 == e.value.code


def test_add_cli_arg(_instance):
    assert {} == _instance._cli

    _instance.add_cli_arg("foo", "bar")
    assert {"foo": "bar"} == _instance._cli


def test_add_env_arg(_instance):
    assert "foo" not in _instance._env

    _instance.add_env_arg("foo", "bar")
    assert "bar" == _instance._env["foo"]

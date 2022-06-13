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

import os

import pytest

from molecule import config, util
from molecule.command import base


class ExtendedBase(base.Base):
    """ExtendedBase Class."""

    def execute(self, action_args=None):
        pass


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.fixture
def _base_class(patched_config_validate, config_instance):
    return ExtendedBase


@pytest.fixture
def _instance(_base_class, config_instance):
    return _base_class(config_instance)


@pytest.fixture
def _patched_base_setup(mocker):
    return mocker.patch("molecule.test.unit.command.test_base.ExtendedBase._setup")


@pytest.fixture
def _patched_write_config(mocker):
    return mocker.patch("molecule.provisioner.ansible.Ansible.write_config")


@pytest.fixture
def _patched_manage_inventory(mocker):
    return mocker.patch("molecule.provisioner.ansible.Ansible.manage_inventory")


@pytest.fixture
def _patched_execute_subcommand(mocker):
    return mocker.patch("molecule.command.base.execute_subcommand")


@pytest.fixture
def _patched_execute_scenario(mocker):
    return mocker.patch("molecule.command.base.execute_scenario")


@pytest.fixture
def _patched_print_matrix(mocker):
    return mocker.patch("molecule.scenarios.Scenarios.print_matrix")


@pytest.fixture
def _patched_prune(mocker):
    return mocker.patch("molecule.scenario.Scenario.prune")


@pytest.fixture
def _patched_sysexit(mocker):
    return mocker.patch("molecule.util.sysexit")


def test_config_private_member(_instance):
    assert isinstance(_instance._config, config.Config)


def test_init_calls_setup(_patched_base_setup, _instance):
    _patched_base_setup.assert_called_once_with()


def test_setup(
    mocker,
    patched_add_or_update_vars,
    _patched_write_config,
    _patched_manage_inventory,
    _instance,
):
    assert os.path.isdir(os.path.dirname(_instance._config.provisioner.inventory_file))
    assert os.path.isfile(_instance._config.config_file)

    _patched_manage_inventory.assert_called_once_with()
    _patched_write_config.assert_called_once_with()


def test_execute_cmdline_scenarios(
    config_instance, _patched_print_matrix, _patched_execute_scenario
):
    # Ensure execute_cmdline_scenarios runs normally:
    # - scenarios.print_matrix is called, which also indicates Scenarios
    #   was instantiated correctly
    # - execute_scenario is called once, indicating the function correctly
    #   loops over Scenarios.
    scenario_name = None
    args = {}
    command_args = {"destroy": "always", "subcommand": "test"}
    base.execute_cmdline_scenarios(scenario_name, args, command_args)

    assert _patched_print_matrix.called_once_with()
    assert _patched_execute_scenario.call_count == 1


def test_execute_cmdline_scenarios_prune(
    config_instance, _patched_prune, _patched_execute_subcommand
):
    # Subcommands should be executed and prune *should* run when
    # destroy is 'always'
    scenario_name = "default"
    args = {}
    command_args = {"destroy": "always", "subcommand": "test"}

    base.execute_cmdline_scenarios(scenario_name, args, command_args)

    assert _patched_execute_subcommand.called
    assert _patched_prune.called


def test_execute_cmdline_scenarios_no_prune(
    config_instance, _patched_prune, _patched_execute_subcommand
):
    # Subcommands should be executed but prune *should not* run when
    # destroy is 'never'
    scenario_name = "default"
    args = {}
    command_args = {"destroy": "never", "subcommand": "test"}

    base.execute_cmdline_scenarios(scenario_name, args, command_args)

    assert _patched_execute_subcommand.called
    assert not _patched_prune.called


def test_execute_cmdline_scenarios_exit_destroy(
    config_instance,
    _patched_execute_scenario,
    _patched_prune,
    _patched_execute_subcommand,
    _patched_sysexit,
):
    # Ensure execute_cmdline_scenarios handles errors correctly when 'destroy'
    # is 'always':
    # - cleanup and destroy subcommands are run when execute_scenario
    #   raises SystemExit
    # - scenario is pruned
    scenario_name = "default"
    args = {}
    command_args = {"destroy": "always", "subcommand": "test"}
    _patched_execute_scenario.side_effect = SystemExit()

    base.execute_cmdline_scenarios(scenario_name, args, command_args)

    assert _patched_execute_subcommand.call_count == 2
    # pull out the second positional call argument for each call,
    # which is the called subcommand. 'cleanup' and 'destroy' should be called.
    assert _patched_execute_subcommand.call_args_list[0][0][1] == "cleanup"
    assert _patched_execute_subcommand.call_args_list[1][0][1] == "destroy"
    assert _patched_prune.called
    assert _patched_sysexit.called


def test_execute_cmdline_scenarios_exit_nodestroy(
    config_instance, _patched_execute_scenario, _patched_prune, _patched_sysexit
):
    # Ensure execute_cmdline_scenarios handles errors correctly when 'destroy'
    # is 'always':
    # - destroy subcommand is not run when execute_scenario raises SystemExit
    # - scenario is not pruned
    # - caught SystemExit is reraised
    scenario_name = "default"
    args = {}
    command_args = {"destroy": "never", "subcommand": "test"}

    _patched_execute_scenario.side_effect = SystemExit()

    # Catch the expected SystemExit reraise
    with pytest.raises(SystemExit):
        base.execute_cmdline_scenarios(scenario_name, args, command_args)

    assert _patched_execute_scenario.called
    assert not _patched_prune.called
    assert not _patched_sysexit.called


def test_runtime_paths(config_instance, _patched_sysexit):
    # the ansible_collections_path and ansible_roles_path from the runtime
    # should be added to the provisioner's paths
    scenario_name = None
    args = {}
    command_args = {"destroy": "never", "subcommand": "verify"}

    base.result_callback()
    base.execute_cmdline_scenarios(scenario_name, args, command_args)

    home = os.path.expanduser("~")
    cache_dir = config_instance.runtime.cache_dir
    runtime_roles_path = config_instance.runtime.environ.get("ANSIBLE_ROLES_PATH")
    provisioner_roles_path = config_instance.provisioner.env.get("ANSIBLE_ROLES_PATH")
    runtime_collections_path = config_instance.runtime.environ.get(
        config_instance.ansible_collections_path
    )
    provisioner_collections_path = config_instance.provisioner.env.get(
        config_instance.ansible_collections_path
    )

    assert runtime_roles_path.startswith(
        f"{cache_dir}/roles:"
        f"{home}/.ansible/roles:"
        f"/usr/share/ansible/roles:"
        f"/etc/ansible/roles"
    )

    assert runtime_collections_path.startswith(
        f"{cache_dir}/collections:" f"{home}/.ansible/collections"
    )

    assert provisioner_roles_path.startswith(f"{cache_dir}/roles")

    assert provisioner_collections_path.startswith(f"{cache_dir}/collections")


def test_execute_subcommand(config_instance):
    # scenario's config.action is mutated in-place for every sequence action,
    # so make sure that is currently set to the executed action
    assert config_instance.action != "list"
    assert base.execute_subcommand(config_instance, "list")
    assert config_instance.action == "list"


def test_execute_scenario(mocker, _patched_execute_subcommand):
    # call a spoofed scenario with a sequence that does not include destroy:
    # - execute_subcommand should be called once for each sequence item
    # - prune should not be called, since the sequence has no destroy step
    scenario = mocker.Mock()
    scenario.sequence = ("a", "b", "c")

    base.execute_scenario(scenario)

    assert _patched_execute_subcommand.call_count == len(scenario.sequence)
    assert not scenario.prune.called


def test_execute_scenario_destroy(mocker, _patched_execute_subcommand):
    # call a spoofed scenario with a sequence that includes destroy:
    # - execute_subcommand should be called once for each sequence item
    # - prune should be called, since the sequence has a destroy step
    scenario = mocker.Mock()
    scenario.sequence = ("a", "b", "destroy", "c")

    base.execute_scenario(scenario)

    assert _patched_execute_subcommand.call_count == len(scenario.sequence)
    assert scenario.prune.called


def test_get_configs(config_instance):
    molecule_file = config_instance.molecule_file
    data = config_instance.config
    util.write_file(molecule_file, util.safe_dump(data))

    result = base.get_configs({}, {})
    assert 1 == len(result)
    assert isinstance(result, list)
    assert isinstance(result[0], config.Config)


def test_verify_configs(config_instance):
    configs = [config_instance]

    assert base._verify_configs(configs) is None


def test_verify_configs_raises_with_no_configs(patched_logger_critical):
    with pytest.raises(SystemExit) as e:
        base._verify_configs([])

    assert 1 == e.value.code

    msg = "'molecule/*/molecule.yml' glob failed.  Exiting."
    patched_logger_critical.assert_called_once_with(msg)


def test_verify_configs_raises_with_duplicate_configs(
    patched_logger_critical, config_instance
):
    with pytest.raises(SystemExit) as e:
        configs = [config_instance, config_instance]
        base._verify_configs(configs)

    assert 1 == e.value.code

    msg = "Duplicate scenario name 'default' found.  Exiting."
    patched_logger_critical.assert_called_once_with(msg)


def test_get_subcommand():
    assert "test_base" == base._get_subcommand(__name__)


@pytest.mark.parametrize(
    "shell",
    [
        "bash",
        "zsh",
        "fish",
    ],
)
def test_command_completion(shell: str) -> None:
    env = os.environ.copy()
    env["_MOLECULE_COMPLETE"] = f"{shell}_source"

    if "bash" in shell:
        bash_version = util.run_command(["bash", "--version"]).stdout.split()[3][0:3]

    result = util.run_command(["molecule"], env=env)

    if "bash" in shell and (float(bash_version) < 4.4):
        assert result.returncode == 1
        assert "Found config file" not in result.stdout
    else:
        assert result.returncode == 0
        assert "Found config file" not in result.stdout

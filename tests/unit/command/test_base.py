#  Copyright (c) 2015-2018 Cisco Systems, Inc.  # noqa: D100
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

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pytest_mock import MockerFixture

from molecule import config, util
from molecule.command import base


FIXTURE_DIR = Path(__file__).parent.parent.parent / "fixtures" / "unit" / "test_base"


class ExtendedBase(base.Base):
    """ExtendedBase Class."""

    def execute(self, action_args=None):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN101, ANN201, D102
        pass


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
@pytest.fixture()
def _base_class(patched_config_validate, config_instance: config.Config):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN202, PT005, ARG001
    return ExtendedBase


@pytest.fixture()
def _instance(_base_class, config_instance: config.Config):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN202, PT005
    return _base_class(config_instance)


@pytest.fixture()
def _patched_base_setup(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN202, PT005
    return mocker.patch("tests.unit.command.test_base.ExtendedBase._setup")


@pytest.fixture()
def _patched_write_config(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN202, PT005
    return mocker.patch("molecule.provisioner.ansible.Ansible.write_config")


@pytest.fixture()
def _patched_manage_inventory(mocker):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN202, PT005
    return mocker.patch("molecule.provisioner.ansible.Ansible.manage_inventory")


@pytest.fixture(name="patched_execute_subcommand")
def fixture_patched_execute_subcommand(mocker: MockerFixture) -> MagicMock:
    """Mock molecule execute_subcommand function.

    Args:
        mocker: pytest mocker fixture.

    Returns:
        MagicMock: Mocked execute_subcommand function.
    """
    return mocker.patch("molecule.command.base.execute_subcommand")


@pytest.fixture(name="patched_execute_scenario")
def fixture_patched_execute_scenario(mocker: MockerFixture) -> MagicMock:
    """Mock molecule execute_scenario function.

    Args:
        mocker: pytest mocker fixture.

    Returns:
        MagicMock: Mocked execute_scenario function.
    """
    return mocker.patch("molecule.command.base.execute_scenario")


@pytest.fixture(name="patched_prune")
def fixture_patched_prune(mocker: MockerFixture) -> MagicMock:
    """Mock molecule prune function.

    Args:
        mocker: pytest mocker fixture.

    Returns:
        MagicMock: Mocked prune function.
    """
    return mocker.patch("molecule.scenario.Scenario.prune")


@pytest.fixture(name="patched_sysexit")
def fixture_patched_sysexit(mocker: MockerFixture) -> MagicMock:
    """Mock molecule util.sysexit function.

    Args:
        mocker: pytest mocker fixture.

    Returns:
        MagicMock: Mocked util.sysexit function.
    """
    return mocker.patch("molecule.util.sysexit")


def test_command_config_private_member(_instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    assert isinstance(_instance._config, config.Config)


def test_init_calls_setup(_patched_base_setup, _instance):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT019, D103
    _patched_base_setup.assert_called_once_with()


def test_command_setup(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,  # noqa: ARG001
    patched_add_or_update_vars,  # noqa: ANN001, ARG001
    _patched_write_config,  # noqa: ANN001, PT019
    _patched_manage_inventory,  # noqa: ANN001, PT019
    _instance,  # noqa: ANN001, PT019
):
    assert os.path.isdir(  # noqa: PTH112
        os.path.dirname(_instance._config.provisioner.inventory_file),  # noqa: PTH120
    )
    assert os.path.isfile(_instance._config.config_file)  # noqa: PTH113

    _patched_manage_inventory.assert_called_once_with()
    _patched_write_config.assert_called_once_with()


@pytest.mark.usefixtures("config_instance")
def test_execute_cmdline_scenarios(patched_execute_scenario: MagicMock) -> None:
    """Ensure execute_cmdline_scenarios runs normally.

    Execute_scenario is called once, indicating the function correctly loops over Scenarios.

    Args:
        patched_execute_scenario: Mocked execute_scenario function.
    """
    scenario_name = None
    args: dict[str, str] = {}
    command_args = {"destroy": "always", "subcommand": "test"}
    base.execute_cmdline_scenarios(scenario_name, args, command_args)  # type: ignore[no-untyped-call]

    scenario_count = 1
    assert patched_execute_scenario.call_count == scenario_count


@pytest.mark.usefixtures("config_instance")
def test_execute_cmdline_scenarios_prune(
    patched_execute_subcommand: MagicMock,
    patched_prune: MagicMock,
) -> None:
    """Confirm prune is called when destroy is 'always'.

    Args:
        patched_execute_subcommand: Mocked execute_subcommand function.
        patched_prune: Mocked prune function.
    """
    scenario_name = "default"
    args: dict[str, str] = {}
    command_args = {"destroy": "always", "subcommand": "test"}

    base.execute_cmdline_scenarios(scenario_name, args, command_args)  # type: ignore[no-untyped-call]

    assert patched_execute_subcommand.called
    assert patched_prune.called


@pytest.mark.usefixtures("config_instance")
def test_execute_cmdline_scenarios_no_prune(
    patched_prune: MagicMock,
    patched_execute_subcommand: MagicMock,
) -> None:
    """Confirm prune is not called when destroy is 'never'.

    Args:
        patched_prune: Mocked prune function.
        patched_execute_subcommand: Mocked execute_subcommand function.
    """
    scenario_name = "default"
    args: dict[str, str] = {}
    command_args = {"destroy": "never", "subcommand": "test"}

    base.execute_cmdline_scenarios(scenario_name, args, command_args)  # type: ignore[no-untyped-call]

    assert patched_execute_subcommand.called
    assert not patched_prune.called


def test_execute_cmdline_scenarios_exit_destroy(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    config_instance: config.Config,  # noqa: ARG001
    patched_execute_scenario: MagicMock,
    patched_prune: MagicMock,
    patched_execute_subcommand: MagicMock,
    patched_sysexit: MagicMock,
):
    # Ensure execute_cmdline_scenarios handles errors correctly when 'destroy'
    # is 'always':
    # - cleanup and destroy subcommands are run when execute_scenario
    #   raises SystemExit
    # - scenario is pruned
    scenario_name = "default"
    args: dict[str, str] = {}
    command_args = {"destroy": "always", "subcommand": "test"}
    patched_execute_scenario.side_effect = SystemExit()

    base.execute_cmdline_scenarios(scenario_name, args, command_args)  # type: ignore[no-untyped-call]

    assert patched_execute_subcommand.call_count == 2  # noqa: PLR2004
    # pull out the second positional call argument for each call,
    # which is the called subcommand. 'cleanup' and 'destroy' should be called.
    assert patched_execute_subcommand.call_args_list[0][0][1] == "cleanup"
    assert patched_execute_subcommand.call_args_list[1][0][1] == "destroy"
    assert patched_prune.called
    assert patched_sysexit.called


def test_execute_cmdline_scenarios_exit_nodestroy(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    config_instance: config.Config,  # noqa: ARG001
    patched_execute_scenario: MagicMock,
    patched_prune: MagicMock,
    patched_sysexit: MagicMock,
):
    # Ensure execute_cmdline_scenarios handles errors correctly when 'destroy'
    # is 'always':
    # - destroy subcommand is not run when execute_scenario raises SystemExit
    # - scenario is not pruned
    # - caught SystemExit is reraised
    scenario_name = "default"
    args: dict[str, str] = {}
    command_args = {"destroy": "never", "subcommand": "test"}

    patched_execute_scenario.side_effect = SystemExit()

    # Catch the expected SystemExit reraise
    with pytest.raises(SystemExit):
        base.execute_cmdline_scenarios(scenario_name, args, command_args)  # type: ignore[no-untyped-call]

    assert patched_execute_scenario.called
    assert not patched_prune.called
    assert not patched_sysexit.called


def test_execute_subcommand(config_instance: config.Config):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    # scenario's config.action is mutated in-place for every sequence action,
    # so make sure that is currently set to the executed action
    assert config_instance.action != "list"
    assert base.execute_subcommand(config_instance, "list")  # type: ignore[no-untyped-call]
    assert config_instance.action == "list"


def test_execute_scenario(mocker: MockerFixture, patched_execute_subcommand):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    # call a spoofed scenario with a sequence that does not include destroy:
    # - execute_subcommand should be called once for each sequence item
    # - prune should not be called, since the sequence has no destroy step
    scenario = mocker.Mock()
    scenario.sequence = ("a", "b", "c")

    base.execute_scenario(scenario)  # type: ignore[no-untyped-call]

    assert patched_execute_subcommand.call_count == len(scenario.sequence)
    assert not scenario.prune.called


def test_execute_scenario_destroy(mocker: MockerFixture, patched_execute_subcommand):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    # call a spoofed scenario with a sequence that includes destroy:
    # - execute_subcommand should be called once for each sequence item
    # - prune should be called, since the sequence has a destroy step
    scenario = mocker.Mock()
    scenario.sequence = ("a", "b", "destroy", "c")

    base.execute_scenario(scenario)  # type: ignore[no-untyped-call]

    assert patched_execute_subcommand.call_count == len(scenario.sequence)
    assert scenario.prune.called


def test_get_configs(config_instance: config.Config):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    molecule_file = config_instance.molecule_file
    data = config_instance.config
    util.write_file(molecule_file, util.safe_dump(data))

    result = base.get_configs({}, {})  # type: ignore[no-untyped-call]
    assert len(result) == 1
    assert isinstance(result, list)
    assert isinstance(result[0], config.Config)


def test_verify_configs(config_instance: config.Config):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    configs = [config_instance]

    assert base._verify_configs(configs) is None  # type: ignore[no-untyped-call]


def test_verify_configs_raises_with_no_configs(caplog):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    with pytest.raises(SystemExit) as e:
        base._verify_configs([])  # type: ignore[no-untyped-call]

    assert e.value.code == 1

    msg = "'molecule/*/molecule.yml' glob failed.  Exiting."
    assert msg in caplog.text


def test_verify_configs_raises_with_duplicate_configs(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    caplog: pytest.LogCaptureFixture,
    config_instance: config.Config,
):
    with pytest.raises(SystemExit) as e:  # noqa: PT012
        configs = [config_instance, config_instance]
        base._verify_configs(configs)  # type: ignore[no-untyped-call]

    assert e.value.code == 1

    msg = "Duplicate scenario name 'default' found.  Exiting."
    assert msg in caplog.text


def test_get_subcommand() -> None:  # noqa: D103
    assert base._get_subcommand(__name__) == "test_base"  # type: ignore[no-untyped-call]


@pytest.mark.parametrize(
    "shell",
    [  # noqa: PT007
        "bash",
        "zsh",
        "fish",
    ],
)
def test_command_completion(shell: str) -> None:  # noqa: D103
    env = os.environ.copy()
    env["_MOLECULE_COMPLETE"] = f"{shell}_source"
    bash_version = "0.0"

    if "bash" in shell:
        bash_version = util.run_command(["bash", "--version"]).stdout.split()[3][0:3]

    result = util.run_command(["molecule"], env=env)

    if "bash" in shell and (float(bash_version) < 4.4):  # noqa: PLR2004
        string = "Shell completion is not supported for Bash versions older than 4.4"
        assert string not in result.stdout
    else:
        assert result.returncode == 0
        assert "Found config file" not in result.stdout

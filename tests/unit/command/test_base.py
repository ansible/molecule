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

from __future__ import annotations

import os
import subprocess

from pathlib import Path
from typing import TYPE_CHECKING, Literal

import pytest

from molecule import config
from molecule.command import base
from molecule.exceptions import ImmediateExit, ScenarioFailureError
from molecule.shell import main
from molecule.utils import util


if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture

    from molecule.types import CommandArgs, MoleculeArgs


FIXTURE_DIR = Path(__file__).parent.parent.parent / "fixtures" / "unit" / "test_base"


class ExtendedBase(base.Base):
    """ExtendedBase Class."""

    def execute(self, action_args: list[str] | None = None) -> None:
        """No-op the execute method.

        Args:
            action_args: Optional list of action arguments.
        """


@pytest.fixture(name="base_class")
def fixture_base_class(
    patched_config_validate: pytest.FixtureRequest,
    config_instance: config.Config,
) -> type[ExtendedBase]:
    """Return a mocked instance of ExtendedBase.

    The use of the `patched_config_validate` fixture, disables
    config.Config._validate from executing.  Thus preventing odd side-effects
    throughout patched.assert_called unit tests (retr0h)

    Args:
        patched_config_validate: Mocked config.Config._validate function.
        config_instance: Mocked config_instance fixture.

    Returns:
        ExtendedBase: An instance of ExtendedBase instantiated with the config_instance.
    """
    return ExtendedBase


@pytest.fixture(name="instance")
def fixture_instance(
    base_class: type[ExtendedBase],
    config_instance: config.Config,
) -> ExtendedBase:
    """Return a mocked instance of ExtendedBase.

    Args:
        base_class: Mocked _base_class fixture.
        config_instance: Mocked config_instance fixture.

    Returns:
        ExtendedBase: An instance of ExtendedBase instantiated with the config_instance.
    """
    return base_class(config_instance)


@pytest.fixture(name="patched_base_setup")
def fixture_patched_base_setup(mocker: MockerFixture) -> MagicMock:
    """Mock ExtendedBase setup function.

    Args:
        mocker: pytest mocker fixture.

    Returns:
        MagicMock: Mocked setup function.
    """
    return mocker.patch("tests.unit.command.test_base.ExtendedBase._setup")


@pytest.fixture(name="patched_write_config")
def fixture_patched_write_config(mocker: MockerFixture) -> MagicMock:
    """Mock molecule write_config function.

    Args:
        mocker: pytest mocker fixture.

    Returns:
        MagicMock: Mocked write_config function.
    """
    return mocker.patch("molecule.provisioner.ansible.Ansible.write_config")


@pytest.fixture(name="patched_manage_inventory")
def fixture_patched_manage_inventory(mocker: MockerFixture) -> MagicMock:
    """Mock molecule manage_inventory function.

    Args:
        mocker: pytest mocker fixture.

    Returns:
        MagicMock: Mocked manage_inventory function.
    """
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
    return mocker.patch("molecule.utils.util.sysexit")


def test_command_config_private_member(instance: ExtendedBase) -> None:
    """Ensure the _config private member is a config.Config instance.

    Args:
        instance: An instance of ExtendedBase.
    """
    assert isinstance(instance._config, config.Config)


def test_init_calls_setup(
    patched_base_setup: MagicMock,
    instance: ExtendedBase,
) -> None:
    """Ensure the setup method is called during initialization.

    Args:
        patched_base_setup: Mocked setup function.
        instance: An instance of ExtendedBase.
    """
    assert isinstance(instance, ExtendedBase)
    patched_base_setup.assert_called_once_with()


def test_command_setup(
    patched_write_config: MagicMock,
    patched_manage_inventory: MagicMock,
    instance: ExtendedBase,
) -> None:
    """Ensure the setup method runs normally.

    Args:
        patched_write_config: Mocked write_config function.
        patched_manage_inventory: Mocked manage_inventory function.
        instance: An instance of ExtendedBase.

    """
    assert Path(instance._config.provisioner.inventory_file).parent.is_dir()  # type: ignore[union-attr]
    assert Path(instance._config.config_file).is_file()

    patched_manage_inventory.assert_called_once_with()
    patched_write_config.assert_called_once_with()


@pytest.mark.usefixtures("config_instance")
def test_execute_cmdline_scenarios(patched_execute_scenario: MagicMock) -> None:
    """Ensure execute_cmdline_scenarios runs normally.

    Execute_scenario is called once, indicating the function correctly loops over Scenarios.

    Args:
        patched_execute_scenario: Mocked execute_scenario function.
    """
    scenario_name = None
    args: MoleculeArgs = {}
    command_args: CommandArgs = {"destroy": "always", "subcommand": "test"}
    base.execute_cmdline_scenarios(scenario_name, args, command_args)

    scenario_count = 1
    assert patched_execute_scenario.call_count == scenario_count


@pytest.mark.usefixtures("config_instance")
def test_execute_cmdline_scenarios_missing(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Confirm execute_scenario exits properly when given a nonexistent scenario.

    Args:
        caplog: pytest caplog fixture.
    """
    scenario_name = ["nonexistent"]
    args: MoleculeArgs = {}
    command_args: CommandArgs = {"destroy": "always", "subcommand": "test"}

    with pytest.raises(ImmediateExit):
        base.execute_cmdline_scenarios(scenario_name, args, command_args)

    error_msg = "'molecule/nonexistent/molecule.yml' glob failed.  Exiting."
    assert error_msg in caplog.text


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
    scenario_name = ["default"]
    args: MoleculeArgs = {}
    command_args: CommandArgs = {"destroy": "always", "subcommand": "test"}

    base.execute_cmdline_scenarios(scenario_name, args, command_args)

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
    scenario_name = ["default"]
    args: MoleculeArgs = {}
    command_args: CommandArgs = {"destroy": "never", "subcommand": "test"}

    base.execute_cmdline_scenarios(scenario_name, args, command_args)

    assert patched_execute_subcommand.called
    assert not patched_prune.called


@pytest.mark.parametrize(
    ("destroy", "subcommands"),
    (
        ("always", ("cleanup", "destroy")),
        ("never", ()),
    ),
)
@pytest.mark.usefixtures("config_instance")
def test_execute_cmdline_scenarios_exit_destroy(  # noqa: PLR0913
    patched_execute_scenario: MagicMock,
    patched_prune: MagicMock,
    patched_execute_subcommand: MagicMock,
    patched_sysexit: MagicMock,
    destroy: Literal["always", "never"],
    subcommands: tuple[str, ...],
) -> None:
    """Ensure execute_cmdline_scenarios handles errors correctly when 'destroy' is set.

    - When ScenarioFailureError occurs, ImmediateExit should be raised immediately

    Args:
        patched_execute_scenario: Mocked execute_scenario function.
        patched_prune: Mocked prune function.
        patched_execute_subcommand: Mocked execute_subcommand function.
        patched_sysexit: Mocked util.sysexit function.
        destroy: Value to set 'destroy' arg to.
        subcommands: Expected subcommands to run after execute_scenario fails.
    """
    scenario_name = ["default"]
    args: MoleculeArgs = {}
    command_args: CommandArgs = {"destroy": destroy, "subcommand": "test"}
    patched_execute_scenario.side_effect = ScenarioFailureError()

    # Should raise ImmediateExit when ScenarioFailureError occurs
    with pytest.raises(ImmediateExit):
        base.execute_cmdline_scenarios(scenario_name, args, command_args)

    assert patched_execute_scenario.called


def test_execute_subcommand(config_instance: config.Config) -> None:
    """Ensure execute_subcommand runs normally.

    Scenario's config.action is mutated in-place for every sequence action,
        so make sure that is currently set to the executed action

    Args:
        config_instance: Mocked config_instance fixture.
    """
    assert config_instance.action != "list"
    assert base.execute_subcommand(config_instance, "list")
    assert config_instance.action == "list"


def test_execute_scenario(
    mocker: MockerFixture,
    patched_execute_subcommand: MagicMock,
) -> None:
    """Ensure execute_scenario runs normally.

    - call a spoofed scenario with a sequence that does not include destroy
    - execute_subcommand should be called once for each sequence item
    - prune should not be called, since the sequence has no destroy step

    Args:
        mocker: pytest mocker fixture.
        patched_execute_subcommand: Mocked execute_subcommand function.
    """
    scenario = mocker.Mock()
    scenario.sequence = ("a", "b", "c")

    base.execute_scenario(scenario)

    assert patched_execute_subcommand.call_count == len(scenario.sequence)
    assert not scenario.prune.called


def test_execute_scenario_destroy(
    mocker: MockerFixture,
    patched_execute_subcommand: MagicMock,
) -> None:
    """Ensure execute_scenario runs normally.

    - call a spoofed scenario with a sequence that includes destroy
    - execute_subcommand should be called once for each sequence item
    - prune should be called, since the sequence has a destroy step

    Args:
        mocker: pytest mocker fixture.
        patched_execute_subcommand: Mocked execute_subcommand function.
    """
    scenario = mocker.Mock()
    scenario.sequence = ("a", "b", "destroy", "c")

    base.execute_scenario(scenario)

    assert patched_execute_subcommand.call_count == len(scenario.sequence)
    assert scenario.prune.called


def test_execute_scenario_shared_destroy(
    mocker: MockerFixture,
    patched_execute_subcommand: MagicMock,
) -> None:
    """Ensure execute_scenario runs normally with shared_state.

    - call a spoofed scenario with a sequence that includes destroy
    - shared_state=True is passed which means destroy should be ignored.
    - execute_subcommand should be called once for each sequence item except destroy
    - prune should not be called, since destroy has been elided from the sequence.

    Args:
        mocker: pytest mocker fixture.
        patched_execute_subcommand: Mocked execute_subcommand function.
    """
    scenario = mocker.Mock()
    scenario.sequence = ("a", "b", "destroy", "c")
    expected_sequence = ("a", "b", "c")  # destroy should be skipped

    # Pass shared_state=True as keyword argument
    base.execute_scenario(scenario, shared_state=True)

    assert patched_execute_subcommand.call_count == len(expected_sequence)
    assert not scenario.prune.called


def test_get_configs(config_instance: config.Config) -> None:
    """Ensure get_configs returns a list of config.Config instances.

    Args:
        config_instance: Mocked config_instance fixture.
    """
    molecule_file = config_instance.molecule_file
    data = config_instance.config
    util.write_file(molecule_file, util.safe_dump(data))

    result = base.get_configs({}, {})
    assert len(result) == 1
    assert isinstance(result, list)
    assert isinstance(result[0], config.Config)


def test_verify_configs(config_instance: config.Config) -> None:
    """Ensure verify_configs runs normally and does not raise.

    Args:
        config_instance: Mocked config_instance fixture.
    """
    configs = [config_instance]
    base._verify_configs(configs)


def test_verify_configs_raises_with_no_configs(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Ensure verify_configs raises when no configs are provided.

    Args:
        caplog: pytest caplog fixture.
    """
    with pytest.raises(ScenarioFailureError) as e:
        base._verify_configs([])

    assert e.value.code == 1

    msg = "'molecule/*/molecule.yml' glob failed.  Exiting."
    assert msg in caplog.text


def test_verify_configs_raises_with_duplicate_configs(
    caplog: pytest.LogCaptureFixture,
    config_instance: config.Config,
) -> None:
    """Ensure verify_configs raises when duplicate configs are provided.

    Args:
        caplog: pytest caplog fixture.
        config_instance: Mocked config_instance fixture.
    """
    configs = [config_instance, config_instance]

    with pytest.raises(ScenarioFailureError) as e:
        base._verify_configs(configs)

    assert e.value.code == 1

    msg = "Duplicate scenario name 'default' found.  Exiting."
    assert msg in caplog.text


def test_get_subcommand() -> None:
    """Ensure get_subcommand returns the subcommand name."""
    assert base._get_subcommand(__name__) == "test_base"


@pytest.mark.parametrize(
    "shell",
    [  # noqa: PT007
        "bash",
        "zsh",
        "fish",
    ],
)
def test_command_completion(shell: str) -> None:
    """Ensure shell completion runs normally.

    Args:
        shell: Shell name.
    """
    env = os.environ.copy()
    env["_MOLECULE_COMPLETE"] = f"{shell}_source"
    bash_version = "0.0"

    if "bash" in shell:
        bash_version = subprocess.run(
            ["bash", "--version"],
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        ).stdout.split()[3][0:3]

    result = subprocess.run(
        ["molecule"],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    if "bash" in shell and (float(bash_version) < 4.4):  # noqa: PLR2004
        string = "Shell completion is not supported for Bash versions older than 4.4"
        assert string not in result.stdout
    else:
        assert result.returncode == 0
        assert "Found config file" not in result.stdout


def test_execute_cmdline_scenarios_handles_scenario_failure_error_when_all_scenarios(
    mocker: MockerFixture,
) -> None:
    """Test that ScenarioFailureError is handled gracefully when scenario_names is None.

    This tests the fix for the issue where running 'molecule test' with missing
    platforms would cause an unhandled exception instead of a clean exit.

    Args:
        mocker: Pytest mocker fixture.
    """
    # Mock get_configs to raise ScenarioFailureError
    mock_get_configs = mocker.patch("molecule.command.base.get_configs")
    mock_get_configs.side_effect = ScenarioFailureError("Test error", 1)

    scenario_names = None  # This triggers the "run all scenarios" path
    args: MoleculeArgs = {}
    command_args: CommandArgs = {"subcommand": "test"}

    # This should raise ScenarioFailureError directly (no conversion in this path)
    with pytest.raises(ScenarioFailureError) as exc_info:
        base.execute_cmdline_scenarios(scenario_names, args, command_args)

    # Verify that ScenarioFailureError was raised with the correct error code
    assert exc_info.value.code == 1


@pytest.mark.parametrize(
    ("cli_args", "config_value", "expected"),
    (
        # CLI: true cases
        (["--shared-state"], True, True),
        (["--shared-state"], False, True),
        (["--shared-state"], None, True),
        # CLI: false cases
        (["--no-shared-state"], True, False),
        (["--no-shared-state"], False, False),
        (["--no-shared-state"], None, False),
        # CLI: none cases
        ([], True, True),
        ([], False, False),
        ([], None, False),
    ),
    ids=(
        "cli_true_config_true_expect_true",
        "cli_true_config_false_expect_true",
        "cli_true_config_missing_expect_true",
        "cli_false_config_true_expect_false",
        "cli_false_config_false_expect_false",
        "cli_false_config_missing_expect_false",
        "cli_none_config_true_expect_true",
        "cli_none_config_false_expect_false",
        "cli_none_config_missing_expect_false",
    ),
)
def test_apply_cli_overrides_comprehensive(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    cli_args: list[str],
    *,
    config_value: bool | None,
    expected: bool,
) -> None:
    """Test all combinations of config file vs CLI shared_state values.

    This test validates that CLI arguments properly override config file values
    by using the actual Molecule shell.main entry point with a TestConfig that
    captures Config objects during CLI execution.

    Args:
        tmp_path: pytest temporary directory fixture.
        monkeypatch: pytest monkeypatch fixture.
        cli_args: CLI arguments to pass (e.g., ["--shared-state"]).
        config_value: Value to set in the config file.
        expected: Expected final shared_state value.
    """
    # 1. Create molecule.yml with or without shared_state
    molecule_dir = tmp_path / "molecule" / "default"
    molecule_dir.mkdir(parents=True)
    molecule_file = molecule_dir / "molecule.yml"

    config_content = "scenario:\n  name: default\n"
    if config_value is not None:
        config_content += f"shared_state: {str(config_value).lower()}\n"

    molecule_file.write_text(config_content)

    # 2. Capture configs and exit after _apply_cli_overrides
    captured_configs: list[config.Config] = []

    # Store the original method before patching
    original_apply_cli_overrides = config.Config._apply_cli_overrides

    def mock_apply_cli_overrides(self: config.Config) -> None:
        original_apply_cli_overrides(self)
        captured_configs.append(self)
        msg = "Test capture complete"
        raise ImmediateExit(msg, 0)

    monkeypatch.setattr("molecule.config.Config._apply_cli_overrides", mock_apply_cli_overrides)
    monkeypatch.chdir(tmp_path)

    argv = ["molecule", "test", *cli_args]
    monkeypatch.setattr("sys.argv", argv)

    captured_configs.clear()

    with pytest.raises(SystemExit) as exc_info:
        main.main(standalone_mode=False)

    # 6. Assert results
    assert exc_info.value.code == 0  # Our ImmediateExit code was handled properly
    assert len(captured_configs) >= 1  # At least one config was created
    assert captured_configs[0].shared_state is expected  # CLI override logic worked correctly


@pytest.mark.parametrize(
    ("env_var_value", "cli_args", "expected_report", "expected_borders"),
    (
        # Env var only cases - report
        ("true", [], True, True),
        ("false", [], False, False),
        ("1", [], True, True),
        ("0", [], False, False),
        ("yes", [], True, True),
        ("no", [], False, False),
        ("True", [], True, True),
        ("FALSE", [], False, False),
        # CLI overrides env var cases
        (
            "false",
            ["--report"],
            True,
            False,
        ),  # CLI --report overrides env false for report, but env still sets borders
        (
            "false",
            ["--command-borders"],
            False,
            True,
        ),  # CLI --command-borders overrides env false for borders, but env still sets report
        # CLI overrides both
        ("false", ["--report", "--command-borders"], True, True),  # CLI overrides both env vars
        # No env vars, no CLI (defaults)
        (None, [], False, False),
    ),
    ids=(
        "env_both_true_no_cli",
        "env_both_false_no_cli",
        "env_both_1_no_cli",
        "env_both_0_no_cli",
        "env_both_yes_no_cli",
        "env_both_no_no_cli",
        "env_both_True_no_cli",
        "env_both_FALSE_no_cli",
        "env_false_cli_report_true",
        "env_false_cli_borders_true",
        "env_false_cli_both_true",
        "no_env_no_cli_defaults",
    ),
)
def test_apply_env_overrides_comprehensive(  # noqa: PLR0913
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env_var_value: str | None,
    cli_args: list[str],
    *,
    expected_report: bool,
    expected_borders: bool,
) -> None:
    """Test all combinations of environment variables vs CLI arguments for report and command_borders.

    This test validates that environment variables are applied before CLI overrides,
    creating the precedence: defaults → env vars → CLI args.

    Args:
        tmp_path: pytest temporary directory fixture.
        monkeypatch: pytest monkeypatch fixture.
        env_var_value: Value to set in MOLECULE_REPORT/MOLECULE_COMMAND_BORDERS env vars.
        cli_args: CLI arguments to pass (e.g., ["--report"]).
        expected_report: Expected final report value.
        expected_borders: Expected final command_borders value.
    """
    # 1. Create basic molecule.yml
    molecule_dir = tmp_path / "molecule" / "default"
    molecule_dir.mkdir(parents=True)
    molecule_file = molecule_dir / "molecule.yml"
    molecule_file.write_text("scenario:\n  name: default\n")

    # 2. Set up environment variables
    env_vars = {}
    if env_var_value is not None:
        env_vars["MOLECULE_REPORT"] = env_var_value
        env_vars["MOLECULE_COMMAND_BORDERS"] = env_var_value

    # 3. Capture configs and exit after _apply_cli_overrides
    captured_configs: list[config.Config] = []

    # Store the original method before patching
    original_apply_cli_overrides = config.Config._apply_cli_overrides

    def mock_apply_cli_overrides(self: config.Config) -> None:
        original_apply_cli_overrides(self)
        captured_configs.append(self)
        msg = "Test capture complete"
        raise ImmediateExit(msg, 0)

    monkeypatch.setattr("molecule.config.Config._apply_cli_overrides", mock_apply_cli_overrides)
    monkeypatch.chdir(tmp_path)

    # 4. Set environment variables BEFORE calling main (so they exist during Config.__init__)
    for env_var, env_value in env_vars.items():
        monkeypatch.setenv(env_var, env_value)

    argv = ["molecule", "test", *cli_args]
    monkeypatch.setattr("sys.argv", argv)

    captured_configs.clear()

    with pytest.raises(SystemExit) as exc_info:
        main.main(standalone_mode=False)

    # 5. Assert results
    assert exc_info.value.code == 0  # Our ImmediateExit code was handled properly
    assert len(captured_configs) >= 1  # At least one config was created

    config_obj = captured_configs[0]
    assert config_obj.command_args.get("report", False) is expected_report
    assert config_obj.command_args.get("command_borders", False) is expected_borders


@pytest.mark.parametrize(
    ("env_report", "env_borders", "cli_args", "expected_report", "expected_borders"),
    (
        # Test precedence: CLI overrides env vars
        ("true", "false", ["--report", "--command-borders"], True, True),  # CLI overrides both
        ("false", "true", ["--report"], True, True),  # CLI overrides report, env borders remains
        (
            "true",
            "false",
            ["--command-borders"],
            True,
            True,
        ),  # CLI overrides borders, env report remains
        # Test different boolean formats
        ("1", "yes", [], True, True),  # Different truthy formats
        ("0", "no", [], False, False),  # Different falsy formats
        ("on", "off", [], True, False),  # More boolean formats
        # Test partial env vars (only one set)
        ("true", None, [], True, False),  # Only report env var set
        (None, "true", [], False, True),  # Only borders env var set
        (None, None, ["--report"], True, False),  # No env vars, only CLI
    ),
    ids=(
        "cli_overrides_both_env_vars",
        "cli_overrides_report_env_borders_remains",
        "cli_overrides_borders_env_report_remains",
        "env_mixed_truthy_formats",
        "env_mixed_falsy_formats",
        "env_on_off_formats",
        "env_report_only",
        "env_borders_only",
        "no_env_cli_report_only",
    ),
)
def test_env_var_cli_precedence(  # noqa: PLR0913
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env_report: str | None,
    env_borders: str | None,
    cli_args: list[str],
    *,
    expected_report: bool,
    expected_borders: bool,
) -> None:
    """Test precedence between environment variables and CLI arguments.

    This test specifically validates that CLI arguments take precedence over
    environment variables, and that different boolean formats work correctly.

    Args:
        tmp_path: Temporary directory for test files.
        monkeypatch: Pytest fixture for patching.
        env_report: Environment variable value for MOLECULE_REPORT.
        env_borders: Environment variable value for MOLECULE_COMMAND_BORDERS.
        cli_args: CLI arguments to test.
        expected_report: Expected value for report flag.
        expected_borders: Expected value for command_borders flag.
    """
    # 1. Create basic molecule.yml
    molecule_dir = tmp_path / "molecule" / "default"
    molecule_dir.mkdir(parents=True)
    molecule_file = molecule_dir / "molecule.yml"
    molecule_file.write_text("scenario:\n  name: default\n")

    # 2. Set up environment variables (only if not None)
    env_vars = {}
    if env_report is not None:
        env_vars["MOLECULE_REPORT"] = env_report
    if env_borders is not None:
        env_vars["MOLECULE_COMMAND_BORDERS"] = env_borders

    # 3. Same capture pattern as other tests
    captured_configs: list[config.Config] = []
    original_apply_cli_overrides = config.Config._apply_cli_overrides

    def mock_apply_cli_overrides(self: config.Config) -> None:
        original_apply_cli_overrides(self)
        captured_configs.append(self)
        msg = "Test capture complete"
        raise ImmediateExit(msg, 0)

    monkeypatch.setattr("molecule.config.Config._apply_cli_overrides", mock_apply_cli_overrides)
    monkeypatch.chdir(tmp_path)

    # 4. Set environment variables BEFORE calling main (so they exist during Config.__init__)
    for env_var, env_value in env_vars.items():
        monkeypatch.setenv(env_var, env_value)

    argv = ["molecule", "test", *cli_args]
    monkeypatch.setattr("sys.argv", argv)

    captured_configs.clear()

    with pytest.raises(SystemExit) as exc_info:
        main.main(standalone_mode=False)

    # 5. Assert results
    assert exc_info.value.code == 0
    assert len(captured_configs) >= 1

    config_obj = captured_configs[0]
    assert config_obj.command_args.get("report", False) is expected_report
    assert config_obj.command_args.get("command_borders", False) is expected_borders

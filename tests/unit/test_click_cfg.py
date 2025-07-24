"""Tests for the new Click configuration system with CliOption architecture."""

from __future__ import annotations

from dataclasses import replace

import click
import pytest

from click.testing import CliRunner

from molecule.click_cfg import CliOption, CliOptions, _sort_options, common_options


class TestCliOption:
    """Test the CliOption dataclass."""

    def test_basic_option_creation(self) -> None:
        """Test creating a basic CliOption."""
        option = CliOption(
            name="test-option",
            help="Test help text",
            short="-t",
            default="default_value",
        )

        assert option.name == "test-option"
        assert option.help == "Test help text"
        assert option.short == "-t"
        assert option.default == "default_value"
        assert option.multiple is False
        assert option.is_flag is False

    def test_flag_option_creation(self) -> None:
        """Test creating a flag option."""
        option = CliOption(
            name="verbose",
            help="Enable verbose output",
            is_flag=True,
            default=False,
        )

        assert option.is_flag is True
        assert option.default is False

    def test_multiple_option_creation(self) -> None:
        """Test creating a multiple option."""
        option = CliOption(
            name="tags",
            help="Specify tags",
            multiple=True,
            short="-t",
        )

        assert option.multiple is True

    def test_argument_option_creation(self) -> None:
        """Test creating an argument option."""
        option = CliOption(
            name="ansible_args",
            help="Ansible arguments",
            is_argument=True,
            nargs=-1,
        )

        assert option.is_argument is True
        assert option.nargs == -1

    def test_as_click_option_basic(self) -> None:
        """Test converting basic option to Click option."""
        option = CliOption(
            name="test-option",
            help="Test help",
            short="-t",
            default="value",
        )

        click_option = option.as_click_option()

        # Apply to a dummy function to test
        @click_option
        def dummy() -> None:
            pass

        assert hasattr(dummy, "__click_params__")
        param = dummy.__click_params__[0]
        assert param.opts == ["--test-option", "-t"]
        assert param.help == "Test help (default: value)"  # Now expect generated help text

    def test_as_click_option_flag(self) -> None:
        """Test converting flag option to Click option."""
        option = CliOption(
            name="verbose",
            help="Enable verbose output",
            is_flag=True,
            default=False,
        )

        click_option = option.as_click_option()

        # Apply to a dummy function to test
        @click_option
        def dummy() -> None:
            pass

        assert hasattr(dummy, "__click_params__")
        param = dummy.__click_params__[0]
        assert param.opts == ["--verbose"]
        assert param.secondary_opts == ["--no-verbose"]
        assert param.help == "Enable verbose output (default: disabled)"

    def test_as_click_option_with_choices(self) -> None:
        """Test converting option with choices to Click option."""
        option = CliOption(
            name="format",
            help="Output format",
            choices=["json", "yaml"],
            default="json",
        )

        click_option = option.as_click_option()

        # Apply to a dummy function to test
        @click_option
        def dummy() -> None:
            pass

        assert hasattr(dummy, "__click_params__")
        param = dummy.__click_params__[0]
        assert param.help == "Output format (default: json)"  # Expect generated help text

    def test_as_click_option_multiple(self) -> None:
        """Test converting multiple option to Click option."""
        option = CliOption(
            name="tags",
            help="Specify tags",
            multiple=True,
            short="-t",
        )

        click_option = option.as_click_option()

        @click_option
        def dummy() -> None:
            pass

        param = dummy.__click_params__[0]
        assert param.multiple is True

    def test_as_click_option_argument(self) -> None:
        """Test converting argument to Click argument."""
        option = CliOption(
            name="ansible_args",
            help="Ansible arguments",
            is_argument=True,
            nargs=-1,
        )

        click_option = option.as_click_option()

        @click_option
        def dummy() -> None:
            pass

        param = dummy.__click_params__[0]
        assert param.name == "ansible_args"
        assert param.nargs == -1
        assert param.type == click.UNPROCESSED

    def test_replace_functionality(self) -> None:
        """Test that dataclass replace works correctly."""
        base_option = CliOption(
            name="scenario-name",
            help="Base scenario option",
            short="-s",
            multiple=True,
        )

        modified_option = replace(base_option, default=["default"], multiple=False)

        assert modified_option.name == "scenario-name"
        assert modified_option.help == "Base scenario option"
        assert modified_option.short == "-s"
        assert modified_option.default == ["default"]
        assert modified_option.multiple is False

    def test_help_text_generation_basic(self) -> None:
        """Test basic help text generation."""
        option = CliOption(
            name="test-option",
            help="Test option",
            default="test_value",
        )

        help_text = option._generate_help_text()
        assert help_text == "Test option (default: test_value)"

    def test_help_text_generation_experimental(self) -> None:
        """Test experimental help text generation."""
        option = CliOption(
            name="test-option",
            help="Test option",
            experimental=True,
        )

        help_text = option._generate_help_text()
        assert help_text == "EXPERIMENTAL: Test option"

    def test_help_text_generation_experimental_with_default(self) -> None:
        """Test experimental help text with default value."""
        option = CliOption(
            name="test-option",
            help="Test option",
            default="test_value",
            experimental=True,
        )

        help_text = option._generate_help_text()
        assert help_text == "EXPERIMENTAL: Test option (default: test_value)"

    def test_help_text_generation_flag_enabled(self) -> None:
        """Test that flag options show enabled status correctly."""
        option = CliOption(
            name="test-flag",
            help="Test flag",
            is_flag=True,
            default=True,
        )

        help_text = option._generate_help_text()
        assert help_text == "Test flag (default: enabled)"

    def test_help_text_generation_flag_disabled(self) -> None:
        """Test that flag options show disabled status correctly."""
        option = CliOption(
            name="test-flag",
            help="Test flag",
            is_flag=True,
            default=False,
        )

        help_text = option._generate_help_text()
        assert help_text == "Test flag (default: disabled)"

    def test_help_text_generation_custom_default(self) -> None:
        """Test custom help_default overrides automatic generation."""
        option = CliOption(
            name="test-option",
            help="Test option",
            default="actual_value",
            help_default="custom_value",
        )

        help_text = option._generate_help_text()
        assert help_text == "Test option (default: custom_value)"

    def test_help_text_generation_custom_default_flag(self) -> None:
        """Test custom help_default overrides flag automatic generation."""
        option = CliOption(
            name="test-flag",
            help="Test flag",
            is_flag=True,
            default=False,
            help_default="custom_status",
        )

        help_text = option._generate_help_text()
        assert help_text == "Test flag (default: custom_status)"

    def test_help_text_generation_experimental_custom_default(self) -> None:
        """Test experimental with custom help_default."""
        option = CliOption(
            name="test-option",
            help="Test option",
            experimental=True,
            help_default="custom_value",
        )

        help_text = option._generate_help_text()
        assert help_text == "EXPERIMENTAL: Test option (default: custom_value)"

    def test_help_text_generation_multiple_list_default(self) -> None:
        """Test multiple option with list default."""
        option = CliOption(
            name="test-multiple",
            help="Test multiple",
            multiple=True,
            default=["value1", "value2"],
        )

        help_text = option._generate_help_text()
        assert help_text == "Test multiple (default: value1, value2)"

    def test_help_text_generation_multiple_single_default(self) -> None:
        """Test multiple option with single item list default."""
        option = CliOption(
            name="test-multiple",
            help="Test multiple",
            multiple=True,
            default=["value1"],
        )

        help_text = option._generate_help_text()
        assert help_text == "Test multiple (default: value1)"

    def test_help_text_generation_argument_no_default(self) -> None:
        """Test that arguments don't show default info."""
        option = CliOption(
            name="test-arg",
            help="Test argument",
            is_argument=True,
            default="value",
        )

        help_text = option._generate_help_text()
        assert help_text == "Test argument"
        assert "default" not in help_text

    def test_help_text_generation_choice_with_default(self) -> None:
        """Test choice option with default."""
        option = CliOption(
            name="test-choice",
            help="Test choice",
            choices=["option1", "option2"],
            default="option1",
        )

        help_text = option._generate_help_text()
        assert help_text == "Test choice (default: option1)"


class TestCliOptions:
    """Test the CliOptions registry class."""

    def test_cli_options_instantiation(self) -> None:
        """Test that CliOptions can be instantiated."""
        options = CliOptions()
        assert isinstance(options, CliOptions)

    def test_scenario_name_base(self) -> None:
        """Test the base scenario_name option."""
        options = CliOptions()
        scenario = options.scenario_name

        assert scenario.name == "scenario-name"
        assert scenario.short == "-s"
        assert scenario.multiple is True
        assert scenario.default is None

    def test_scenario_name_with_default(self) -> None:
        """Test scenario_name with default."""
        options = CliOptions()
        scenario = options.scenario_name_with_default

        assert scenario.name == "scenario-name"
        assert scenario.default == ["default"]  # MOLECULE_DEFAULT_SCENARIO_NAME as list
        assert "default" in scenario._generate_help_text()  # Check generated help text

    def test_scenario_name_single(self) -> None:
        """Test single scenario_name without default."""
        options = CliOptions()
        scenario = options.scenario_name_single

        assert scenario.name == "scenario-name"
        assert scenario.multiple is False
        assert scenario.default is None

    def test_scenario_name_single_with_default(self) -> None:
        """Test single scenario_name with default."""
        options = CliOptions()
        scenario = options.scenario_name_single_with_default

        assert scenario.name == "scenario-name"
        assert scenario.multiple is False
        assert scenario.default == "default"
        assert "default" in scenario._generate_help_text()  # Check generated help text

    def test_exclude_option(self) -> None:
        """Test the exclude option."""
        options = CliOptions()
        exclude = options.exclude

        assert exclude.name == "exclude"
        assert exclude.short == "-e"
        assert exclude.multiple is True

    def test_all_scenarios_option(self) -> None:
        """Test the all_scenarios flag option."""
        options = CliOptions()
        all_opt = options.all_scenarios

        assert all_opt.name == "all"
        assert all_opt.is_flag is True
        assert all_opt.default is False

    def test_driver_options(self) -> None:
        """Test driver-related options."""
        options = CliOptions()

        driver = options.driver_name
        assert driver.name == "driver-name"
        assert driver.short == "-d"

        driver_with_choices = options.driver_name_with_choices
        assert driver_with_choices.name == "driver-name"
        assert driver_with_choices.choices is not None
        assert len(driver_with_choices.choices) > 0  # Should have available drivers

    def test_platform_options(self) -> None:
        """Test platform-related options."""
        options = CliOptions()

        platform = options.platform_name
        assert platform.name == "platform-name"
        assert platform.short == "-p"

        platform_with_default = options.platform_name_with_default
        assert platform_with_default.default is None  # MOLECULE_PLATFORM_NAME defaults to None
        assert platform_with_default.help_default == "None"
        assert "(default: None)" in platform_with_default._generate_help_text()

    def test_execution_options(self) -> None:
        """Test execution-related options."""
        options = CliOptions()

        parallel = options.parallel
        assert parallel.name == "parallel"
        assert parallel.is_flag is True
        assert "(default: disabled)" in parallel._generate_help_text()

        force = options.force
        assert force.name == "force"
        assert force.short == "-f"
        assert force.is_flag is True
        assert "(default: disabled)" in force._generate_help_text()

        destroy = options.destroy
        assert destroy.name == "destroy"
        assert destroy.choices == ["always", "never"]
        assert destroy.default == "always"
        assert "(default: always)" in destroy._generate_help_text()

    def test_output_options(self) -> None:
        """Test output and reporting options."""
        options = CliOptions()

        report = options.report
        assert report.name == "report"
        assert report.is_flag is True
        assert report.experimental is True
        help_text = report._generate_help_text()
        assert "EXPERIMENTAL:" in help_text
        assert "(default: disabled)" in help_text

        shared_inventory = options.shared_inventory
        assert shared_inventory.name == "shared-inventory"
        assert shared_inventory.is_flag is True
        assert shared_inventory.experimental is True
        help_text = shared_inventory._generate_help_text()
        assert "EXPERIMENTAL:" in help_text
        assert "(default: disabled)" in help_text

        shared_state = options.shared_state
        assert shared_state.name == "shared-state"
        assert shared_state.is_flag is True
        assert shared_state.experimental is True
        help_text = shared_state._generate_help_text()
        assert "EXPERIMENTAL:" in help_text
        assert "(default: disabled)" in help_text

    def test_format_options(self) -> None:
        """Test format options."""
        options = CliOptions()

        format_simple = options.format_simple
        assert format_simple.name == "format"
        assert format_simple.short == "-f"
        assert format_simple.choices == ["simple", "plain"]
        assert "(default: simple)" in format_simple._generate_help_text()

        format_full = options.format_full
        assert format_full.choices == ["simple", "plain", "yaml"]
        assert "(default: simple)" in format_full._generate_help_text()

    def test_connection_options(self) -> None:
        """Test connection options."""
        options = CliOptions()

        host = options.host
        assert host.name == "host"
        assert host.short == "-h"

    def test_dependency_provisioner_options(self) -> None:
        """Test dependency and provisioner options."""
        options = CliOptions()

        dependency = options.dependency_name
        assert dependency.name == "dependency-name"
        assert dependency.choices == ["galaxy"]
        assert dependency.default == "galaxy"
        assert "(default: galaxy)" in dependency._generate_help_text()

        provisioner = options.provisioner_name
        assert provisioner.name == "provisioner-name"
        assert provisioner.choices == ["ansible"]
        assert provisioner.default == "ansible"
        assert "(default: ansible)" in provisioner._generate_help_text()

    def test_argument_options(self) -> None:
        """Test argument options."""
        options = CliOptions()

        ansible_args = options.ansible_args
        assert ansible_args.name == "ansible_args"
        assert ansible_args.is_argument is True
        assert ansible_args.nargs == -1

        subcommand = options.subcommand
        assert subcommand.name == "subcommand"
        assert subcommand.is_argument is True
        assert subcommand.nargs == 1

    def test_experimental_flag_functionality(self) -> None:
        """Test that experimental flag works correctly."""
        options = CliOptions()

        # Test experimental options
        experimental_options = [
            options.report,
            options.shared_inventory,
            options.shared_state,
        ]

        for option in experimental_options:
            assert option.experimental is True
            help_text = option._generate_help_text()
            assert help_text.startswith("EXPERIMENTAL:")

        # Test non-experimental options
        non_experimental_options = [
            options.parallel,
            options.force,
            options.destroy,
        ]

        for option in non_experimental_options:
            assert option.experimental is False
            help_text = option._generate_help_text()
            assert not help_text.startswith("EXPERIMENTAL:")

    def test_help_text_generation(self) -> None:
        """Test automatic help text generation with defaults."""
        options = CliOptions()

        # Test flag option (should show disabled/enabled)
        force = options.force
        force_help = force._generate_help_text()
        assert "(default: disabled)" in force_help

        # Test choice option with default
        destroy = options.destroy
        destroy_help = destroy._generate_help_text()
        assert "(default: always)" in destroy_help

        # Test multiple option with list default
        scenario = options.scenario_name_with_default
        scenario_help = scenario._generate_help_text()
        assert "(default: default)" in scenario_help

        # Test option without default
        host = options.host
        host_help = host._generate_help_text()
        assert "default" not in host_help

        # Test argument (should not show default info)
        ansible_args = options.ansible_args
        args_help = ansible_args._generate_help_text()
        assert "default" not in args_help

        # Test custom help_default
        platform_with_default = options.platform_name_with_default
        platform_help = platform_with_default._generate_help_text()
        assert "(default: None)" in platform_help


class TestCommonOptionsDecorator:
    """Test the common_options decorator."""

    def test_decorator_with_no_additional_options(self) -> None:
        """Test decorator with no additional options (just COMMON_OPTIONS)."""

        @click.command()
        @common_options()
        def test_command(ctx: click.Context) -> None:
            # Should have all COMMON_OPTIONS available
            scenario = ctx.params["scenario_name"]
            exclude = ctx.params["exclude"]
            report = ctx.params["report"]
            click.echo(f"scenario={scenario}, exclude={exclude}, report={report}")

        runner = CliRunner()
        result = runner.invoke(
            test_command,
            ["--scenario-name", "test", "--exclude", "skip", "--report"],
        )

        assert result.exit_code == 0
        assert "scenario=('test',)" in result.output
        assert "exclude=('skip',)" in result.output
        assert "report=True" in result.output

    def test_decorator_with_additional_string_options(self) -> None:
        """Test decorator with additional string options."""

        @click.command()
        @common_options("parallel", "force")
        def test_command(ctx: click.Context) -> None:
            # Should have COMMON_OPTIONS plus additional ones
            scenario = ctx.params["scenario_name"]
            parallel = ctx.params["parallel"]
            force = ctx.params["force"]
            click.echo(f"scenario={scenario}, parallel={parallel}, force={force}")

        runner = CliRunner()
        result = runner.invoke(test_command, ["--scenario-name", "test", "--parallel", "--force"])

        assert result.exit_code == 0
        assert "scenario=('test',)" in result.output
        assert "parallel=True" in result.output
        assert "force=True" in result.output

    def test_decorator_deduplication(self) -> None:
        """Test that decorator deduplicates options when same option is in COMMON_OPTIONS and additional."""

        @click.command()
        @common_options(
            "scenario_name_with_default",
            "report",
        )  # report is already in COMMON_OPTIONS
        def test_command(ctx: click.Context) -> None:
            scenario = ctx.params["scenario_name"]
            report = ctx.params["report"]
            click.echo(f"scenario={scenario}, report={report}")

        runner = CliRunner()
        result = runner.invoke(test_command, ["--scenario-name", "test", "--report"])

        assert result.exit_code == 0
        assert "scenario=('test',)" in result.output
        assert "report=True" in result.output

    def test_decorator_with_single_option(self) -> None:
        """Test decorator with a single option."""

        @click.command()  # Applied last - converts to Click command
        @common_options("parallel")  # Applied first - adds options
        def test_command(ctx: click.Context) -> None:
            click.echo(f"parallel={ctx.params['parallel']}")

        runner = CliRunner()
        result = runner.invoke(test_command, ["--parallel"])

        assert result.exit_code == 0
        assert "parallel=True" in result.output

    def test_decorator_with_multiple_options(self) -> None:
        """Test decorator with multiple options."""

        @click.command()
        @common_options("scenario_name_with_default", "parallel", "force")
        def test_command(ctx: click.Context) -> None:
            scenario = ctx.params["scenario_name"]
            parallel = ctx.params["parallel"]
            force = ctx.params["force"]
            click.echo(f"scenario={scenario}, parallel={parallel}, force={force}")

        runner = CliRunner()
        result = runner.invoke(test_command, ["--scenario-name", "test", "--parallel", "--force"])

        assert result.exit_code == 0
        assert "scenario=('test',)" in result.output  # Fixed: tuple format
        assert "parallel=True" in result.output
        assert "force=True" in result.output

    def test_decorator_with_argument(self) -> None:
        """Test decorator with argument option."""

        @click.command()
        @common_options("ansible_args")
        def test_command(ctx: click.Context) -> None:
            args = ctx.params["ansible_args"]
            click.echo(f"args={args}")

        runner = CliRunner()
        result = runner.invoke(test_command, ["--", "--extra-vars", "test=1"])

        assert result.exit_code == 0
        assert "args=('--extra-vars', 'test=1')" in result.output

    def test_decorator_with_choices(self) -> None:
        """Test decorator with choice option."""

        @click.command()
        @common_options("format_simple")
        def test_command(ctx: click.Context) -> None:
            output_format = ctx.params["format"]
            click.echo(f"format={output_format}")

        runner = CliRunner()
        result = runner.invoke(test_command, ["--format", "plain"])

        assert result.exit_code == 0
        assert "format=plain" in result.output

    def test_decorator_with_multiple_scenarios(self) -> None:
        """Test decorator with multiple scenario names."""

        @click.command()
        @common_options("scenario_name")
        def test_command(ctx: click.Context) -> None:
            scenarios = ctx.params["scenario_name"]
            click.echo(f"scenarios={scenarios}")

        runner = CliRunner()
        result = runner.invoke(
            test_command,
            ["--scenario-name", "test1", "--scenario-name", "test2"],
        )

        assert result.exit_code == 0
        assert "scenarios=('test1', 'test2')" in result.output  # Fixed: tuple format

    def test_decorator_help_output(self) -> None:
        """Test that help output includes all options."""

        @click.command()
        @common_options("scenario_name_with_default", "parallel")
        def test_command(ctx: click.Context) -> None:
            pass

        runner = CliRunner()
        result = runner.invoke(test_command, ["--help"])

        assert result.exit_code == 0
        assert "--scenario-name" in result.output
        assert "--parallel" in result.output
        assert "-s" in result.output  # short form for scenario

    def test_decorator_invalid_option_name(self) -> None:
        """Test decorator with invalid option name."""
        with pytest.raises(AttributeError):

            @click.command()
            @common_options("nonexistent_option")
            def test_command(ctx: click.Context) -> None:
                pass

    def test_ctx_only_function_signature(self) -> None:
        """Test that functions only need ctx parameter."""

        @click.command()
        @common_options("parallel", "force")
        def test_command(ctx: click.Context) -> None:
            # Function signature only has ctx, but can access all options
            parallel = ctx.params["parallel"]
            force = ctx.params["force"]
            click.echo(f"parallel={parallel}, force={force}")

        runner = CliRunner()
        result = runner.invoke(test_command, ["--parallel", "--force"])

        assert result.exit_code == 0
        assert "parallel=True" in result.output
        assert "force=True" in result.output

    def test_complex_scenario_composition(self) -> None:
        """Test complex scenario with multiple option types."""

        @click.command()
        @common_options(
            "scenario_name_with_default",
            "exclude",
            "all_scenarios",
            "driver_name_with_choices",
            "parallel",
            "format_simple",
        )
        def test_command(ctx: click.Context) -> None:
            params = ctx.params
            click.echo(f"Complex command: {params}")

        runner = CliRunner()
        result = runner.invoke(
            test_command,
            [
                "--scenario-name",
                "test1",
                "--exclude",
                "excluded",
                "--all",
                "--driver-name",
                "default",  # Fixed: use 'default' instead of 'delegated'
                "--parallel",
                "--format",
                "plain",
            ],
        )

        assert result.exit_code == 0
        # Verify all parameters are accessible
        assert "scenario_name" in result.output
        assert "exclude" in result.output
        assert "all" in result.output
        assert "driver_name" in result.output
        assert "parallel" in result.output
        assert "format" in result.output

    def test_option_sort_order(self) -> None:
        """Test that options are sorted in the correct order."""
        cli_options = CliOptions()

        # Create a test set with options from each category
        test_options = [
            cli_options.force,  # Short form, non-experimental
            cli_options.scenario_name_with_default,  # Should be first (scenario-name)
            cli_options.report,  # Experimental
            cli_options.exclude,  # Should be second
            cli_options.all_scenarios,  # Should be third (all)
            cli_options.parallel,  # Long form, non-experimental
            cli_options.shared_state,  # Experimental
            cli_options.driver_name,  # Short form, non-experimental
        ]

        sorted_options = _sort_options(test_options)
        sorted_names = [opt.name for opt in sorted_options]

        # Verify the expected order
        expected_order = [
            "scenario-name",  # Section 1: Core workflow (scenario-name, exclude, all)
            "exclude",  # Section 1: Core workflow (scenario-name, exclude, all)
            "all",  # Section 1: Core workflow (scenario-name, exclude, all)
            "driver-name",  # Section 2: short forms (alphabetical): driver-name
            "force",  # Section 2: short forms (alphabetical): force
            "parallel",  # Section 3: long forms (alphabetical)
            "report",  # Section 4: experimental (alphabetical): report
            "shared-state",  # Section 4: experimental (alphabetical): shared-state
        ]

        assert sorted_names == expected_order, f"Expected {expected_order}, got {sorted_names}"

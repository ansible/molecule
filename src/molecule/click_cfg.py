"""New Click Configuration System with CliOption Architecture.

This module provides a framework-agnostic approach to CLI option management
that supports both Click and future migration to argparse or other frameworks.
It also contains Click-specific decorators and utilities.
"""

from __future__ import annotations

import functools
import logging

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any

import click

from click_help_colors import HelpColorsCommand, HelpColorsGroup

from molecule import util
from molecule.ansi_output import should_do_markup
from molecule.api import drivers
from molecule.config import MOLECULE_PARALLEL
from molecule.constants import MOLECULE_DEFAULT_SCENARIO_NAME, MOLECULE_PLATFORM_NAME
from molecule.exceptions import ImmediateExit


if TYPE_CHECKING:
    from collections.abc import Callable

    ClickCommand = Callable[[Callable[..., None]], click.Command]
    ClickGroup = Callable[[Callable[..., None]], click.Group]


# Common option combinations for different command types
# Options that most workflow commands share
COMMON_OPTIONS = [
    "all_scenarios",
    "exclude",
    "report",
    "scenario_name_with_default",
    "shared_state",
    "command_borders",
]


@dataclass
class CliOption:
    """Framework-agnostic CLI option definition.

    Attributes:
        name: The name of the CLI option.
        help: Help text for the option.
        short: Short form flag (e.g., "-s") or None.
        multiple: Whether the option can be specified multiple times.
        default: Default value for the option.
        type: Python type for the option value.
        choices: List of valid choices for the option.
        is_flag: Whether this is a boolean flag option.
        required: Whether the option is required.
        is_argument: Whether this is a positional argument rather than an option.
        nargs: Number of arguments for positional arguments.
        experimental: Whether this is an experimental feature.
        help_default: Custom default value to display in help text.
    """

    name: str
    help: str
    short: str | None = None
    multiple: bool = False
    default: Any = None
    type: type | None = None
    choices: list[str] | None = None
    is_flag: bool = False
    required: bool = False
    is_argument: bool = False
    nargs: int = 1
    experimental: bool = False
    help_default: str | None = None

    def _generate_help_text(self) -> str:
        """Generate help text with automatic default value inclusion.

        Returns:
            Formatted help text with experimental prefix and default info.
        """
        help_text = self.help

        # Add experimental prefix
        if self.experimental:
            help_text = f"EXPERIMENTAL: {help_text}"

        # Early exit for arguments - they don't show default info
        if self.is_argument:
            return help_text

        default_value = None

        # Use custom help_default if provided
        if self.help_default is not None:
            default_value = self.help_default
        # For flags, show disabled/enabled
        elif self.is_flag and self.default is not None:
            default_value = "enabled" if self.default else "disabled"
        # For options with actual defaults
        elif self.default is not None:
            if self.multiple and isinstance(self.default, list) and self.default:
                if len(self.default) == 1:
                    default_value = str(self.default[0])
                else:
                    default_value = ", ".join(map(str, self.default))
            else:
                default_value = str(self.default)

        # Append default info if we have a value
        if default_value is not None:
            help_text += f" (default: {default_value})"

        return help_text

    def as_click_option(self) -> Callable[..., Any]:
        """Convert to Click option decorator.

        Returns:
            A Click option or argument decorator function.
        """
        if self.is_argument:
            return click.argument(
                self.name.replace("-", "_"),
                nargs=self.nargs,
                type=click.UNPROCESSED if self.type is None else self.type,
            )

        params = [f"--{self.name}"]
        if self.short:
            params.append(self.short)

        kwargs = {
            "help": self._generate_help_text(),
            "default": self.default,
            "multiple": self.multiple,
            "required": self.required,
        }

        # Type and choices
        if self.choices:
            kwargs["type"] = click.Choice(self.choices)
        elif self.type:
            kwargs["type"] = self.type

        # Handle flag options
        if self.is_flag:
            return click.option(f"--{self.name}/--no-{self.name}", **kwargs)

        return click.option(*params, **kwargs)


class CliOptions:
    """Central registry of all CLI options with support for variants."""

    # Alphabetically ordered properties

    @property
    def all_scenarios(self) -> CliOption:
        """Target all scenarios option."""
        return CliOption(
            name="all",
            help="Target all scenarios. Overrides scenario-name. For 'reset', this includes shared state and inventory.",
            is_flag=True,
            default=False,
        )

    @property
    def ansible_args(self) -> CliOption:
        """Ansible arguments."""
        return CliOption(
            name="ansible_args",
            help="Arguments to forward to Ansible",
            is_argument=True,
            nargs=-1,
        )

    @property
    def dependency_name(self) -> CliOption:
        """Dependency name option."""
        return CliOption(
            name="dependency-name",
            help="Name of dependency to initialize.",
            choices=["galaxy"],
            default="galaxy",
        )

    @property
    def destroy(self) -> CliOption:
        """Destroy strategy option."""
        return CliOption(
            name="destroy",
            help="The destroy strategy used at the conclusion of a Molecule run.",
            choices=["always", "never"],
            default="always",
        )

    @property
    def driver_name(self) -> CliOption:
        """Driver name option without choices."""
        return CliOption(
            name="driver-name",
            help="Name of the driver to use.",
            short="-d",
        )

    @property
    def driver_name_with_choices(self) -> CliOption:
        """Driver name option with available choices."""
        return replace(
            self.driver_name,
            choices=[str(s) for s in drivers()],
            help="Name of driver to use.",
        )

    @property
    def exclude(self) -> CliOption:
        """Exclude scenarios option."""
        return CliOption(
            name="exclude",
            help="Name of the scenario to exclude from targeting. May be specified multiple times.",
            short="-e",
            multiple=True,
        )

    @property
    def force(self) -> CliOption:
        """Force execution option."""
        return CliOption(
            name="force",
            help="Enable or disable force mode.",
            short="-f",
            is_flag=True,
            default=False,
        )

    @property
    def format_full(self) -> CliOption:
        """Format option with full choices including yaml."""
        return CliOption(
            name="format",
            help="Change output format.",
            short="-f",
            choices=["simple", "plain", "yaml"],
            default="simple",
        )

    @property
    def format_simple(self) -> CliOption:
        """Format option with simple choices."""
        return CliOption(
            name="format",
            help="Change output format.",
            short="-f",
            choices=["simple", "plain"],
            default="simple",
        )

    @property
    def host(self) -> CliOption:
        """Host connection option."""
        return CliOption(
            name="host",
            help="Host to access.",
            short="-h",
        )

    @property
    def parallel(self) -> CliOption:
        """Parallel execution option."""
        return CliOption(
            name="parallel",
            help="Enable or disable parallel mode.",
            is_flag=True,
            default=MOLECULE_PARALLEL,
        )

    @property
    def platform_name(self) -> CliOption:
        """Platform name option."""
        return CliOption(
            name="platform-name",
            help="Name of the platform to target.",
            short="-p",
        )

    @property
    def platform_name_with_default(self) -> CliOption:
        """Platform name option with default."""
        return replace(
            self.platform_name,
            default=MOLECULE_PLATFORM_NAME,
            help="Name of the platform to target only.",
            help_default="None",
        )

    @property
    def provisioner_name(self) -> CliOption:
        """Provisioner name option."""
        return CliOption(
            name="provisioner-name",
            help="Name of provisioner to initialize.",
            choices=["ansible"],
            default="ansible",
        )

    @property
    def report(self) -> CliOption:
        """Reporting option."""
        return CliOption(
            name="report",
            help="Enable or disable end-of-run summary report.",
            is_flag=True,
            default=False,
            experimental=True,
        )

    @property
    def scenario_name(self) -> CliOption:
        """Base scenario name option without default."""
        return CliOption(
            name="scenario-name",
            help="Name of the scenario to target.  May be specified multiple times.",
            short="-s",
            multiple=True,
        )

    @property
    def scenario_name_with_default(self) -> CliOption:
        """Scenario name option with default value (multiple)."""
        return replace(
            self.scenario_name,
            default=[MOLECULE_DEFAULT_SCENARIO_NAME],
        )

    @property
    def scenario_name_single(self) -> CliOption:
        """Single scenario name option without default."""
        return replace(
            self.scenario_name,
            multiple=False,
            help="Name of the scenario to target.",
        )

    @property
    def scenario_name_single_with_default(self) -> CliOption:
        """Single scenario name option with default."""
        return replace(
            self.scenario_name_single,
            default=MOLECULE_DEFAULT_SCENARIO_NAME,
            help="Name of the scenario to target.",
        )

    @property
    def shared_state(self) -> CliOption:
        """Shared state option."""
        return CliOption(
            name="shared-state",
            help="Enable or disable sharing (some) state between scenarios.",
            is_flag=True,
            default=False,
            experimental=True,
        )

    @property
    def command_borders(self) -> CliOption:
        """Command borders option."""
        return CliOption(
            name="command-borders",
            help="Enable or disable borders around command output.",
            is_flag=True,
            default=False,
            experimental=True,
        )

    @property
    def subcommand(self) -> CliOption:
        """Subcommand argument for matrix command."""
        return CliOption(
            name="subcommand",
            help="Subcommand to analyze",
            is_argument=True,
            nargs=1,
        )


def options(option_names: list[str]) -> Callable[..., Any]:
    """Decorator that adds CLI options to a command function.

    Args:
        option_names: List of option names to apply from CliOptions class.

    Example:
        @options(["scenario_name_with_default", "parallel", "force"])
        def my_command(ctx: click.Context) -> None:
            scenario = ctx.params["scenario_name"]
            parallel = ctx.params["parallel"]
            force = ctx.params["force"]

    Returns:
        The decorated function with the specified Click options applied.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        cli_options = CliOptions()

        # Create the wrapper function with click.pass_context applied to IT
        @click.pass_context  # type: ignore[arg-type]
        @functools.wraps(func)
        def wrapper(ctx: click.Context, *_args: object, **_kwargs: object) -> object:
            # All options and arguments are available via ctx.params
            # Functions only need ctx, so we ignore any additional args/kwargs Click might pass
            return func(ctx)

        # Get all the CliOption instances
        options_list = [getattr(cli_options, option_name) for option_name in option_names]

        # Sort options and apply them to the wrapper (reverse order for correct display)
        sorted_options = _sort_options(options_list)
        for option in reversed(sorted_options):
            click_option = option.as_click_option()
            wrapper = click_option(wrapper)

        return wrapper

    return decorator


def common_options(*additional_options: str) -> Callable[..., Any]:
    """Decorator that adds common CLI options plus any additional options to a command function.

    This decorator includes COMMON_OPTIONS by default and adds any additional
    options provided as arguments.

    Args:
        *additional_options: Additional option names to include beyond COMMON_OPTIONS.

    Example:
        @common_options("parallel", "force")
        def my_command(ctx: click.Context) -> None:
            # All COMMON_OPTIONS plus parallel and force are available
            scenario = ctx.params["scenario_name"]  # from COMMON_OPTIONS
            parallel = ctx.params["parallel"]       # additional
            force = ctx.params["force"]             # additional

        @common_options()
        def my_other_command(ctx: click.Context) -> None:
            # Just COMMON_OPTIONS are available
            scenario = ctx.params["scenario_name"]

    Returns:
        The decorated function with common options and additional options applied.
    """
    option_names = list(set(COMMON_OPTIONS + list(additional_options)))
    return options(option_names)


def _sort_options(option_list: list[CliOption]) -> list[CliOption]:
    """Sort options in user-friendly order with clear sections.

    Order:
    1. Core workflow options (scenario-name, exclude, all)
    2. Options with short forms (alphabetical)
    3. Long options without short forms (alphabetical)
    4. Experimental options (alphabetical)

    Args:
        option_list: List of CliOption instances.

    Returns:
        List of sorted CliOption instances.
    """
    # Convert to dict for easy lookup and removal
    options_by_name = {opt.name: opt for opt in option_list}

    # Core workflow options (scenario-name, exclude, all)
    core_workflow_names = ["scenario-name", "exclude", "all"]
    core_workflow_options = [
        options_by_name.pop(name) for name in core_workflow_names if name in options_by_name
    ]

    # Extract and sort each category
    experimental_options = sorted(
        [opt for opt in options_by_name.values() if opt.experimental],
        key=lambda opt: opt.name,
    )
    short_form_options = sorted(
        [opt for opt in options_by_name.values() if not opt.experimental and opt.short is not None],
        key=lambda opt: opt.name,
    )
    long_form_options = sorted(
        [opt for opt in options_by_name.values() if not opt.experimental and opt.short is None],
        key=lambda opt: opt.name,
    )

    # Build final list by combining all sections
    return core_workflow_options + short_form_options + long_form_options + experimental_options


class FirstLineHelpMixin:
    """Mixin to modify help text to only show the first line.

    Attributes:
        help: The help text that will be modified to show only first line.
    """

    help: str | None

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize the command.

        Args:
            *args: Positional arguments to pass to parent.
            **kwargs: Keyword arguments to pass to parent.
        """
        super().__init__(*args, **kwargs)
        if self.help:
            first_line = self.help.strip().split("\n")[0].strip()
            self.help = first_line


class FirstLineHelpCommand(FirstLineHelpMixin, HelpColorsCommand):
    """Override the default help generation to remove the args section."""


class FirstLineHelpGroup(FirstLineHelpMixin, HelpColorsGroup):
    """Override the default help generation to remove the args section."""


def click_group_ex() -> ClickGroup:
    """Return extended version of click.group().

    Returns:
        Click command group.
    """
    # Color coding used to group command types, documented only here as we may
    # decide to change them later.
    # green : (default) as sequence step
    # blue : molecule own command, not dependent on scenario
    # yellow : special commands, like full test sequence, or login
    return click.group(
        cls=FirstLineHelpGroup,
        # Workaround to disable click help line truncation to ~80 chars
        # https://github.com/pallets/click/issues/486
        context_settings={
            "max_content_width": 9999,
            "color": should_do_markup(),
            "help_option_names": ["-h", "--help"],
        },
        help_headers_color="yellow",
        help_options_color="green",
        help_options_custom_colors={
            "drivers": "blue",
            "init": "blue",
            "list": "blue",
            "matrix": "blue",
            "login": "bright_yellow",
            "reset": "blue",
            "test": "bright_yellow",
        },
    )


def click_command_ex(name: str | None = None) -> Callable[[Callable[..., Any]], click.Command]:
    """Return extended version of click.command() with immediate exit exception handling.

    Args:
        name: A replacement name in the case the automatic one is insufficient.

    Returns:
        Click command decorator with exception handling.
    """

    def decorator(func: Callable[..., Any]) -> click.Command:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            try:
                return func(*args, **kwargs)
            except ImmediateExit as exc:
                logger = logging.getLogger(__name__)

                # Check if debug mode is enabled
                ctx = click.get_current_context(silent=True)
                debug_mode = False
                if ctx and ctx.obj and isinstance(ctx.obj, dict):
                    debug_mode = ctx.obj.get("args", {}).get("debug", False)

                # For success (code 0), always use info logging
                # For failures (code != 0), use debug-aware logging
                if exc.code == 0:
                    logger.info(exc.message)
                elif debug_mode:
                    # Show full traceback in debug mode for failures
                    logger.exception(exc.message)
                else:
                    # Show only the error message in normal mode for failures
                    logger.error(exc.message)  # noqa: TRY400

                util.sysexit(code=exc.code)

        # Apply the click.command decorator to the wrapper
        return click.command(
            cls=FirstLineHelpCommand,
            name=name,
            help_headers_color="yellow",
            help_options_color="green",
        )(wrapper)

    return decorator

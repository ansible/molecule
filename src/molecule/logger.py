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
"""Logging Module."""

from __future__ import annotations

import logging
import os
import time

from functools import wraps
from typing import TYPE_CHECKING, Protocol, cast

from ansible_compat.ports import cache

from molecule.ansi_output import AnsiOutput
from molecule.console import console, original_stderr
from molecule.constants import ANSICodes as A
from molecule.reporting.definitions import CompletionState
from molecule.text import underscore


if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, MutableMapping
    from typing import ParamSpec, TypeVar

    from molecule.config import Config

    P = ParamSpec("P")
    R = TypeVar("R")


LOG_LEVEL_LUT = {
    0: logging.INFO,
    1: logging.DEBUG,
}


class HasConfig(Protocol):
    """A class with a _config attribute.

    There are a few such classes in Molecule. We just care that it's one of them.

    Attributes:
        _config: A Config instance.
    """

    _config: Config


class MoleculeConsoleHandler(logging.Handler):
    """Custom logging handler that uses ANSI color codes directly.

    Provides colored output without depending on RichHandler or competing formatters.
    """

    def __init__(
        self,
        *,
        show_time: bool = False,
        show_path: bool = False,
    ) -> None:
        """Initialize the console handler.

        Args:
            show_time: Whether to show timestamps.
            show_path: Whether to show file paths.
        """
        super().__init__()
        self.show_time = show_time
        self.show_path = show_path
        self.ansi_output = AnsiOutput()

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record with scenario context using original stderr.

        All messages go to the original stderr, bypassing Rich's redirection entirely.
        Also updates the log record with a plain text version for caplog compatibility.

        Args:
            record: The logging record to emit.
        """
        try:
            # Format the message
            message = self.format(record)

            # Check if this message has scenario context passed from ScenarioLoggerAdapter
            scenario_name = getattr(record, "molecule_scenario", None)
            step_name = getattr(record, "molecule_step", None)

            # Get both colored and plain versions using dual methods
            # cspell:ignore levelname
            colored_level, plain_level = self.ansi_output.format_log_level(record.levelname)

            # Process message once for each version
            colored_message = self.ansi_output.process_markup(message)
            plain_message = self.ansi_output.strip_markup(message)

            if scenario_name:
                colored_scenario, plain_scenario = self.ansi_output.format_scenario(
                    scenario_name,
                    step_name,
                )

                # Create colored output for display
                colored_output = f"{colored_level} {colored_scenario} {colored_message}"

                # Create plain output for caplog
                plain_output = f"{plain_level} {plain_scenario} {plain_message}"
            else:
                # Create colored output for display
                colored_output = f"{colored_level} {colored_message}"

                # Create plain output for caplog
                plain_output = f"{plain_level} {plain_message}"

            # Update the log record with the plain version for caplog and other handlers
            record.msg = plain_output
            record.args = ()

            # Write colored output to stderr for users
            original_stderr.write(colored_output + "\n")
            original_stderr.flush()

        except Exception:  # noqa: BLE001
            self.handleError(record)

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record message.

        Args:
            record: The logging record to format.

        Returns:
            The formatted message string.
        """
        # Use the default formatter if one is set
        if self.formatter:
            return self.formatter.format(record)

        # Simple default formatting
        return record.getMessage()


def configure() -> None:
    """Configure a molecule root logger.

    All other loggers will inherit the configuration we set here.
    """
    # Keep using root logger because we do want to process messages from other
    # libraries.
    logger = logging.getLogger()

    # Avoid adding duplicate MoleculeConsoleHandlers
    if not any(isinstance(h, MoleculeConsoleHandler) for h in logger.handlers):
        # Use our custom ANSI color handler instead of RichHandler
        handler = MoleculeConsoleHandler(
            show_time=False,
            show_path=False,
        )

        # Set a minimal formatter since we handle styling in the handler
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)

        # Insert at index 0 for priority - ensures our handler processes first
        logger.handlers.insert(0, handler)

    logger.propagate = False
    logger.setLevel(logging.INFO)


def set_log_level(log_level: int, debug: bool) -> None:  # noqa: FBT001
    """Set logging level.

    Args:
        log_level: verbosity control (0 - INFO, 1 - DEBUG)
        debug: debug mode indicator
    """
    # If we get verbosity level > 1, we just use debug because this is the
    # most detailed log level we have.
    if debug:
        log_level = 1  # DEBUG from the LOG_LEVEL_LUT
    logging.getLogger("molecule").setLevel(LOG_LEVEL_LUT.get(log_level, logging.DEBUG))


def get_logger(name: str) -> logging.Logger:
    """Return a child logger.

    Returned logger inherits configuration from the molecule logger.

    Args:
        name: Name of the child logger.

    Returns:
        A child logger of molecule.
    """
    return logging.getLogger("molecule." + name)


class ScenarioLoggerAdapter(logging.LoggerAdapter):  # type: ignore[type-arg]
    """Logger adapter that automatically includes scenario context in messages.

    This adapter includes scenario names and optional step information in log messages
    to provide better context when multiple scenarios are running or being processed.
    """

    def process(
        self,
        msg: object,
        kwargs: MutableMapping[str, object],
    ) -> tuple[object, MutableMapping[str, object]]:
        """Process the logging record.

        Args:
            msg: The log message.
            kwargs: Additional keyword arguments.

        Returns:
            A tuple of (processed_message, kwargs).
        """
        scenario_name = self.extra.get("scenario_name", "unknown") if self.extra else "unknown"
        step_name = self.extra.get("step_name") if self.extra else None

        # Pass scenario and step information through kwargs
        # Create new extra dict or copy existing one to avoid modifying the original
        current_extra = kwargs.get("extra", {})
        new_extra = dict(current_extra) if isinstance(current_extra, dict) else {}
        new_extra["molecule_scenario"] = scenario_name
        if step_name:
            new_extra["molecule_step"] = step_name
        kwargs["extra"] = new_extra
        return msg, kwargs


def get_scenario_logger(
    name: str,
    scenario_name: str,
    step_name: str,
) -> ScenarioLoggerAdapter:
    """Return a scenario-aware logger that includes scenario name in all messages.

    Args:
        name: Name of the child logger.
        scenario_name: Name of the scenario for context.
        step_name: Step name (e.g., 'converge', 'create', 'destroy').

    Returns:
        A ScenarioLoggerAdapter that includes scenario context in all messages.
    """
    logger = get_logger(name)
    extra = {"scenario_name": scenario_name, "step_name": step_name}
    return ScenarioLoggerAdapter(logger, extra)


def github_actions_groups(func: Callable[P, R]) -> Callable[P, R]:
    """Print group indicators before/after execution of a method.

    Args:
        func: The function to wrap.

    Returns:
        The wrapped function.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        self = cast("HasConfig", args[0])
        scenario = self._config.scenario.name
        subcommand = underscore(self.__class__.__name__)
        console.print(
            "::group::",
            f"[ci_info]Molecule[/] [scenario]{scenario}[/] > [action]{subcommand}[/]",
            sep="",
            markup=True,
            emoji=False,
            highlight=False,
        )
        try:
            return func(*args, **kwargs)
        finally:
            console.print("::endgroup::", markup=True, emoji=False, highlight=False)

    return wrapper


def gitlab_ci_sections(func: Callable[P, R]) -> Callable[P, R]:
    """Print group indicators before/after execution of a method.

    Args:
        func: The function to wrap.

    Returns:
        The wrapped function.
    """
    # GitLab requires:
    #  - \r (carriage return)
    #  - \e[0K (clear line ANSI escape code. We use \033 for the \e escape char)
    clear_line = "\r\033[0K"

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        self = cast("HasConfig", args[0])
        scenario = self._config.scenario.name
        subcommand = underscore(self.__class__.__name__)
        console.print(
            f"section_start:{int(time.time())}:{scenario}.{subcommand}",
            end=clear_line,
            markup=False,
            emoji=False,
            highlight=False,
        )
        console.print(
            # must be one color for the whole line or gitlab sets odd widths to each word.
            f"[ci_info]Molecule {scenario} > {subcommand}[/]",
            end="\n",
            markup=True,
            emoji=False,
            highlight=False,
        )
        try:
            return func(*args, **kwargs)
        finally:
            console.print(
                f"section_end:{int(time.time())}:{scenario}.{subcommand}",
                end=f"{clear_line}\n",
                markup=False,
                emoji=False,
                highlight=False,
            )

    return wrapper


def travis_ci_folds(func: Callable[P, R]) -> Callable[P, R]:
    """Print group indicators before/after execution of a method.

    Args:
        func: The function to wrap.

    Returns:
        The wrapped function.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        self = cast("HasConfig", args[0])
        scenario = self._config.scenario.name
        subcommand = underscore(self.__class__.__name__)
        console.print(
            f"travis_fold:start:{scenario}.{subcommand}",
            f"[ci_info]Molecule[/] [scenario]{scenario}[/] > [action]{subcommand}[/]",
            sep="",
            markup=True,
            emoji=False,
            highlight=False,
        )
        try:
            return func(*args, **kwargs)
        finally:
            console.print(
                f"travis_fold:end:{scenario}.{subcommand}",
                markup=False,
                emoji=False,
                highlight=False,
            )

    return wrapper


def section_logger(func: Callable[P, R]) -> Callable[P, R]:
    """Wrap effective execution of a method.

    Args:
        func: The function to wrap.

    Returns:
        The wrapped function.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        config_instance = args[0]
        if not hasattr(config_instance, "_config"):
            return func(*args, **kwargs)

        step_name = config_instance._config.action  # noqa: SLF001
        scenario_log = get_scenario_logger(
            __name__,
            config_instance._config.scenario.name,  # noqa: SLF001
            step_name,
        )

        scenario_log.info("[exec_executing]Executing[/]")

        try:
            rt = func(*args, **kwargs)

            state_info = config_instance._config.scenario.results.last_action_summary  # noqa: SLF001
            ansi_output = AnsiOutput()
            log = ansi_output.format_completion_message(state_info.message, state_info.color)
            if state_info.note:
                log += ansi_output.format_completion_note(state_info.note)
            getattr(scenario_log, state_info.log_level)(log)

        except Exception:
            failed_state = CompletionState.failed
            scenario_log.error(f"{failed_state.color}{failed_state.message}{A.RESET}")
            raise
        else:
            return rt

    return wrapper


@cache
def get_section_loggers() -> Iterable[Callable[[Callable[..., object]], Callable[..., object]]]:
    """Return a list of section wrappers to be added.

    Returns:
        A list of logging decorators.
    """
    default_section_loggers = [section_logger]
    if not os.getenv("CI"):
        return default_section_loggers
    if os.getenv("GITHUB_ACTIONS"):
        return [github_actions_groups, *default_section_loggers]
    if os.getenv("GITLAB_CI"):
        return [gitlab_ci_sections, *default_section_loggers]
    if os.getenv("TRAVIS"):
        return [travis_ci_folds, *default_section_loggers]
    # CI is set but no extra section_loggers apply.
    return default_section_loggers

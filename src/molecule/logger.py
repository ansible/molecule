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

import logging
import os
import time
from functools import wraps
from typing import Callable, Iterable

from ansible_compat.ports import cache
from enrich.logging import RichHandler

from molecule.console import console, console_stderr
from molecule.text import underscore

LOG = logging.getLogger(__name__)

LOG_LEVEL_LUT = {
    0: logging.INFO,
    1: logging.DEBUG,
}


def configure() -> None:
    """
    Configure a molecule root logger.

    All other loggers will inherit the configuration we set here.
    """
    # Keep using root logger because we do want to process messages from other
    # libraries.
    logger = logging.getLogger()
    handler = RichHandler(
        console=console_stderr, show_time=False, show_path=False, markup=True
    )  # type: ignore
    logger.addHandler(handler)
    logger.propagate = False
    logger.setLevel(logging.INFO)


def set_log_level(log_level: int, debug: bool) -> None:
    """
    Set logging level.

    :param log_level: verbosity control (0 - INFO, 1 - DEBUG)
    :param debug: debug mode indicator
    """
    # If we get verbosity level > 1, we just use debug because this is the
    # most detailed log level we have.
    if debug:
        log_level = 1  # DEBUG from the LOG_LEVEL_LUT
    logging.getLogger("molecule").setLevel(LOG_LEVEL_LUT.get(log_level, logging.DEBUG))


def get_logger(name: str) -> logging.Logger:
    """
    Return a child logger.

    Returned logger inherits configuration from the molecule logger.
    """
    return logging.getLogger("molecule." + name)


def github_actions_groups(func: Callable) -> Callable:
    """Print group indicators before/after execution of a method."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
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


def gitlab_ci_sections(func: Callable) -> Callable:
    """Print group indicators before/after execution of a method."""
    # GitLab requires:
    #  - \r (carriage return)
    #  - \e[0K (clear line ANSI escape code. We use \033 for the \e escape char)
    clear_line = "\r\033[0K"

    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
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


def travis_ci_folds(func: Callable) -> Callable:
    """Print group indicators before/after execution of a method."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
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


def section_logger(func: Callable) -> Callable:
    """Wrap effective execution of a method."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        LOG.info(
            "[info]Running [scenario]%s[/] > [action]%s[/][/]",
            self._config.scenario.name,
            underscore(self.__class__.__name__),
            extra={"markup": True},
        )
        rt = func(*args, **kwargs)
        # section close code goes here
        return rt

    return wrapper


@cache
def get_section_loggers() -> Iterable[Callable]:
    """Return a list of section wrappers to be added."""
    default_section_loggers = [section_logger]
    if not os.getenv("CI"):
        return default_section_loggers
    elif os.getenv("GITHUB_ACTIONS"):
        return [github_actions_groups] + default_section_loggers
    elif os.getenv("GITLAB_CI"):
        return [gitlab_ci_sections] + default_section_loggers
    elif os.getenv("TRAVIS"):
        return [travis_ci_folds] + default_section_loggers
    # CI is set but no extra section_loggers apply.
    return default_section_loggers

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
import sys
from functools import lru_cache

from enrich.console import Console
from enrich.logging import RichHandler

from molecule.console import console, should_do_markup, theme
from molecule.text import chomp

SUCCESS = 100
OUT = 101


class LogFilter(logging.Filter):
    """A custom log filter which excludes log messages above the logged level."""

    def __init__(self, level):
        """Construct LogFilter."""
        self.__level = level

    def filter(self, logRecord):  # pragma: no cover
        # https://docs.python.org/3/library/logging.html#logrecord-attributes
        return logRecord.levelno <= self.__level


class CustomLogger(logging.getLoggerClass()):  # type: ignore  # see https://sam.hooke.me/note/2020/03/mypy-and-verbose-logging/
    """
    A custom logging class which adds additional methods to the logger.

    These methods serve as syntactic sugar for formatting log messages.
    """

    def __init__(self, name, level=logging.NOTSET):
        """Construct CustomLogger."""
        super(CustomLogger, self).__init__(name, level=level)
        logging.addLevelName(SUCCESS, "SUCCESS")
        logging.addLevelName(OUT, "OUT")

    def success(self, msg, *args, **kwargs):
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, msg, args, **kwargs)

    def out(self, msg, *args, **kwargs):
        msg = chomp(msg)
        if self.isEnabledFor(OUT):
            console.print(msg, args, **kwargs)


class TrailingNewlineFormatter(logging.Formatter):
    """A custom logging formatter which removes additional newlines from messages."""

    def format(self, record):
        if record.msg:
            record.msg = record.msg.rstrip()
        return super(TrailingNewlineFormatter, self).format(record)


@lru_cache()
def get_logger(name=None) -> logging.Logger:
    """
    Build a logger with the given name and returns the logger.

    :param name: The name for the logger. This is usually the module
                 name, ``__name__``.
    :return: logger object
    """
    logging.setLoggerClass(CustomLogger)

    logger = logging.getLogger(name)  # type: logging.Logger
    logger.setLevel(logging.DEBUG)

    handler = RichHandler(
        console=LOGGING_CONSOLE, show_time=False, show_path=False, markup=True
    )  # type: ignore
    logger.addHandler(handler)
    logger.propagate = False

    return logger


LOGGING_CONSOLE = Console(
    file=sys.stderr, force_terminal=should_do_markup(), theme=theme
)

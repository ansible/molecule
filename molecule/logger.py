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
import sys

import colorama
from ansible.module_utils.parsing.convert_bool import boolean as to_bool


def should_do_markup() -> bool:
    """Decide about use of ANSI colors."""
    py_colors = os.environ.get("PY_COLORS", None)
    if py_colors is not None:
        return to_bool(py_colors, strict=False)

    return sys.stdout.isatty() and os.environ.get("TERM") != "dumb"


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
        super(logging.getLoggerClass(), self).__init__(name, level)
        logging.addLevelName(SUCCESS, "SUCCESS")
        logging.addLevelName(OUT, "OUT")

    def success(self, msg, *args, **kwargs):
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, msg, args, **kwargs)

    def out(self, msg, *args, **kwargs):
        if self.isEnabledFor(OUT):
            self._log(OUT, msg, args, **kwargs)


class TrailingNewlineFormatter(logging.Formatter):
    """A custom logging formatter which removes additional newlines from messages."""

    def format(self, record):
        if record.msg:
            record.msg = record.msg.rstrip()
        return super(TrailingNewlineFormatter, self).format(record)


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

    logger.addHandler(_get_info_handler())
    logger.addHandler(_get_out_handler())
    logger.addHandler(_get_warn_handler())
    logger.addHandler(_get_error_handler())
    logger.addHandler(_get_critical_handler())
    logger.addHandler(_get_success_handler())
    logger.propagate = False

    return logger


def _get_info_handler() -> logging.StreamHandler:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.addFilter(LogFilter(logging.INFO))  # type: ignore
    handler.setFormatter(
        TrailingNewlineFormatter("--> {}".format(cyan_text("%(message)s")))
    )

    return handler


def _get_out_handler() -> logging.StreamHandler:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(OUT)
    handler.addFilter(LogFilter(OUT))  # type: ignore
    handler.setFormatter(TrailingNewlineFormatter("    %(message)s"))

    return handler


def _get_warn_handler() -> logging.StreamHandler:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.WARN)
    handler.addFilter(LogFilter(logging.WARN))  # type: ignore
    handler.setFormatter(TrailingNewlineFormatter(yellow_text("%(message)s")))

    return handler


def _get_error_handler() -> logging.StreamHandler:
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.ERROR)
    handler.addFilter(LogFilter(logging.ERROR))  # type: ignore
    handler.setFormatter(TrailingNewlineFormatter(red_text("%(message)s")))

    return handler


def _get_critical_handler() -> logging.StreamHandler:
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.CRITICAL)
    handler.addFilter(LogFilter(logging.CRITICAL))  # type: ignore
    handler.setFormatter(TrailingNewlineFormatter(red_text("ERROR: %(message)s")))

    return handler


def _get_success_handler() -> logging.StreamHandler:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(SUCCESS)
    handler.addFilter(LogFilter(SUCCESS))  # type: ignore
    handler.setFormatter(TrailingNewlineFormatter(green_text("%(message)s")))

    return handler


def red_text(msg) -> str:
    """Add red markers."""
    return color_text(colorama.Fore.RED, msg)


def yellow_text(msg) -> str:
    """Add yellow markers."""
    return color_text(colorama.Fore.YELLOW, msg)


def green_text(msg) -> str:
    """Add green markers."""
    return color_text(colorama.Fore.GREEN, msg)


def cyan_text(msg) -> str:
    """Add cyan markers."""
    return color_text(colorama.Fore.CYAN, msg)


def color_text(color, msg) -> str:
    """Add color markers."""
    if should_do_markup():
        return "{}{}{}".format(color, msg, colorama.Style.RESET_ALL)
    return msg

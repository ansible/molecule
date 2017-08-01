#  Copyright (c) 2015-2017 Cisco Systems, Inc.
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

import logging
import sys

import colorama

colorama.init(autoreset=True)

SUCCESS = 100
OUT = 101


class LogFilter(object):
    """
    A custom log filter which excludes log messages above the logged
    level.
    """

    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):  # pragma: no cover
        # https://docs.python.org/3/library/logging.html#logrecord-attributes
        return logRecord.levelno <= self.__level


class CustomLogger(logging.getLoggerClass()):
    """
    A custom logging class which adds additional methods to the logger.  These
    methods serve as syntactic sugar for formatting log messages.
    """

    def __init__(self, name, level=logging.NOTSET):
        super(logging.getLoggerClass(), self).__init__(name, level)
        logging.addLevelName(SUCCESS, 'SUCCESS')
        logging.addLevelName(OUT, 'OUT')

    def success(self, msg, *args, **kwargs):
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, msg, args, **kwargs)

    def out(self, msg, *args, **kwargs):
        if self.isEnabledFor(OUT):
            self._log(OUT, msg, args, **kwargs)


class TrailingNewlineFormatter(logging.Formatter):
    """
    A custom logging formatter which removes additional newlines from messages.
    """

    def format(self, record):
        if record.msg:
            record.msg = record.msg.rstrip()
        return super(TrailingNewlineFormatter, self).format(record)


def get_logger(name=None):
    """
    Build a logger with the given name and returns the logger.

    :param name: The name for the logger. This is usually the module
                 name, ``__name__``.
    :return: logger object
    """
    logging.setLoggerClass(CustomLogger)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    logger.addHandler(_get_info_handler())
    logger.addHandler(_get_out_handler())
    logger.addHandler(_get_warn_handler())
    logger.addHandler(_get_error_handler())
    logger.addHandler(_get_critical_handler())
    logger.addHandler(_get_success_handler())
    logger.propagate = False

    return logger


def _get_info_handler():
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.addFilter(LogFilter(logging.INFO))
    handler.setFormatter(
        TrailingNewlineFormatter('--> {}'.format(cyan_text('%(message)s'))))

    return handler


def _get_out_handler():
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(OUT)
    handler.addFilter(LogFilter(OUT))
    handler.setFormatter(TrailingNewlineFormatter('    %(message)s'))

    return handler


def _get_warn_handler():
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.WARN)
    handler.addFilter(LogFilter(logging.WARN))
    handler.setFormatter(TrailingNewlineFormatter(yellow_text('%(message)s')))

    return handler


def _get_error_handler():
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.ERROR)
    handler.addFilter(LogFilter(logging.ERROR))
    handler.setFormatter(TrailingNewlineFormatter(red_text('%(message)s')))

    return handler


def _get_critical_handler():
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.CRITICAL)
    handler.addFilter(LogFilter(logging.CRITICAL))
    handler.setFormatter(
        TrailingNewlineFormatter(red_text('ERROR: %(message)s')))

    return handler


def _get_success_handler():
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(SUCCESS)
    handler.addFilter(LogFilter(SUCCESS))
    handler.setFormatter(TrailingNewlineFormatter(green_text('%(message)s')))

    return handler


def red_text(msg):
    return color_text(colorama.Fore.RED, msg)


def yellow_text(msg):
    return color_text(colorama.Fore.YELLOW, msg)


def green_text(msg):
    return color_text(colorama.Fore.GREEN, msg)


def cyan_text(msg):
    return color_text(colorama.Fore.CYAN, msg)


def color_text(color, msg):
    return '{}{}{}'.format(color, msg, colorama.Style.RESET_ALL)

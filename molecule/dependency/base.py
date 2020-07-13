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
"""Base Dependency Module."""

import abc
import time

import sh

from molecule import util
from molecule.logger import get_logger

LOG = get_logger(__name__)


class Base(object):
    """Dependency Base Class."""

    __metaclass__ = abc.ABCMeta

    RETRY = 3
    SLEEP = 3
    BACKOFF = 3

    def __init__(self, config):
        """
        Initialize code for all :ref:`Dependency` classes.

        :param config: An instance of a Molecule config.
        :returns: None
        """
        self._config = config

    def execute_with_retries(self):
        """Run dependency downloads with retry and timed back-off."""
        exception = None

        try:
            util.run_command(self._sh_command, debug=self._config.debug)
            msg = "Dependency completed successfully."
            LOG.success(msg)
            return
        except sh.ErrorReturnCode:
            pass

        for counter in range(1, (self.RETRY + 1)):
            msg = "Retrying dependency ... {}/{} time(s)".format(counter, self.RETRY)
            LOG.warning(msg)

            msg = "Sleeping {} seconds before retrying ...".format(self.SLEEP)
            LOG.warning(msg)
            time.sleep(self.SLEEP)
            self.SLEEP += self.BACKOFF

            try:
                util.run_command(self._sh_command, debug=self._config.debug)
                msg = "Dependency completed successfully."
                LOG.success(msg)
                return
            except sh.ErrorReturnCode as _exception:
                exception = _exception

        util.sysexit(exception.exit_code)

    @abc.abstractmethod
    def execute(self):  # pragma: no cover
        """
        Execute ``cmd`` and returns None.

        :return: None
        """
        pass

    @abc.abstractproperty
    def default_options(self):  # pragma: no cover
        """
        Get default CLI arguments provided to ``cmd`` as a dict.

        :return: dict
        """
        pass

    @abc.abstractproperty
    def default_env(self):  # pragma: no cover
        """
        Get default env variables provided to ``cmd`` as a dict.

        :return: dict
        """
        pass

    @property
    def name(self):
        """
        Name of the dependency and returns a string.

        :returns: str
        """
        return self._config.config["dependency"]["name"]

    @property
    def enabled(self):
        return self._config.config["dependency"]["enabled"]

    @property
    def options(self):
        return util.merge_dicts(
            self.default_options, self._config.config["dependency"]["options"]
        )

    @property
    def env(self):
        return util.merge_dicts(
            self.default_env, self._config.config["dependency"]["env"]
        )

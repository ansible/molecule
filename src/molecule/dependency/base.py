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
import logging
import os
import time
from subprocess import CalledProcessError

from molecule import util

LOG = logging.getLogger(__name__)


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
            # print(555, self._sh_command)
            util.run_command(self._sh_command, debug=self._config.debug, check=True)
            msg = "Dependency completed successfully."
            LOG.info(msg)
            return
        except CalledProcessError:
            pass

        for counter in range(1, (self.RETRY + 1)):
            msg = f"Retrying dependency ... {counter:d}/{self.RETRY:d} time(s)"
            LOG.warning(msg)

            msg = f"Sleeping for {self.SLEEP:d} seconds before retrying ..."
            LOG.warning(msg)
            time.sleep(self.SLEEP)
            self.SLEEP += self.BACKOFF

            try:
                util.run_command(self._sh_command, debug=self._config.debug, check=True)
                msg = "Dependency completed successfully."
                LOG.info(msg)
                return
            except CalledProcessError as _exception:
                exception = _exception

        LOG.error(str(exception))
        util.sysexit(exception.returncode)

    @abc.abstractmethod
    def execute(self, action_args=None):  # pragma: no cover
        """
        Execute ``cmd`` and returns None.

        :return: None
        """
        for name, version in self._config.driver.required_collections.items():
            self._config.runtime.require_collection(name, version)

    @property
    @abc.abstractmethod
    def default_options(self):  # pragma: no cover
        """
        Get default CLI arguments provided to ``cmd`` as a dict.

        :return: dict
        """

    @property
    def default_env(self):  # pragma: no cover
        """
        Get default env variables provided to ``cmd`` as a dict.

        :return: dict
        """
        env = util.merge_dicts(os.environ, self._config.env)
        return env

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

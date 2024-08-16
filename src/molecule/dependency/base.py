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
from __future__ import annotations

import abc
import logging
import os
import time

from subprocess import CalledProcessError

from molecule import util


LOG = logging.getLogger(__name__)


class Base:
    """Dependency Base Class.

    Attributes:
        RETRY: Number of times to retry the dependency.
        SLEEP: Number of seconds to sleep between retries.
        BACKOFF: Additional number of seconds to sleep for each successive attempt.
    """

    __metaclass__ = abc.ABCMeta

    RETRY = 3
    SLEEP = 3
    BACKOFF = 3

    def __init__(self, config) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN001
        """Initialize code for all :ref:`Dependency` classes.

        Args:
            config: An instance of a Molecule config.
        """
        self._config = config
        self._sh_command: list[str] | None = None

    def execute_with_retries(self):  # type: ignore[no-untyped-def]  # noqa: ANN201
        """Run dependency downloads with retry and timed back-off."""
        exception = None

        try:
            util.run_command(self._sh_command, debug=self._config.debug, check=True)  # type: ignore[arg-type]
            msg = "Dependency completed successfully."
            LOG.info(msg)
            return  # noqa: TRY300
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
                util.run_command(self._sh_command, debug=self._config.debug, check=True)  # type: ignore[arg-type]
                msg = "Dependency completed successfully."
                LOG.info(msg)
                return  # noqa: TRY300
            except CalledProcessError as _exception:
                exception = _exception

        LOG.error(str(exception))
        util.sysexit(exception.returncode)  # type: ignore[union-attr]

    @abc.abstractmethod
    def execute(self, action_args=None):  # type: ignore[no-untyped-def] # pragma: no cover  # noqa: ANN001, ANN201
        """Execute ``cmd`` and returns None."""
        for name, version in self._config.driver.required_collections.items():
            self._config.runtime.require_collection(name, version)

    @property
    @abc.abstractmethod
    def default_options(self):  # type: ignore[no-untyped-def] # pragma: no cover  # noqa: ANN201
        """Get default CLI arguments provided to ``cmd`` as a dict.

        Returns:
            dict
        """

    @property
    def default_env(self):  # type: ignore[no-untyped-def] # pragma: no cover  # noqa: ANN201
        """Get default env variables provided to ``cmd`` as a dict.

        Returns:
            dict
        """
        env = util.merge_dicts(os.environ, self._config.env)
        return env  # noqa: RET504

    @property
    def name(self):  # type: ignore[no-untyped-def]  # noqa: ANN201
        """Name of the dependency and returns a string.

        :returns: str
        """
        return self._config.config["dependency"]["name"]

    @property
    def enabled(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self._config.config["dependency"]["enabled"]

    @property
    def options(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return util.merge_dicts(
            self.default_options,
            self._config.config["dependency"]["options"],
        )

    @property
    def env(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return util.merge_dicts(
            self.default_env,
            self._config.config["dependency"]["env"],
        )

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
"""Verifier Base Module."""
from __future__ import annotations

import abc
import os

from molecule import util


class Verifier:
    """Verifier Base Class."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, config=None) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN001
        """Initialize code for all :ref:`Verifier` classes.

        Args:
            config: An instance of a Molecule config.
        """
        self._config = config

    @property
    @abc.abstractmethod
    def name(self):  # type: ignore[no-untyped-def] # pragma: no cover  # noqa: ANN201
        """Name of the verifier and returns a string.

        :returns: str
        """

    @property
    @abc.abstractmethod
    def default_options(self):  # type: ignore[no-untyped-def] # pragma: no cover  # noqa: ANN201
        """Get default CLI arguments provided to ``cmd`` as a dict.

        Return:
            dict
        """

    @property
    @abc.abstractmethod
    def default_env(self):  # type: ignore[no-untyped-def] # pragma: no cover  # noqa: ANN201
        """Get default env variables provided to ``cmd`` as a dict.

        Return:
            dict
        """

    @abc.abstractmethod
    def execute(self, action_args=None):  # type: ignore[no-untyped-def] # pragma: no cover  # noqa: ANN001, ANN201
        """Execute ``cmd`` and returns None."""

    @abc.abstractmethod
    def schema(self):  # type: ignore[no-untyped-def] # pragma: no cover  # noqa: ANN201
        """Return validation schema."""

    @property
    def enabled(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return self._config.config["verifier"]["enabled"]

    @property
    def directory(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return os.path.join(  # noqa: PTH118
            self._config.scenario.directory,
            self._config.config["verifier"].get("directory", "tests"),
        )

    @property
    def options(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return util.merge_dicts(
            self.default_options,
            self._config.config["verifier"]["options"],
        )

    @property
    def env(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return util.merge_dicts(
            self.default_env,
            self._config.config["verifier"]["env"],
        )

    def __eq__(self, other):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN204
        """Implement equality comparison."""
        return str(self) == str(other)

    def __lt__(self, other):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN204
        """Implement lower than comparison."""
        return str.__lt__(str(self), str(other))

    def __hash__(self):  # type: ignore[no-untyped-def]  # noqa: ANN204
        """Implement hashing."""
        return self.name.__hash__()

    def __str__(self) -> str:
        """Return readable string representation of object."""
        return self.name  # type: ignore[no-any-return]

    def __repr__(self) -> str:
        """Return detailed string representation of object."""
        return self.name  # type: ignore[no-any-return]

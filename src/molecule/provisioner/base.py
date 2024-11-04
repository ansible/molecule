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
"""Provisioner Base Module."""
from __future__ import annotations

import abc

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from molecule.config import Config


class Base(abc.ABC):
    """Provisioner Base Class."""

    def __init__(self, config: Config) -> None:
        """Initialize code for all :ref:`Provisioner` classes.

        Args:
            config: An instance of a Molecule config.
        """
        self._config = config

    @property
    @abc.abstractmethod
    def default_options(self) -> dict[str, str | bool]:  # pragma: no cover
        """Get default CLI arguments provided to ``cmd``.

        Returns:
            The default CLI arguments.
        """

    @property
    @abc.abstractmethod
    def default_env(self) -> dict[str, str]:  # pragma: no cover
        """Get default env variables provided to ``cmd``.

        Returns:
            The default env variables.
        """

    @property
    @abc.abstractmethod
    def name(self) -> str:  # pragma: no cover
        """Name of the provisioner.

        Returns:
            The provisioner's name.
        """

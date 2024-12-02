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

from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

from molecule import util


if TYPE_CHECKING:
    from collections.abc import MutableMapping

    from molecule.config import Config


class VerifierSchemaName(TypedDict):
    """Verifier schema name definition.

    Attributes:
        type: schema type.
        allowed: list of allowed verifier names.
    """

    type: str
    allowed: list[str]


class VerifierSchema(TypedDict):
    """Verifier schema.

    Attributes:
        name: Schema name container.
    """

    name: VerifierSchemaName


class VerifierDef(TypedDict):
    """Verifier schema container.

    Attributes:
        type: Schema type.
        schema: Schema container.
    """

    type: str
    schema: VerifierSchema


class Schema(TypedDict):
    """Verifier schema definition.

    Attributes:
        verifier: Verifier schema container.
    """

    verifier: VerifierDef


class Verifier(abc.ABC):
    """Verifier Base Class."""

    def __init__(self, config: Config) -> None:
        """Initialize code for all :ref:`Verifier` classes.

        Args:
            config: An instance of a Molecule config.
        """
        self._config = config

    @property
    @abc.abstractmethod
    def name(self) -> str:  # pragma: no cover
        """Name of the verifier.

        Returns:
            The name of the verifier.
        """

    @property
    @abc.abstractmethod
    def default_options(self) -> MutableMapping[str, str | bool]:  # pragma: no cover
        """Get default CLI arguments provided to ``cmd``.

        Returns:
            The default verifier options.
        """

    @property
    @abc.abstractmethod
    def default_env(self) -> dict[str, str]:  # pragma: no cover
        """Get default env variables provided to ``cmd``.

        Returns:
            The default verifier environment variables.
        """

    @abc.abstractmethod
    def execute(self, action_args: list[str] | None = None) -> None:  # pragma: no cover
        """Execute ``cmd``.

        Args:
            action_args: list of arguments to be passed.
        """

    @abc.abstractmethod
    def schema(self) -> Schema:  # pragma: no cover
        """Return validation schema.

        Returns:
            Verifier schema.
        """

    @property
    def enabled(self) -> bool:
        """Is the verifier enabled.

        Returns:
            Whether the verifier is enabled.
        """
        return self._config.config["verifier"]["enabled"]

    @property
    def directory(self) -> str:
        """Verifier directory.

        Returns:
            The directory of the the verifier files.
        """
        return str(
            Path(
                self._config.scenario.directory,
                self._config.config["verifier"].get("directory", "tests"),
            ),
        )

    @property
    def options(self) -> MutableMapping[str, str | bool]:
        """The computed options for this verifier.

        Returns:
            The combined dictionary of default options and those specified in the config.
        """
        return util.merge_dicts(
            self.default_options,
            self._config.config["verifier"]["options"],
        )

    @property
    def env(self) -> dict[str, str]:
        """The computed environment variables for this verifier.

        Returns:
            The combined dictionary of default environment variables and those
            specified in the config.
        """
        return util.merge_dicts(
            self.default_env,
            self._config.config["verifier"]["env"],
        )

    def __eq__(self, other: object) -> bool:
        """Implement equality comparison.

        Args:
            other: object to compare against this one.

        Returns:
            Whether other matches the name of this verifier.
        """
        return str(self) == str(other)

    def __lt__(self, other: object) -> bool:
        """Implement lower than comparison.

        Args:
            other: object to compare against this one.

        Returns:
            Whether other is less than the name of this verifier.
        """
        return str.__lt__(str(self), str(other))

    def __hash__(self) -> int:
        """Implement hashing.

        Returns:
            The hash of the verifier's name.
        """
        return self.name.__hash__()

    def __str__(self) -> str:
        """Return readable string representation of object.

        Returns:
            The verifier's name.
        """
        return self.name

    def __repr__(self) -> str:
        """Return detailed string representation of object.

        Returns:
            The verifier's name.
        """
        return self.name

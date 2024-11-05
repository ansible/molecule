# Copyright 2015 Docker, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# Taken from Docker Compose:
# https://github.com/docker/compose/blob/master/compose/config/interpolation.py
"""Interpolation Module."""
from __future__ import annotations

import string

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Mapping, MutableMapping
    from re import Match


class InvalidInterpolation(Exception):  # noqa: N818
    """InvalidInterpolation Exception."""

    def __init__(
        self,
        string: str,  # pylint: disable=redefined-outer-name
        place: Exception,
    ) -> None:
        """Construct InvalidInterpolation.

        Args:
            string: Error message.
            place: The original exception with location information.
        """
        self.string = string
        self.place = place


class Interpolator:
    """Configuration options may contain environment variables.

    For example, suppose the shell contains ``VERIFIER_NAME=testinfra`` and
    the following molecule.yml is supplied.

    ```yaml
        verifier:
          - name: ${VERIFIER_NAME}
    ```

    Molecule will substitute ``$VERIFIER_NAME`` with the value of the
    ``VERIFIER_NAME`` environment variable.

    !!! warning

        If an environment variable is not set, Molecule substitutes with an
        empty string.

    Both ``$VARIABLE`` and ``${VARIABLE}`` syntax are supported. Extended
    shell-style features, such as ``${VARIABLE-default}`` and
    ``${VARIABLE:-default}`` are also supported. Even the default as another
    environment variable is supported like ``${VARIABLE-$DEFAULT}`` or
    ``${VARIABLE:-$DEFAULT}``. An empty string is returned when
    both variables are undefined.

    If a literal dollar sign is needed in a configuration, use a double dollar
    sign (`$$`).

    Molecule will substitute special ``MOLECULE_`` environment variables
    defined in `molecule.yml`.

    !!! note

        Remember, the ``MOLECULE_`` namespace is reserved for Molecule.  Do not
        prefix your own variables with `MOLECULE_`.

    A file may be placed in the root of the project as `.env.yml`, and Molecule
    will read variables when rendering `molecule.yml`.  See command usage.
    """

    def __init__(
        self,
        templater: type[TemplateWithDefaults],
        mapping: MutableMapping[str, str],
    ) -> None:
        """Construct Interpolator.

        Args:
            templater: A templater class.
            mapping: A mapping object.
        """
        self.templater = templater
        self.mapping = mapping

    def interpolate(
        self,
        string: str,  # pylint: disable=redefined-outer-name
        keep_string: str | None = None,
    ) -> str:
        """Template string with this Interpolator's mapping.

        Args:
            string: The string to modify.
            keep_string: A substring to keep intact, regardless of mapping.

        Returns:
            The modified string.

        Raises:
            InvalidInterpolation: When the interpolation fails.
        """
        try:
            return self.templater(string).substitute(self.mapping, keep_string)
        except ValueError as e:
            raise InvalidInterpolation(string, e) from e


class TemplateWithDefaults(string.Template):
    """TemplateWithDefaults Class.

    Attributes:
        idpattern: Replacement pattern for base Template class.
    """

    idpattern = r"[_a-z][_a-z0-9]*(?::?-[^}]+)?"

    # pylint: disable=too-many-return-statements  # pylint: disable=useless-suppression
    def substitute(  # type: ignore[override]  # pylint: disable=arguments-differ
        self,
        mapping: Mapping[str, str],
        keep_string: str | None,
    ) -> str:
        """Substitute substrings according to a mapping.

        Args:
            mapping: The mapping to apply to the string.
            keep_string: A substring to keep intact, regardless of mapping.

        Returns:
            The converted string.
        """

        # Helper function for .sub()
        def convert(mo: Match[str]) -> str | None:  # noqa: PLR0911
            # Check the most common path first.
            named = mo.group("named") or mo.group("braced")
            if named is not None:
                if keep_string and named.startswith(keep_string):
                    return f"${named}"
                if ":-" in named:
                    var, _, default = named.partition(":-")
                    # If default is also a variable
                    if default.startswith("$"):
                        default = mapping.get(default[1:], "")
                    return mapping.get(var) or default
                if "-" in named:
                    var, _, default = named.partition("-")
                    # If default is also a variable
                    if default.startswith("$"):
                        default = mapping.get(default[1:], "")
                    return mapping.get(var, default)
                val = mapping.get(named, "")
                return f"{val}"
            if mo.group("escaped") is not None:
                return self.delimiter
            if mo.group("invalid") is not None:
                self._invalid(mo)  # type: ignore[attr-defined]
                return None
            return None

        return self.pattern.sub(convert, self.template)  # type: ignore[arg-type]

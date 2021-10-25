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
"""Iterpolation Module."""

import string
from typing import MutableMapping, Type


class InvalidInterpolation(Exception):
    """InvalidInterpolation Exception."""

    def __init__(self, string: str, place: Exception):
        """Construct InvalidInterpolation."""
        self.string = string
        self.place = place


class Interpolator(object):
    """
    Configuration options may contain environment variables.

    For example, suppose the shell contains ``VERIFIER_NAME=testinfra`` and
    the following molecule.yml is supplied.

    .. code-block:: yaml

        verifier:
          - name: ${VERIFIER_NAME}

    Molecule will substitute ``$VERIFIER_NAME`` with the value of the
    ``VERIFIER_NAME`` environment variable.

    .. warning::

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

    .. important::

        Remember, the ``MOLECULE_`` namespace is reserved for Molecule.  Do not
        prefix your own variables with `MOLECULE_`.

    A file may be placed in the root of the project as `.env.yml`, and Molecule
    will read variables when rendering `molecule.yml`.  See command usage.
    """

    def __init__(
        self, templater: Type["TemplateWithDefaults"], mapping: MutableMapping
    ):
        """Construct Interpolator."""
        self.templater = templater
        self.mapping = mapping

    def interpolate(self, string: str, keep_string=None) -> str:
        try:
            return self.templater(string).substitute(self.mapping, keep_string)  # type: ignore
        except ValueError as e:
            raise InvalidInterpolation(string, e)


class TemplateWithDefaults(string.Template):
    """TemplateWithDefaults Class."""

    idpattern = r"[_a-z][_a-z0-9]*(?::?-[^}]+)?"

    # Modified from python2.7/string.py
    def substitute(self, mapping, keep_string):

        # Helper function for .sub()
        def convert(mo):
            # Check the most common path first.
            named = mo.group("named") or mo.group("braced")
            if named is not None:
                # TODO(retr0h): This needs to be better handled.
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
                self._invalid(mo)

        return self.pattern.sub(convert, self.template)

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

import abc
import os

import molecule
from molecule import util


class Verifier(object):
    """Verifier Base Class."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, config=None):
        """
        Initialize code for all :ref:`Verifier` classes.

        :param config: An instance of a Molecule config.
        :returns: None
        """
        self._config = config

    @abc.abstractproperty
    def name(self):  # pragma: no cover
        """
        Name of the verifier and returns a string.

        :returns: str
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

    @abc.abstractmethod
    def execute(self):  # pragma: no cover
        """
        Execute ``cmd`` and returns None.

        :return: None
        """
        pass

    @abc.abstractmethod
    def schema(self):  # pragma: no cover
        """
        Return validation schema.

        :return: None
        """
        pass

    @property
    def enabled(self):
        return self._config.config["verifier"]["enabled"]

    @property
    def directory(self):
        return os.path.join(
            self._config.scenario.directory,
            self._config.config["verifier"].get("directory", "tests"),
        )

    @property
    def options(self):
        return util.merge_dicts(
            self.default_options, self._config.config["verifier"]["options"]
        )

    @property
    def env(self):
        return util.merge_dicts(
            self.default_env, self._config.config["verifier"]["env"]
        )

    def __eq__(self, other):
        """Implement equality comparision."""
        return str(self) == str(other)

    def __lt__(self, other):
        """Implement lower than comparision."""
        return str.__lt__(str(self), str(other))

    def __hash__(self):
        """Implement hashing."""
        return self.name.__hash__()

    def __str__(self):
        """Return readable string representation of object."""
        return self.name

    def __repr__(self):
        """Return detailed string representation of object."""
        return self.name

    def template_dir(self):
        p = os.path.abspath(
            os.path.join(
                os.path.dirname(molecule.__file__),
                "cookiecutter",
                "scenario",
                "verifier",
                self.name,
            )
        )
        return p

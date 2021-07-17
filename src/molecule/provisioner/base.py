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

import abc


class Base(object):
    """Provisioner Base Class."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, config):
        """
        Initialize code for all :ref:`Provisioner` classes.

        :param config: An instance of a Molecule config.
        :returns: None
        """
        self._config = config

    @property
    @abc.abstractmethod
    def default_options(self):  # pragma: no cover
        """
        Get default CLI arguments provided to ``cmd`` as a dict.

        :return: dict
        """

    @property
    @abc.abstractmethod
    def default_env(self):  # pragma: no cover
        """
        Get default env variables provided to ``cmd`` as a dict.

        :return: dict
        """

    @property
    @abc.abstractmethod
    def name(self):  # pragma: no cover
        """
        Name of the provisioner and returns a string.

        :returns: str
        """

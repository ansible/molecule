#  Copyright (c) 2015-2017 Cisco Systems, Inc.
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

import abc


class Base(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, config):
        """
        Base initializer for all :ref:`Driver` classes.

        :param config: An instance of a Molecule config.
        :returns: None
        """
        self._config = config

    @abc.abstractproperty
    def testinfra_options(self):
        """
        Returns a Testinfra specific options dict.

        :returns: dict
        """
        pass  # pragma: no cover

    @abc.abstractproperty
    def connection_options(self):
        """
        Returns a driver specific connection options dict.

        :returns: str
        """
        pass  # pragma: no cover

    @abc.abstractproperty
    def login_cmd_template(self):
        """
        Returns the command string to login to a host.

        :returns: str
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def login_args(self, instance_name):
        """
        Returns the arguments used in the login command and returns a list.

        :param instance_name: A string containing the instance to login to.
        :returns: list
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def status(self):
        """
        Determine instances status and return a list.

        :returns: list
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def _delayed_import(self):
        """
        Delay driver module imports and return a module.  By delaying the
        import, Molecule can import all drivers in the config module, and only
        instantiate the configured one.  Otherwise, Molecule would require
        each driver's packages be installed.

        :returns: module
        """
        pass  # pragma: no cover

    @property
    def name(self):
        return self._config.config['driver']['name']

    @property
    def options(self):
        return self._config.config['driver']['options']

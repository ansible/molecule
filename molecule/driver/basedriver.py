#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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


class InvalidDriverSpecified(Exception):
    """
    Exception class raised when an invalid driver is specified.
    """
    pass


class InvalidProviderSpecified(Exception):
    """
    Exception class raised when an invalid provider is specified.
    """
    pass


class InvalidPlatformSpecified(Exception):
    """
    Exception class raised when an invalid platform is specified.
    """
    pass


class BaseDriver(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, molecule):
        """
        Base initializer for all :ref:`Driver` classes.

        :param molecule: An instance of molecule.
        :returns: None
        """
        self.molecule = molecule

    @abc.abstractproperty
    def name(self):
        """
        The name of the driver, returns a string.

        :returns: str
        """
        pass  # pragma: no cover

    @abc.abstractproperty
    def instances(self):
        """
        List of instance(s) owned by this driver.

        :returns: list
        """
        pass  # pragma: no cover

    @abc.abstractproperty
    def default_provider(self):
        """
        Defaut provider used to create instance(s) (e.g. virtualbox), and
        returns a string.

        :returns: str
        """
        pass  # pragma: no cover

    @abc.abstractproperty
    def default_platform(self):
        """
        Default platform used (e.g. RHEL) and returns a string.

        :returns: str
        """
        pass  # pragma: no cover

    @abc.abstractproperty
    def provider(self):
        """
        Provider that is configured to be used and returns a string.

        :returns: str
        """
        pass  # pragma: no cover

    @abc.abstractproperty
    def platform(self):
        """
        Platform that is used for creating instance(s) and returns a string.

        :returns: str
        """
        pass  # pragma: no cover

    @platform.setter
    @abc.abstractproperty
    def platform(self, val):
        """
        Set the platform used for creating instance(s).

        :param val: A string providing the name of the platform.
        :returns: None
        """
        pass  # pragma: no cover

    @abc.abstractproperty
    def valid_providers(self):
        """
        List of valid providers supported by driver.

        :returns: list
        """
        pass  # pragma: no cover

    @abc.abstractproperty
    def valid_platforms(self):
        """
        List of valid platforms supported.

        :returns: list
        """
        pass  # pragma: no cover

    @abc.abstractproperty
    def ssh_config_file(self):
        """
        Returns the ssh config file location for the driver and returns
        a string.

        :returns: str
        """
        pass  # pragma: no cover

    @abc.abstractproperty
    def ansible_connection_params(self):
        """
        Returns the parameters used for connecting with ansible and returns a
        string.

        :returns: str
        """
        pass  # pragma: no cover

    @abc.abstractproperty
    def testinfra_args(self):
        """
        Returns the kwargs used when invoking the testinfra validator, and
        returns a dict.

        :returns: dict
        """
        pass  # pragma: no cover

    @abc.abstractproperty
    def serverspec_args(self):
        """
        Returns the kwargs used when invoking the serverspec validator, and
        returns a dict.

        :returns: dict
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def up(self, no_provision=True):
        """
        Starts the configured instance(s) within the driver.

        :param no_provision: An optional bool to determine if the driver's
         provisioner should be invoked.  Only used by :class:`.VagrantDriver`.
        :returns: None
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def destroy(self):
        """
        Destroys the instance(s).

        :returns: None
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def status(self):
        """
        List of instance(s) running status.

        :returns: list
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def conf(self, vm_name=None, ssh_config=False):
        """
        SSH config required for logging into a instance(s).

        :param vm_name:
        :param ssh_config:
        :returns: None

        .. warning:: The usage of this method seems inconsistent across
           each driver.
        .. todo:: The return value of this method is inconsistent across
                  drivers.
        .. todo:: The param `vm_name` is inconsistent across drivers.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def inventory_entry(self, instance):
        """
        Returns an inventory entry for the given instance and returns a
        string.

        :param instance: A dict containing a single element provided by
         :meth:`.instances`.

        :returns: str
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def login_cmd(self, instance_name):
        """
        Returns the command string to login to a host.

        :param instance_name:
        :returns:
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def login_args(self, instance_name):
        """
        Returns the arguments used in the login command.

        :param instance_name:
        :returns:

        .. warning:: The usage of this method seems inconsistent across
           each driver.
        .. todo:: The return value of this method is inconsistent across
                  drivers.
        """
        pass  # pragma: no cover

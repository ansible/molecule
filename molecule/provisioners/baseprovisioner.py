#  Copyright (c) 2015-2016 Cisco Systems
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
import abc


class InvalidProviderSpecified(Exception):
    pass


class InvalidPlatformSpecified(Exception):
    pass


class BaseProvisioner(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, molecule):
        self.m = molecule

    @abc.abstractproperty
    def name(self):
        """
        Getter for type of provisioner
        :return:
        """
        return

    @abc.abstractproperty
    def instances(self):
        """
        Provides the list of instances owned by this provisioner
        :return:
        """
        return

    @abc.abstractproperty
    def default_provider(self):
        """
        Defaut provider used to create VMs for e.g. virtualbox etc
        :return:
        """
        return

    @abc.abstractproperty
    def default_platform(self):
        """
        Default platform used for e.g. RHEL, trusty etc
        :return:
        """
        return

    @abc.abstractproperty
    def provider(self):
        """
        Provider that is configured to be used
        :return:
        """
        return

    @abc.abstractproperty
    def platform(self):
        """
        Platform that is used for creating VMs
        :return:
        """
        return

    @abc.abstractproperty
    def valid_providers(self):
        """
        List of valid providers supported by provisioner
        :return:
        """
        return

    @abc.abstractproperty
    def valid_platforms(self):
        """
        List of valid platforms supported
        :return:
        """
        return self._valid_platforms

    @abc.abstractproperty
    def ssh_config_file(self):
        """
        Returns the ssh config file location for the provisioner
        :return:
        """
        return

    @abc.abstractproperty
    def ansible_connection_params(self):
        """
        Returns the parameters used for connecting with ansible.
        :return:
        """

    @abc.abstractproperty
    def testinfra_args(self):
        """
        Returns the kwargs used when invoking the testinfra validator
        :return:
        """
        return

    @abc.abstractproperty
    def serverspec_args(self):
        """
        Returns the kwargs used when invoking the serverspec validator
        :return:
        """
        return

    @abc.abstractmethod
    def up(self, no_provision=True):
        """
        Starts the configured VMs in within the provisioner
        :param no_provision:
        :return:
        """
        return

    @abc.abstractmethod
    def destroy(self):
        """
        Destroys the VMs
        :return:
        """
        return

    @abc.abstractmethod
    def status(self):
        """
        Returns the running status of the VMs
        :return:
        """
        return

    @abc.abstractmethod
    def conf(self, vm_name=None, ssh_config=False):
        """
        SSH config required for logging into a VM
        :return:
        """
        return

    @abc.abstractmethod
    def inventory_entry(self, instance):
        """
        Returns an inventory entry with the given arguments
        :return:
        """
        return

    @abc.abstractmethod
    def login_cmd(self, instance_name):
        """
        Returns the command string to login to a host
        :return:
        """
        return

    @abc.abstractmethod
    def login_args(self, instance_name):
        """
        Returns the arguments used in the login command
        :return:
        """
        return

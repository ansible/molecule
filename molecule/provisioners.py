#  Copyright (c) 2015 Cisco Systems
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
import os

import vagrant

import utilities


class InvalidProviderSpecified(Exception):
    pass


class InvalidPlatformSpecified(Exception):
    pass


def get_provisioner(molecule):
    if 'vagrant' in molecule._config.config:
        return VagrantProvisioner(molecule)
    elif 'proxmox' in molecule._config.config:
        return ProxmoxProvisioner(molecule)
    else:
        return None


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

    @abc.abstractmethod
    def up(no_provision=True):
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


class VagrantProvisioner(BaseProvisioner):
    def __init__(self, molecule):
        super(VagrantProvisioner, self).__init__(molecule)
        self._vagrant = vagrant.Vagrant(quiet_stdout=False, quiet_stderr=False)
        self._provider = self._get_provider()
        self._platform = self._get_platform()
        molecule._env['VAGRANT_VAGRANTFILE'] = molecule._config.config['molecule']['vagrantfile_file']
        self._vagrant.env = molecule._env

    def _get_provider(self):
        if self.m._args.get('--provider'):
            if not [item
                    for item in self.m._config.config['vagrant']['providers']
                    if item['name'] == self.m._args['--provider']]:
                raise InvalidProviderSpecified()
            self.m._state['default_provider'] = self.m._args['--provider']
            self.m._env['VAGRANT_DEFAULT_PROVIDER'] = self.m._args['--provider']
        else:
            self.m._env['VAGRANT_DEFAULT_PROVIDER'] = self.default_provider

        return self.m._env['VAGRANT_DEFAULT_PROVIDER']

    def _get_platform(self):
        if self.m._args.get('--platform'):
            if not [item
                    for item in self.m._config.config['vagrant']['platforms']
                    if item['name'] == self.m._args['--platform']]:
                raise InvalidPlatformSpecified()
            self.m._state['default_platform'] = self.m._args['--platform']
            self.m._env['MOLECULE_PLATFORM'] = self.m._args['--platform']
        else:
            self.m._env['MOLECULE_PLATFORM'] = self.default_platform

        return self.m._env['MOLECULE_PLATFORM']

    def _write_vagrant_file(self):
        kwargs = {'config': self.m._config.config, 'current_platform': self.platform, 'current_provider': self.provider}

        template = self.m._config.config['molecule']['vagrantfile_template']
        dest = self.m._config.config['molecule']['vagrantfile_file']
        utilities.write_template(template, dest, kwargs=kwargs)

    @property
    def name(self):
        return 'vagrant'

    @property
    def instances(self):
        return self.m._config.config['vagrant']['instances']

    @property
    def default_provider(self):
        # assume static inventory if there's no vagrant section
        if self.m._config.config.get('vagrant') is None:
            return 'static'

        # assume static inventory if no providers are listed
        if self.m._config.config['vagrant'].get('providers') is None:
            return 'static'

        # take config's default_provider if specified, otherwise use the first in the provider list
        default_provider = self.m._config.config['molecule'].get('default_provider')
        if default_provider is None:
            default_provider = self.m._config.config['vagrant']['providers'][0]['name']

        # default to first entry if no entry for provider exists or provider is false
        if not self.m._state.get('default_provider'):
            return default_provider

        return self.m._state['default_provider']

    @property
    def default_platform(self):
        # assume static inventory if there's no vagrant section
        if self.m._config.config.get('vagrant') is None:
            return 'static'

        # assume static inventory if no platforms are listed
        if self.m._config.config['vagrant'].get('platforms') is None:
            return 'static'

        # take config's default_platform if specified, otherwise use the first in the platform list
        default_platform = self.m._config.config['molecule'].get('default_platform')
        if default_platform is None:
            default_platform = self.m._config.config['vagrant']['platforms'][0]['name']

        # default to first entry if no entry for platform exists or platform is false
        if not self.m._state.get('default_platform'):
            return default_platform

        return self.m._state['default_platform']

    @property
    def provider(self):
        return self._provider

    @property
    def platform(self):
        return self._platform

    @property
    def valid_providers(self):
        return self.m._config.config['vagrant']['providers']

    @property
    def valid_platforms(self):
        return self.m._config.config['vagrant']['platforms']

    @property
    def ssh_config_file(self):
        return '.vagrant/ssh-config'

    def up(self, no_provision=True):
        self._write_vagrant_file()
        self._vagrant.up(no_provision)

    def destroy(self):
        self._write_vagrant_file()
        if self.m._state.get('created'):
            self._vagrant.destroy()

        os.remove(self.m._config.config['molecule']['vagrantfile_file'])

    def status(self):
        return self._vagrant.status()

    def conf(self, vm_name=None, ssh_config=False):
        if ssh_config:
            return self._vagrant.ssh_config(vm_name=vm_name)
        else:
            return self._vagrant.conf(vm_name=vm_name)


# Place holder for Proxmox, partially implemented
class ProxmoxProvisioner(BaseProvisioner):
    def __init__(self):
        super(ProxmoxProvisioner, self).__init__()

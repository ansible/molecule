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

import os
import copy

import vagrant

from molecule import utilities
from molecule.provisioners import baseprovisioner


class VagrantProvisioner(baseprovisioner.BaseProvisioner):
    def __init__(self, molecule):
        super(VagrantProvisioner, self).__init__(molecule)
        self._vagrant = vagrant.Vagrant(quiet_stdout=False, quiet_stderr=False)
        self._provider = self._get_provider()
        self._platform = self._get_platform()
        molecule._env['VAGRANT_VAGRANTFILE'] = molecule._config.config[
            'molecule']['vagrantfile_file']
        self._vagrant.env = molecule._env
        self._updated_multiplatform = False

    def _get_provider(self):
        if self.m._args.get('--provider'):
            if not [item
                    for item in self.m._config.config['vagrant']['providers']
                    if item['name'] == self.m._args['--provider']]:
                raise baseprovisioner.InvalidProviderSpecified()
            self.m._state.change_state('default_provider',
                                       self.m._args['--provider'])
            self.m._env['VAGRANT_DEFAULT_PROVIDER'] = self.m._args[
                '--provider']
        else:
            self.m._env['VAGRANT_DEFAULT_PROVIDER'] = self.default_provider

        return self.m._env['VAGRANT_DEFAULT_PROVIDER']

    def _get_platform(self):
        if self.m._args.get('--platform'):
            if self.m._args['--platform'] != 'all':
                if not [item
                        for item in self.m._config.config['vagrant'][
                            'platforms']
                        if item['name'] == self.m._args['--platform']]:
                    raise baseprovisioner.InvalidPlatformSpecified()
            self.m._state.change_state('default_platform',
                                       self.m._args['--platform'])
            self.m._env['MOLECULE_PLATFORM'] = self.m._args['--platform']
        else:
            self.m._env['MOLECULE_PLATFORM'] = self.default_platform

        return self.m._env['MOLECULE_PLATFORM']

    def _write_vagrant_file(self):
        kwargs = {'config': self.m._config.config,
                  'current_platform': self.platform,
                  'current_provider': self.provider}

        template = self.m._config.config['molecule']['vagrantfile_template']
        dest = self.m._config.config['molecule']['vagrantfile_file']
        utilities.write_template(template, dest, kwargs=kwargs)

    @property
    def name(self):
        return 'vagrant'

    @property
    def instances(self):
        self.populate_platform_instances()
        return self.m._config.config['vagrant']['instances']

    @property
    def default_provider(self):
        # take config's default_provider if specified, otherwise use the first in the provider list
        default_provider = self.m._config.config['molecule'].get(
            'default_provider')
        if default_provider is None:
            default_provider = self.m._config.config['vagrant']['providers'][
                0]['name']

        # default to first entry if no entry for provider exists or provider is false
        if not self.m._state.default_provider:
            return default_provider

        return self.m._state.default_provider

    @property
    def default_platform(self):
        # assume static inventory if there's no vagrant section
        if self.m._config.config.get('vagrant') is None:
            return 'static'

        # assume static inventory if no platforms are listed
        if self.m._config.config['vagrant'].get('platforms') is None:
            return 'static'

        # take config's default_platform if specified, otherwise use the first in the platform list
        default_platform = self.m._config.config['molecule'].get(
            'default_platform')
        if default_platform is None:
            default_platform = self.m._config.config['vagrant']['platforms'][
                0]['name']

        # default to first entry if no entry for platform exists or platform is false
        if not self.m._state.default_platform:
            return default_platform

        return self.m._state.default_platform

    @property
    def provider(self):
        return self._provider

    @property
    def platform(self):
        return self._platform

    @property
    def host_template(self):
        return '{} ansible_ssh_host={} ansible_ssh_port={} ansible_ssh_private_key_file={} ansible_ssh_user={}\n'

    @property
    def valid_providers(self):
        return self.m._config.config['vagrant']['providers']

    @property
    def valid_platforms(self):
        return self.m._config.config['vagrant']['platforms']

    @property
    def ssh_config_file(self):
        return '.vagrant/ssh-config'

    @property
    def testinfra_args(self):
        kwargs = {
            'ansible-inventory':
            self.m._config.config['ansible']['inventory_file'],
            'connection': 'ansible'
        }

        return kwargs

    @property
    def serverspec_args(self):
        return dict()

    @property
    def ansible_connection_params(self):
        params = {'user': 'vagrant', 'connection': 'ssh'}

        return params

    def up(self, no_provision=True):
        self.populate_platform_instances()
        self._write_vagrant_file()
        self._vagrant.up(no_provision)

    def destroy(self):
        if self.m._state.created:
            self._vagrant.destroy()

        if os._exists(self.m._config.config['molecule']['vagrantfile_file']):
            os.remove(self.m._config.config['molecule']['vagrantfile_file'])

    def status(self):
        return self._vagrant.status()

    def conf(self, vm_name=None, ssh_config=False):
        if ssh_config:
            return self._vagrant.ssh_config(vm_name=vm_name)
        else:
            return self._vagrant.conf(vm_name=vm_name)

    def inventory_entry(self, instance):
        # TODO: for Ansiblev2, the following line must have s/ssh_//
        template = '{} ansible_ssh_host={} ansible_ssh_port={} ansible_ssh_private_key_file={} ansible_ssh_user={}\n'

        if not self._updated_multiplatform:
            ssh = self.conf(vm_name=utilities.format_instance_name(
                instance['name'], self._platform, self.instances))
        else:
            ssh = self.conf(vm_name=utilities.format_instance_name(
                instance['name'], 'all', self.instances))

        return template.format(ssh['Host'], ssh['HostName'], ssh['Port'],
                               ssh['IdentityFile'], ssh['User'])

    def login_cmd(self, instance_name):
        return 'ssh {} -l {} -p {} -i {} {}'

    def login_args(self, instance_name):
        # Try to retrieve the SSH configuration of the host.
        conf = self.conf(vm_name=instance_name)

        return [
            conf['HostName'], conf['User'], conf['Port'], conf['IdentityFile'],
            ' '.join(self.m._config.config['molecule']['raw_ssh_args'])
        ]

    def populate_platform_instances(self):
        if self.m._args.get('--platform'):
            if len(self.m._config.config['vagrant'][
                    'platforms']) > 1 and self.m._args[
                        '--platform'] == 'all' and not self._updated_multiplatform:
                new_instances = []

                for instance in self.m._config.config['vagrant']['instances']:
                    for platform in self.m._config.config['vagrant'][
                            'platforms']:
                        platform_instance = copy.deepcopy(instance)
                        platform_instance['platform'] = platform['box']
                        platform_instance['name'] = instance[
                            'name'] + '-' + platform['name']
                        platform_instance['vm_name'] = instance[
                            'name'] + '-' + platform['name']
                        new_instances.append(platform_instance)

                self.m._config.config['vagrant']['instances'] = new_instances
                self._updated_multiplatform = True

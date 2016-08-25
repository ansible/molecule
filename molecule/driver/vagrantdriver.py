#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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

import collections
import copy
import os
import subprocess

import vagrant

from molecule import util
from molecule.driver import basedriver


class VagrantDriver(basedriver.BaseDriver):
    def __init__(self, molecule):
        super(VagrantDriver, self).__init__(molecule)
        self._vagrant = vagrant.Vagrant(quiet_stdout=False, quiet_stderr=False)
        self._provider = self._get_provider()
        self._platform = self._get_platform()
        molecule._env['VAGRANT_VAGRANTFILE'] = molecule.config.config[
            'molecule']['vagrantfile_file']
        self._vagrant.env = molecule._env
        self._updated_multiplatform = False

    @property
    def name(self):
        return 'vagrant'

    @property
    def instances(self):
        self._populate_platform_instances()
        return self.molecule.config.config['vagrant']['instances']

    @property
    def default_provider(self):
        # take config's default_provider if specified, otherwise use the first in the provider list
        default_provider = self.molecule.config.config['molecule'].get(
            'default_provider')
        if default_provider is None:
            default_provider = self.molecule.config.config['vagrant'][
                'providers'][0]['name']

        # default to first entry if no entry for provider exists or provider is false
        if not self.molecule._state.default_provider:
            return default_provider

        return self.molecule._state.default_provider

    @property
    def default_platform(self):
        # assume static inventory if there's no vagrant section
        if self.molecule.config.config.get('vagrant') is None:
            return 'static'

        # assume static inventory if no platforms are listed
        if self.molecule.config.config['vagrant'].get('platforms') is None:
            return 'static'

        # take config's default_platform if specified, otherwise use the first in the platform list
        default_platform = self.molecule.config.config['molecule'].get(
            'default_platform')
        if default_platform is None:
            default_platform = self.molecule.config.config['vagrant'][
                'platforms'][0]['name']

        # default to first entry if no entry for platform exists or platform is false
        if not self.molecule._state.default_platform:
            return default_platform

        return self.molecule._state.default_platform

    @property
    def provider(self):
        return self._provider

    @property
    def platform(self):
        return self._platform

    @platform.setter
    def platform(self, val):
        self._platform = val

    @property
    def valid_providers(self):
        return self.molecule.config.config['vagrant']['providers']

    @property
    def valid_platforms(self):
        return self.molecule.config.config['vagrant']['platforms']

    @property
    def ssh_config_file(self):
        return '.vagrant/ssh-config'

    @property
    def ansible_connection_params(self):
        return {'user': 'vagrant', 'connection': 'ssh'}

    @property
    def testinfra_args(self):
        return {
            'ansible-inventory':
            self.molecule.config.config['ansible']['inventory_file'],
            'connection': 'ansible'
        }

    @property
    def serverspec_args(self):
        return dict()

    def up(self, no_provision=True):
        self._populate_platform_instances()
        self._write_vagrant_file()
        self._vagrant.up(no_provision)

    def destroy(self):
        if self.molecule._state.created:
            self._vagrant.destroy()

        if os._exists(self.molecule.config.config['molecule'][
                'vagrantfile_file']):
            os.remove(self.molecule.config.config['molecule'][
                'vagrantfile_file'])

    def status(self):
        try:
            return self._vagrant.status()
        except subprocess.CalledProcessError:
            return self._fallback_status()

    def conf(self, vm_name=None, ssh_config=False):
        if ssh_config:
            return self._vagrant.ssh_config(vm_name=vm_name)
        else:
            return self._vagrant.conf(vm_name=vm_name)

    def inventory_entry(self, instance):
        # TODO: for Ansiblev2, the following line must have s/ssh_//
        template = '{} ansible_ssh_host={} ansible_ssh_port={} ansible_ssh_private_key_file={} ansible_ssh_user={}\n'

        if not self._updated_multiplatform:
            ssh = self.conf(vm_name=util.format_instance_name(
                instance['name'], self.platform, self.instances))
        else:
            ssh = self.conf(vm_name=util.format_instance_name(
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
            ' '.join(self.molecule.config.config['molecule']['raw_ssh_args'])
        ]

    def _populate_platform_instances(self):
        if self.molecule._args.get('--platform'):
            if len(self.molecule.config.config['vagrant'][
                    'platforms']) > 1 and self.molecule._args[
                        '--platform'] == 'all' and not self._updated_multiplatform:
                new_instances = []

                for instance in self.molecule.config.config['vagrant'][
                        'instances']:
                    for platform in self.molecule.config.config['vagrant'][
                            'platforms']:
                        platform_instance = copy.deepcopy(instance)
                        platform_instance['platform'] = platform['box']
                        platform_instance['name'] = instance[
                            'name'] + '-' + platform['name']
                        platform_instance['vm_name'] = instance[
                            'name'] + '-' + platform['name']
                        new_instances.append(platform_instance)

                self.molecule.config.config['vagrant'][
                    'instances'] = new_instances
                self._updated_multiplatform = True

    def _get_provider(self):
        if self.molecule._args.get('--provider'):
            if not [item
                    for item in self.molecule.config.config['vagrant'][
                        'providers']
                    if item['name'] == self.molecule._args['--provider']]:
                raise basedriver.InvalidDriverSpecified()
            self.molecule._state.change_state(
                'default_provider', self.molecule._args['--provider'])
            self.molecule._env[
                'VAGRANT_DEFAULT_PROVIDER'] = self.molecule._args['--provider']
        else:
            self.molecule._env[
                'VAGRANT_DEFAULT_PROVIDER'] = self.default_provider

        return self.molecule._env['VAGRANT_DEFAULT_PROVIDER']

    def _get_platform(self):
        if self.molecule._args.get('--platform'):
            if self.molecule._args['--platform'] != 'all':
                if not [item
                        for item in self.molecule.config.config['vagrant'][
                            'platforms']
                        if item['name'] == self.molecule._args['--platform']]:
                    raise basedriver.InvalidDriverSpecified()
            self.molecule._state.change_state(
                'default_platform', self.molecule._args['--platform'])
            return self.molecule._args['--platform']
        return self.default_platform

    def _write_vagrant_file(self):
        kwargs = {'config': self.molecule.config.config,
                  'current_platform': self.platform,
                  'current_provider': self.provider}

        template = self.molecule.config.config['molecule'][
            'vagrantfile_template']
        dest = self.molecule.config.config['molecule']['vagrantfile_file']
        util.write_template(template, dest, kwargs=kwargs)

    def _fallback_status(self):
        Status = collections.namedtuple('Status', ['name', 'state',
                                                   'provider'])
        return [Status(name=instance['name'],
                       state='not_created',
                       provider=self.provider) for instance in self.instances]

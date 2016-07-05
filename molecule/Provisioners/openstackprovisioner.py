
import os

import vagrant
from baseprovsioner import *
import molecule.utilities as utilities


class VagrantProvisioner(BaseProvisioner):
    def __init__(self, molecule):
        super(VagrantProvisioner, self).__init__(molecule)
        self._vagrant = vagrant.Vagrant(quiet_stdout=False, quiet_stderr=False)
        self._provider = self._get_provider()
        self._platform = self._get_platform()
        self._vagrant.env = molecule._env

    def _get_provider(self):
        return 'openstack'

    def _get_platform(self):
        return 'openstack'

    def _write_vagrant_file(self):
        kwargs = {'config': self.m._config.config,
                  'current_platform': self.platform,
                  'current_provider': self.provider}

        template = self.m._config.config['molecule']['vagrantfile_template']
        dest = self.m._config.config['molecule']['vagrantfile_file']
        utilities.write_template(template, dest, kwargs=kwargs)

    @property
    def name(self):
        return 'openstack'

    @property
    def instances(self):
        return self.m._config.config['openstack']['instances']

    @property
    def default_provider(self):
        return 'openstack'

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

    def inventory_entry(self, instance):
        # TODO: for Ansiblev2, the following line must have s/ssh_//
        template = '{} ansible_ssh_host={} ansible_ssh_port={} ansible_ssh_private_key_file={} ansible_ssh_user={}\n'

        ssh = self.conf(vm_name=utilities.format_instance_name(
            instance['name'], self._platform, self.instances))
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

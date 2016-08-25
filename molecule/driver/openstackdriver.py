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

import collections
import os

import shade

from molecule import util
from molecule.driver import basedriver

LOG = util.get_logger(__name__)


class OpenstackDriver(basedriver.BaseDriver):
    def __init__(self, molecule):
        super(OpenstackDriver, self).__init__(molecule)
        self._provider = self._get_provider()
        self._platform = self._get_platform()
        self._openstack = shade.openstack_cloud()
        self._keypair_name = None
        self._molecule_generated_ssh_key = False

    def get_keyfile(self):
        if ('keyfile' in self.molecule.config.config['openstack']):
            return self.molecule.config.config['openstack']['keyfile']
        elif self._molecule_generated_ssh_key:
            return util.generated_ssh_key_file_location()
        else:
            LOG.info(
                'Keyfile not specified. molecule will generate a temporary one.')
            self._molecule_generated_ssh_key = True
            return util.generate_temp_ssh_key()

    def get_keypair_name(self):
        if ('keypair' in self.molecule.config.config['openstack']):
            return self.molecule.config.config['openstack']['keypair']
        else:
            LOG.info('Keypair not specified. molecule will generate one.')
            return util.generate_random_keypair_name('molecule', 10)

    @property
    def name(self):
        return 'openstack'

    @property
    def instances(self):
        return self.molecule.config.config['openstack']['instances']

    @property
    def default_provider(self):
        return self._provider

    @property
    def default_platform(self):
        return self._platform

    @property
    def provider(self):
        return self._provider

    @property
    def platform(self):
        return self._platform

    @platform.setter
    def platform(self, val):
        self._platform = val

    def molecule_generated_keypair(self):
        return 'keypair' not in self.molecule.config.config['openstack']

    @property
    def molecule_generated_ssh_key(self):
        return self._molecule_generated_ssh_key

    @property
    def valid_providers(self):
        return [{'name': self.provider}]

    @property
    def valid_platforms(self):
        return [{'name': self.platform}]

    @property
    def ssh_config_file(self):
        return None

    @property
    def ansible_connection_params(self):
        return {'connection': 'ssh'}

    def keypair_name(self):
        return self._keypair_name

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
        self._set_keypair()

        active_instances = self._openstack.list_servers()
        active_instance_names = {instance['name']: instance['status']
                                 for instance in active_instances}

        LOG.warning("Creating openstack instances ...")
        for instance in self.instances:
            if instance['name'] not in active_instance_names:
                LOG.info("\tBringing up {}".format(instance['name']))
                server = self._openstack.create_server(
                    name=instance['name'],
                    image=self._openstack.get_image(instance['image']),
                    flavor=self._openstack.get_flavor(instance['flavor']),
                    auto_ip=True,
                    wait=True,
                    key_name=self._keypair_name,
                    security_groups=instance['security_groups']
                    if 'security_groups' in instance else None)
                util.reset_known_host_key(server['interface_ip'])
                instance['created'] = True
                num_retries = 0
                while not util.check_ssh_availability(
                        server['interface_ip'],
                        instance['sshuser'],
                        timeout=6,
                        sshkey_filename=self.get_keyfile()) or num_retries == 5:
                    LOG.info("\t Waiting for ssh availability...")
                    num_retries += 1

    def destroy(self):
        LOG.info("Deleting openstack instances ...")

        active_instances = self._openstack.list_servers()
        active_instance_names = {instance['name']: instance['id']
                                 for instance in active_instances}

        for instance in self.instances:
            LOG.warning("\tRemoving {} ...".format(instance['name']))
            if instance['name'] in active_instance_names:
                if not self._openstack.delete_server(
                        active_instance_names[instance['name']],
                        wait=True):
                    LOG.error("Unable to remove {}!".format(instance['name']))
                else:
                    util.print_success('\tRemoved {}'.format(instance['name']))
                    instance['created'] = False

        # cleanup any molecule generated files
        if self.molecule_generated_keypair() and self._keypair_name:
            self._openstack.delete_keypair(self._keypair_name)

        if self._molecule_generated_ssh_key:
            util.remove_temp_ssh_key()

    def status(self):
        Status = collections.namedtuple('Status', ['name', 'state',
                                                   'provider'])
        status_list = []
        for instance in self.instances:
            if self._instance_is_accessible(instance):
                status_list.append(Status(name=instance['name'],
                                          state='UP',
                                          provider=self.provider))
            else:
                status_list.append(Status(name=instance['name'],
                                          state='not_created',
                                          provider=self.provider))

        return status_list

    def conf(self, name=None, ssh_config=False):
        inventory_file = self.molecule.config.config['ansible'][
            'inventory_file']
        if os.path.exists(inventory_file):
            with open(inventory_file) as stream:
                for line in stream:
                    if len(line.split()) > 0 and line.split()[0] == name:
                        ansible_host = line.split()[1]
                        host_address = ansible_host.split('=')[1]
                        return host_address
        return None

    def inventory_entry(self, instance):
        template = self._host_template()

        for server in self._openstack.list_servers(detailed=False):
            if server['name'] == instance['name']:
                server_config = { 'hostname' : instance['name'],
                                     'interface_ip_address' : server['interface_ip'], 
                                     'ssh_username' : instance['sshuser']
                                     }
                if self._molecule_generated_ssh_key:
                    server_config['ssh_key_filename'] = 'ansible_ssh_private_key_file={}'.format(util.generated_ssh_key_file_location())
                return template.format(**server_config)
        return ''

    def login_cmd(self, instance_name):
        return 'ssh {} -l {}'

    def login_args(self, instance_name):
        # Try to retrieve the SSH configuration of the host.
        conf = self.conf(name=instance_name)
        user = ''

        for instance in self.instances:
            if instance_name == instance['name']:
                user = instance['sshuser']

        return [conf, user]

    def _get_provider(self):
        return 'openstack'

    def _get_platform(self):
        return 'openstack'

    def _set_keypair(self):
        self._keypair_name = self.get_keypair_name()
        kpn = self._keypair_name

        pub_key_file = self.get_keyfile() + ".pub"

        if self._openstack.search_keypairs(kpn):
            LOG.info('Keypair already exists. Skipping import.')
        else:
            LOG.info('Adding keypair... ' + kpn)
            self._openstack.create_keypair(kpn, open(pub_key_file,
                                                     'r').read().strip())

    def _host_template(self):
        return '{hostname} ansible_ssh_host={interface_ip_address} ansible_ssh_user={ssh_username} {ssh_key_filename} ansible_ssh_extra_args="-o ConnectionAttempts=5"\n'

    def _instance_is_accessible(self, instance):
        instance_ip = self.conf(instance['name'])
        if instance_ip is not None:
            return util.check_ssh_availability(instance_ip,
                                               instance['sshuser'],
                                               timeout=0,
                                               sshkey_filename=self.get_keyfile())
        return False

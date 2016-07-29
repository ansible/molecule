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

import shade

from molecule import utilities
from molecule.provisioners import baseprovisioner


class OpenstackProvisioner(baseprovisioner.BaseProvisioner):
    def __init__(self, molecule):
        super(OpenstackProvisioner, self).__init__(molecule)
        self._provider = self._get_provider()
        self._platform = self._get_platform()
        self._openstack = shade.openstack_cloud()

    def set_keypair(self):
        keypair_name = self.m._config.config['openstack']['keypair']
        pub_key_file = self.m._config.config['openstack']['keyfile']

        if self._openstack.search_keypairs(keypair_name):
            utilities.logger.info('Keypair already exists. Skipping import.')
        else:
            utilities.logger.info('Adding keypair...')
            self._openstack.create_keypair(keypair_name, open(
                pub_key_file, 'r').read().strip())

    def _get_provider(self):
        return 'openstack'

    def _get_platform(self):
        return 'openstack'

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
        return 'openstack'

    @property
    def provider(self):
        return self._provider

    @property
    def platform(self):
        return self._platform

    @property
    def host_template(self):
        return '{} ansible_ssh_host={} ansible_ssh_user={} ansible_ssh_extra_args="-o ConnectionAttempts=5"\n'

    @property
    def valid_providers(self):
        return [{'name': 'Openstack'}]

    @property
    def valid_platforms(self):
        return [{'name': 'Openstack'}]

    @property
    def ssh_config_file(self):
        return None

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
        params = {'connection': 'ssh'}

        return params

    def up(self, no_provision=True):
        self.set_keypair()

        active_instances = self._openstack.list_servers()
        active_instance_names = {instance['name']: instance['status']
                                 for instance in active_instances}

        utilities.logger.warning("Creating openstack instances ...")
        for instance in self.instances:
            if instance['name'] not in active_instance_names:
                utilities.logger.info("\tBringing up {}".format(instance[
                    'name']))
                server = self._openstack.create_server(
                    name=instance['name'],
                    image=self._openstack.get_image(instance['image']),
                    flavor=self._openstack.get_flavor(instance['flavor']),
                    auto_ip=True,
                    wait=True,
                    key_name=self.m._config.config['openstack']['keypair'],
                    security_groups=instance['security_groups']
                    if 'security_groups' in instance else None)
                utilities.reset_known_host_key(server['interface_ip'])
                instance['created'] = True
                num_retries = 0
                while not utilities.check_ssh_availability(
                        server['interface_ip'],
                        instance['sshuser'],
                        timeout=6) or num_retries == 5:
                    utilities.logger.info("\t Waiting for ssh availability...")
                    num_retries += 1

    def destroy(self):
        utilities.logger.info("Deleting openstack instances ...")

        active_instances = self._openstack.list_servers()
        active_instance_names = {instance['name']: instance['id']
                                 for instance in active_instances}

        for instance in self.instances:
            utilities.logger.warning("\tRemoving {} ...".format(instance[
                'name']))
            if instance['name'] in active_instance_names:
                if not self._openstack.delete_server(
                        active_instance_names[instance['name']],
                        wait=True):
                    utilities.logger.error("Unable to remove {}!".format(
                        instance['name']))
                else:
                    utilities.print_success('\tRemoved {}'.format(instance[
                        'name']))
                    instance['created'] = False

    def status(self):
        Status = collections.namedtuple('Status', ['name', 'state',
                                                   'provider'])
        status_list = []

        for instance in self.instances:
            if self.instance_is_accessible(instance):
                status_list.append(Status(name=instance['name'],
                                          state='UP',
                                          provider='Openstack'))
            else:
                status_list.append(Status(name=instance['name'],
                                          state='DOWN',
                                          provider='Openstack'))

        return status_list

    def conf(self, name=None, ssh_config=False):

        with open(self.m._config.config['ansible'][
                'inventory_file']) as instance:
            for line in instance:
                if len(line.split()) > 0 and line.split()[0] == name:
                    ansible_host = line.split()[1]
                    host_address = ansible_host.split('=')[1]
                    return host_address
        return None

    def instance_is_accessible(self, instance):
        instance_ip = self.conf(instance['name'])
        if instance_ip is not None:
            return utilities.check_ssh_availability(instance_ip,
                                                    instance['sshuser'],
                                                    timeout=0)
        return False

    def inventory_entry(self, instance):
        template = self.host_template

        for server in self._openstack.list_servers(detailed=False):
            if server['name'] == instance['name']:
                return template.format(instance['name'],
                                       server['interface_ip'],
                                       instance['sshuser'])
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

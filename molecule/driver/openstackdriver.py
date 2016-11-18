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

import collections
import hashlib
import os
import socket
import sys
import time

import paramiko
try:
    import shade
except ImportError:
    sys.exit('ERROR: Driver missing, install shade!')

from molecule import util
from molecule.driver import basedriver

LOG = util.get_logger(__name__)


class OpenstackDriver(basedriver.BaseDriver):
    def __init__(self, molecule):
        super(OpenstackDriver, self).__init__(molecule)
        self._provider = self._get_provider()
        self._platform = self._get_platform()
        self._openstack = shade.openstack_cloud()

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

    @property
    def valid_providers(self):
        return [{'name': self.provider}]

    @property
    def valid_platforms(self):
        return [{'name': self.platform}]

    @property
    def ssh_config_file(self):
        return

    @property
    def ansible_connection_params(self):
        return {'connection': 'ssh'}

    @property
    def testinfra_args(self):
        return {
            'ansible_inventory':
            self.molecule.config.config['ansible']['inventory_file'],
            'connection': 'ansible'
        }

    @property
    def serverspec_args(self):
        return {}

    def up(self, no_provision=True):
        self.molecule.state.change_state('driver', self.name)
        kpn = self._get_keypair()

        active_instances = self._openstack.list_servers()
        active_instance_names = {
            instance['name']: instance['status']
            for instance in active_instances
        }

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
                    key_name=kpn,
                    security_groups=instance['security_groups']
                    if 'security_groups' in instance else None)
                self._reset_known_host_key(server['interface_ip'])
                instance['created'] = True
                num_retries = 0
                while not self._check_ssh_availability(
                        server['interface_ip'],
                        instance['sshuser'],
                        timeout=6,
                        sshkey_filename=self._get_keyfile(
                        )) or num_retries == 5:
                    LOG.info("\t Waiting for ssh availability ...")
                    num_retries += 1

    def destroy(self):
        LOG.info("Deleting openstack instances ...")

        active_instances = self._openstack.list_servers()
        active_instance_names = {
            instance['name']: instance['id']
            for instance in active_instances
        }

        for instance in self.instances:
            LOG.warning("\tRemoving {} ...".format(instance['name']))
            if instance['name'] in active_instance_names:
                if not self._openstack.delete_server(
                        active_instance_names[instance['name']], wait=True):
                    LOG.error("Unable to remove {}!".format(instance['name']))
                else:
                    util.print_success('\tRemoved {}'.format(instance['name']))
                    instance['created'] = False

        # cleanup any molecule generated ssh keysfiles
        self._cleanup_temp_keys()

    def status(self):
        Status = collections.namedtuple('Status',
                                        ['name', 'state', 'provider'])
        status_list = []
        for instance in self.instances:
            if self._instance_is_accessible(instance):
                status_list.append(
                    Status(
                        name=instance['name'],
                        state='UP',
                        provider=self.provider))
            else:
                status_list.append(
                    Status(
                        name=instance['name'],
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
        return

    def inventory_entry(self, instance):
        template = self._host_template()

        for server in self._openstack.list_servers(detailed=False):
            if server['name'] == instance['name']:
                server_config = {
                    'hostname': instance['name'],
                    'interface_ip_address': server['interface_ip'],
                    'ssh_username': instance['sshuser'],
                    'ssh_key_filename': self._get_keyfile()
                }
                return template.format(**server_config)
        return ''

    def login_cmd(self, instance_name):
        return 'ssh {} -l {} -i {}'

    def login_args(self, instance_name):
        # Try to retrieve the SSH configuration of the host.
        conf = self.conf(name=instance_name)
        user = ''
        keyfile = self._get_keyfile()

        for instance in self.instances:
            if instance_name == instance['name']:
                user = instance['sshuser']

        return [conf, user, keyfile]

    def _get_provider(self):
        return 'openstack'

    def _get_platform(self):
        return 'openstack'

    def _get_keypair(self):
        if ('keypair' in self.molecule.config.config['openstack']):
            return self.molecule.config.config['openstack']['keypair']
        else:
            return self._get_temp_keypair()

    def _get_keyfile(self):
        if ('keyfile' in self.molecule.config.config['openstack']):
            return os.path.expanduser(self.molecule.config.config['openstack'][
                'keyfile'])
        else:
            return self._get_temp_keyfile()

    def _get_temp_keypair(self):
        kpn = self._get_temp_keyname()

        if not self._openstack.search_keypairs(kpn):
            LOG.info("\tCreating openstack keypair {} ...".format(kpn))
            pub_key_file = self._get_keyfile() + '.pub'
            self._openstack.create_keypair(kpn,
                                           open(pub_key_file,
                                                'r').read().strip())

        return kpn

    def _get_temp_keyfile(self):
        kn = self._get_temp_keyname()
        kl = self._get_temp_keylocation()
        pvtloc = kl + '/' + kn
        publoc = kl + '/' + kn + '.pub'

        if not os.path.exists(pvtloc):
            LOG.info("\tCreating local ssh key {} ...".format(pvtloc))
            k = paramiko.RSAKey.generate(2048)
            k.write_private_key_file(pvtloc)
            # write the public key too
            pub = paramiko.RSAKey(filename=pvtloc)
            with open(publoc, 'w') as f:
                f.write("%s %s" % (pub.get_name(), pub.get_base64()))

        return pvtloc

    def _get_temp_keyname(self):
        mpath = os.path.abspath(self.molecule.config.config['molecule'][
            'molecule_dir'])
        return 'molecule_' + hashlib.sha256(mpath).hexdigest()[:10]

    def _get_temp_keylocation(self):
        loc = self.molecule.config.config['molecule']['molecule_dir'] + '/.ssh'
        if not os.path.exists(loc):
            os.makedirs(loc)
        return os.path.abspath(loc)

    def _reset_known_host_key(self, hostname):
        return os.system('ssh-keygen -R {}'.format(hostname))

    def _check_ssh_availability(self, hostip, user, timeout, sshkey_filename):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostip, username=user, key_filename=sshkey_filename)
            return True
        except (paramiko.BadHostKeyException, paramiko.AuthenticationException,
                paramiko.SSHException, socket.error):
            time.sleep(timeout)
            return False

    def _cleanup_temp_keys(self):
        # if we don't have a keypair config, delete the temp one
        if ('keypair' not in self.molecule.config.config['openstack']):
            kpn = self._get_temp_keyname()
            if self._openstack.search_keypairs(kpn):
                LOG.warning("\tRemoving openstack keypair {} ...".format(kpn))
                if not self._openstack.delete_keypair(kpn):
                    LOG.error("Unable to remove openstack keypair {}!".format(
                        kpn))
                else:
                    util.print_success('\tRemoved openstack keypair {}'.format(
                        kpn))

        # if we don't have a keyfile config, delete the temp one
        if ('keyfile' not in self.molecule.config.config['openstack']):
            kn = self._get_temp_keyname()
            kl = self._get_temp_keylocation()
            pvtloc = kl + '/' + kn
            publoc = kl + '/' + kn + '.pub'
            if os.path.exists(pvtloc):
                LOG.warning("\tRemoving {} ...".format(pvtloc))
                os.remove(pvtloc)
            if os.path.exists(publoc):
                LOG.warning("\tRemoving {} ...".format(publoc))
                os.remove(publoc)

    def _host_template(self):
        return ('{hostname} ansible_ssh_host={interface_ip_address} '
                'ansible_ssh_user={ssh_username} '
                'ansible_ssh_private_key_file={ssh_key_filename} '
                'ansible_ssh_extra_args="-o ConnectionAttempts=5"\n')

    def _instance_is_accessible(self, instance):
        instance_ip = self.conf(instance['name'])
        if instance_ip is not None:
            return self._check_ssh_availability(
                instance_ip,
                instance['sshuser'],
                timeout=0,
                sshkey_filename=self._get_keyfile())
        return False

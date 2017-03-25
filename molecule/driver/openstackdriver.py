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
import sys
import time

from subprocess import check_output, CalledProcessError, STDOUT

import paramiko
try:
    import shade
except ImportError:  # pragma: no cover
    sys.exit('ERROR: Driver missing, install shade.')

from molecule import util
from molecule.driver import basedriver


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
    def ip_pool(self):
        return self.molecule.config.config['openstack'].get('ip_pool')

    @property
    def networks(self):
        return self.molecule.config.config['openstack']['networks']

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
    def ssh_timeout(self):
        return self.molecule.config.config['openstack'].get('ssh_timeout', 30)

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
            instance['name']: instance['interface_ip']
            for instance in active_instances
        }

        util.print_warn('Creating openstack instances...')
        for instance in self.instances:

            try:
                # We divide the ssh_timeout by 2, because the connect
                # itself takes at least a second and is followed by
                # a 1 sec sleep
                ssh_timeout = int(
                    instance.get('ssh_timeout', self.ssh_timeout) / 2)
            except TypeError:
                util.print_error('Can not cast ssh_timeout setting "%s"'
                                 ' to int' %
                                 instance.get('ssh_timeout', self.ssh_timeout))
                util.sysexit()

            if instance['name'] not in active_instance_names:
                msg = '\tBringing up {}...'.format(instance['name'])
                util.print_info(msg)
                server = self._openstack.create_server(
                    name=instance['name'],
                    image=self._openstack.get_image(instance['image']),
                    flavor=self._openstack.get_flavor(instance['flavor']),
                    auto_ip=True,
                    wait=False,
                    key_name=kpn,
                    ip_pool=instance.get('ip_pool')
                    if instance.get('ip_pool') else self.ip_pool,
                    network=instance.get('networks', []),
                    security_groups=instance.get('security_groups', []))
                instance['created'] = True
                instance['reachable'] = False
                instance['server'] = server
            else:
                instance['address'] = active_instance_names[instance['name']]
                instance['reachable'] = True

        for instance in self.instances:
            if not instance.get('server'):
                instance['server'] = self._openstack.get_server(instance[
                    'name'])
            if not instance.get('address'):
                util.print_info(
                    '\t Waiting for instance %s to be in state active...' %
                    instance['name'])
                server = self._openstack.wait_for_server(
                    instance['server'], auto_ip=True)
                instance['address'] = server['interface_ip']

        for instance in self.instances:
            for _ in range(ssh_timeout):
                util.print_info(
                    '\t  Waiting for ssh availability of instance %s...' %
                    instance['name'])
                if self._check_ssh_availability(
                        instance['address'],
                        instance['sshuser'],
                        timeout=1,
                        sshkey_filename=self._get_keyfile()):
                    instance['reachable'] = True
                    break
            if not instance['reachable']:
                util.print_error(
                    'Could not reach instance "%s"'
                    ' within limit of %s seconds' %
                    (instance['name'],
                     instance.get('ssh_timeout', self.ssh_timeout)))
                util.sysexit()

    def destroy(self):
        util.print_info('Deleting openstack instances...')

        active_instances = self._openstack.list_servers()
        active_instance_names = {
            instance['name']: instance['id']
            for instance in active_instances
        }

        for instance in self.instances:
            util.print_warn('\tRemoving {}...'.format(instance['name']))
            if instance['name'] in active_instance_names:
                if not self._openstack.delete_server(
                        active_instance_names[instance['name']], wait=True):
                    msg = 'Unable to remove {}.'.format(instance['name'])
                    util.print_error(msg)
                else:
                    util.print_success('\tRemoved {}.'.format(instance[
                        'name']))
                    instance['created'] = False

        # cleanup any molecule generated ssh keysfiles
        self._cleanup_temp_keypair()
        self._cleanup_temp_keyfile()

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
        return 'ssh {} -l {} {}'

    def login_args(self, instance_name):
        # Try to retrieve the SSH configuration of the host.
        conf = self.conf(name=instance_name)
        user = ''
        keyfile_arg = ''
        if self._get_keyfile():
            keyfile_arg = '-i %s' % self._get_temp_keyfile()

        for instance in self.instances:
            if instance_name == instance['name']:
                user = instance['sshuser']

        return [conf, user, keyfile_arg]

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
        if 'keypair' not in self.molecule.config.config['openstack']:
            return self._get_temp_keyfile()
        elif 'keyfile' in self.molecule.config.config['openstack']:
            return os.path.expanduser(self.molecule.config.config['openstack'][
                'keyfile'])

    def _get_temp_keypair(self):
        kpn = self._get_temp_keyname()

        if not self._openstack.search_keypairs(kpn):
            msg = '\tCreating openstack keypair {}...'.format(kpn)
            util.print_info(msg)
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
            util.print_info('\tCreating local ssh key {}...'.format(pvtloc))
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

    def _check_ssh_availability(self,
                                hostip,
                                user,
                                timeout,
                                sshkey_filename=None):
        key_arg = '-i %s' % sshkey_filename if sshkey_filename else ''
        command = 'ssh -o StrictHostKeyChecking=no -o '\
                  'UserKnownHostsFile=/dev/null -o'\
                  'BatchMode=yes %s -l %s %s exit'\
                  % (key_arg, user, hostip)
        command = command.split()
        try:
            check_output(command, stderr=STDOUT)
            return True
        except CalledProcessError:
            time.sleep(timeout)
            return False

    def _cleanup_temp_keypair(self):
        # if we don't have a keypair config, delete the temp one
        if ('keypair' not in self.molecule.config.config['openstack']):
            kpn = self._get_temp_keyname()
            if self._openstack.search_keypairs(kpn):
                msg = '\tRemoving openstack keypair {}...'.format(kpn)
                util.print_warn(msg)
                if not self._openstack.delete_keypair(kpn):
                    msg = 'Unable to remove openstack keypair {}.'.format(kpn)
                    util.print_error(msg)
                else:
                    msg = '\tRemoved openstack keypair {}.'.format(kpn)
                    util.print_success(msg)

    def _cleanup_temp_keyfile(self):
        # if we don't have a keyfile config, delete the temp one
        if ('keyfile' not in self.molecule.config.config['openstack']):
            kn = self._get_temp_keyname()
            kl = self._get_temp_keylocation()
            pvtloc = kl + '/' + kn
            publoc = kl + '/' + kn + '.pub'
            if os.path.exists(pvtloc):
                util.print_warn('\tRemoving {}...'.format(pvtloc))
                os.remove(pvtloc)
            if os.path.exists(publoc):
                util.print_warn('\tRemoving {}...'.format(publoc))
                os.remove(publoc)

    def _host_template(self):
        return ('{hostname} ansible_host={interface_ip_address} '
                'ansible_user={ssh_username} '
                'ansible_ssh_private_key_file="{ssh_key_filename}" '
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

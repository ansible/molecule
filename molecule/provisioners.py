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

import os
import sys

import sh
from colorama import Fore

from molecule.core import Molecule
import molecule.utilities as utilities


class Ansible(Molecule):
    def __init__(self, args):
        super(self.__class__, self).__init__(args)

    def _remove_templates(self):
        os.remove(self._config.config['molecule']['vagrantfile_file'])
        os.remove(self._config.config['molecule']['rakefile_file'])
        os.remove(self._config.config['molecule']['config_file'])

    def _create_templates(self):
        self._populate_instance_names()

        # vagrantfile
        kwargs = {
            'config': self._config.config,
            'current_platform': self._env['MOLECULE_PLATFORM'],
            'current_provider': self._env['VAGRANT_DEFAULT_PROVIDER']
        }
        utilities.write_template(self._config.config['molecule']['vagrantfile_template'],
                                 self._config.config['molecule']['vagrantfile_file'],
                                 kwargs=kwargs)

        # ansible.cfg
        utilities.write_template(self._config.config['molecule']['ansible_config_template'],
                                 self._config.config['molecule']['config_file'])

        # rakefile
        kwargs = {
            'molecule_file': self._config.config['molecule']['molecule_file'],
            'current_platform': self._env['MOLECULE_PLATFORM']
        }
        utilities.write_template(self._config.config['molecule']['rakefile_template'],
                                 self._config.config['molecule']['rakefile_file'],
                                 kwargs=kwargs)

    def _populate_instance_names(self):
        for instance in self._config.config['vagrant']['instances']:
            instance['vm_name'] = utilities.format_instance_name(instance['name'], self._env['MOLECULE_PLATFORM'],
                                                                 self._config.config['vagrant']['instances'])

    def _create_inventory_file(self):
        inventory = ''
        # TODO: for Ansiblev2, the following line must have s/ssh_//
        host_template = \
            '{} ansible_ssh_host={} ansible_ssh_port={} ansible_ssh_private_key_file={} ansible_ssh_user={}\n'
        for instance in self._config.config['vagrant']['instances']:
            ssh = self._vagrant.conf(vm_name=utilities.format_instance_name(instance['name'], self._env[
                'MOLECULE_PLATFORM'], self._config.config['vagrant']['instances']))
            inventory += host_template.format(ssh['Host'], ssh['HostName'], ssh['Port'], ssh['IdentityFile'],
                                              ssh['User'])

        # get a list of all groups and hosts in those groups
        groups = {}
        for instance in self._config.config['vagrant']['instances']:
            if 'ansible_groups' in instance:
                for group in instance['ansible_groups']:
                    if group not in groups:
                        groups[group] = []
                    groups[group].append(instance['name'])

        for group, instances in groups.iteritems():
            inventory += '\n[{}]\n'.format(group)
            for instance in instances:
                inventory += '{}\n'.format(utilities.format_instance_name(instance, self._env['MOLECULE_PLATFORM'],
                                                                          self._config.config['vagrant']['instances']))

        inventory_file = self._config.config['molecule']['inventory_file']
        try:
            utilities.write_file(inventory_file, inventory)
        except IOError:
            print('{}WARNING: could not write inventory file {}{}'.format(Fore.YELLOW, inventory_file, Fore.RESET))

    def _create_playbook_args(self):
        # don't pass these to molecule-playbook CLI
        env_args = ['raw_ssh_args', 'host_key_checking', 'config_file', 'raw_env_vars']

        # args that molecule-playbook doesn't accept as --arg=value
        special_args = ['playbook', 'verbose']

        # set raw environment variables if any are found
        if 'raw_env_vars' in self._config.config['ansible']:
            for key, value in self._config.config['ansible']['raw_env_vars'].iteritems():
                self._env[key] = value

        # grab inventory_file default from molecule if it's not set in the user-supplied ansible options
        if 'inventory_file' not in self._config.config['ansible']:
            self._config.config['ansible']['inventory_file'] = self._config.config['molecule']['inventory_file']

        # grab config_file default from molecule if it's not set in the user-supplied ansible options
        if 'config_file' not in self._config.config['ansible']:
            self._config.config['ansible']['config_file'] = self._config.config['molecule']['config_file']

        self._env['PYTHONUNBUFFERED'] = '1'
        self._env['ANSIBLE_FORCE_COLOR'] = 'true'
        self._env['ANSIBLE_HOST_KEY_CHECKING'] = str(self._config.config['ansible']['host_key_checking']).lower()
        self._env['ANSIBLE_SSH_ARGS'] = ' '.join(self._config.config['ansible']['raw_ssh_args'])
        self._env['ANSIBLE_CONFIG'] = self._config.config['ansible']['config_file']

        kwargs = {}
        args = []

        # pull in values passed to molecule CLI
        if '--tags' in self._args:
            self._config.config['ansible']['tags'] = self._args['--tags']

        # pass supported --arg=value args
        for arg, value in self._config.config['ansible'].iteritems():
            # don't pass False arguments to ansible-playbook
            if value and arg not in (env_args + special_args):
                kwargs[arg] = value

        # verbose is weird -vvvv
        if self._config.config['ansible']['verbose']:
            args.append('-' + self._config.config['ansible']['verbose'])

        kwargs['_env'] = self._env
        kwargs['_out'] = utilities.print_stdout
        kwargs['_err'] = utilities.print_stderr

        return self._config.config['ansible']['playbook'], args, kwargs

    def idempotence(self):
        print('{}Idempotence test in progress...{}'.format(Fore.CYAN, Fore.RESET)),

        output = self.converge(idempotent=True)
        idempotent = self._parse_provisioning_output(output.stdout)

        if idempotent:
            print('{}OKAY{}'.format(Fore.GREEN, Fore.RESET))
            return

        print('{}FAILED{}'.format(Fore.RED, Fore.RESET))
        sys.exit(1)

    def converge(self, idempotent=False):
        if not idempotent:
            self.create()

        self._create_inventory_file()
        playbook, args, kwargs = self._create_playbook_args()

        if idempotent:
            kwargs.pop('_out', None)
            kwargs.pop('_err', None)
            kwargs['_env']['ANSIBLE_NOCOLOR'] = 'true'
            kwargs['_env']['ANSIBLE_FORCE_COLOR'] = 'false'
            try:
                output = sh.ansible_playbook(playbook, *args, **kwargs)
                return output
            except sh.ErrorReturnCode as e:
                print('ERROR: {}'.format(e))
                sys.exit(e.exit_code)
        try:
            output = sh.ansible_playbook(playbook, *args, **kwargs)
            return output.exit_code
        except sh.ErrorReturnCode as e:
            print('ERROR: {}'.format(e))
            sys.exit(e.exit_code)

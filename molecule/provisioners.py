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
import yaml
from colorama import Fore

from molecule.core import Molecule
import molecule.utilities as utilities


class Ansible(Molecule):
    def __init__(self, args):
        super(self.__class__, self).__init__(args)
        self._env['VAGRANT_VAGRANTFILE'] = self._config['vagrantfile_file']

    def _load_molecule_file(self, config):
        if not os.path.isfile(config['molecule_file']):
            error = "\n{0}Unable to find {1}. Exiting.{2}"
            print(error.format(Fore.RED, config['molecule_file'], Fore.RESET))
            sys.exit(1)

        with open(config['molecule_file'], 'r') as env:
            try:
                config = yaml.load(env)
            except Exception as e:
                error = "\n{0}{1} isn't properly formatted: {2}{3}"
                print(error.format(Fore.RED, config['molecule_file'], e, Fore.RESET))
                sys.exit(1)

        return config

    def _remove_templates(self):
        os.remove(self._config['vagrantfile_file'])
        os.remove(self._config['rakefile_file'])
        os.remove(self._config['ansible']['config_file'])

    def _create_templates(self):
        self._populate_instance_names()

        # vagrantfile
        kwargs = {'molecule': self._molecule_file['vagrant'],
                'config': self._config,
                'current_platform': self._env['MOLECULE_PLATFORM'],
                'current_provider': self._env['VAGRANT_DEFAULT_PROVIDER']}
        utilities.write_template(self._config['vagrantfile_template'], self._config['vagrantfile_file'], kwargs=kwargs)

        # ansible.cfg
        utilities.write_template(self._config['ansible_config_template'], self._config['ansible']['config_file'])

        # rakefile
        kwargs = {'molecule_file': self._config['molecule_file'], 'current_platform': self._env['MOLECULE_PLATFORM']}
        utilities.write_template(self._config['rakefile_template'], self._config['rakefile_file'], kwargs=kwargs)

    def _format_instance_name(self, name):
        for instance in self._molecule_file['vagrant']['instances']:
            if instance['name'] == name:
                if 'options' in instance and instance['options'] is not None:
                    if 'append_platform_to_hostname' in instance['options']:
                        if not instance['options']['append_platform_to_hostname']:
                            return name
        return name + '-' + self._env['MOLECULE_PLATFORM']

    def _populate_instance_names(self):
        for instance in self._molecule_file['vagrant']['instances']:
            instance['vm_name'] = self._format_instance_name(instance['name'])

    def _create_inventory_file(self):
        inventory = ''
        # TODO: for Ansiblev2, the following line must have s/ssh_//
        host_template = \
            "{0} ansible_ssh_host={1} ansible_ssh_port={2} ansible_ssh_private_key_file={3} ansible_ssh_user={4}\n"
        for instance in self._molecule_file['vagrant']['instances']:
            ssh = self._vagrant.conf(vm_name=self._format_instance_name(instance['name']))
            inventory += host_template.format(ssh['Host'], ssh['HostName'], ssh['Port'], ssh['IdentityFile'],
                                              ssh['User'])

        # get a list of all groups and hosts in those groups
        groups = {}
        for instance in self._molecule_file['vagrant']['instances']:
            if 'ansible_groups' in instance:
                for group in instance['ansible_groups']:
                    if group not in groups:
                        groups[group] = []
                    groups[group].append(instance['name'])

        for group, instances in groups.iteritems():
            inventory += "\n[{0}]\n".format(group)
            for instance in instances:
                inventory += "{0}\n".format(self._format_instance_name(instance))

        inventory_file = self._config['ansible']['inventory_file']
        utilities.write_file(inventory_file, inventory)

    def _create_playbook_args(self):
        merged_args = self._config['ansible'].copy()

        # don't pass these to molecule-playbook CLI
        env_args = ['raw_ssh_args', 'host_key_checking', 'config_file', 'raw_env_vars']

        # args that molecule-playbook doesn't accept as --arg=value
        special_args = ['playbook', 'verbose']

        # merge defaults with molecule.yml values
        if 'ansible' in self._molecule_file:
            merged_args = utilities.merge_dicts(merged_args, self._molecule_file['ansible'])

            # set raw environment variables if any are found
            if 'raw_env_vars' in self._molecule_file['ansible']:
                for key, value in self._molecule_file['ansible']['raw_env_vars'].iteritems():
                    self._env[key] = value

        self._env['PYTHONUNBUFFERED'] = '1'
        self._env['ANSIBLE_FORCE_COLOR'] = 'true'
        self._env['ANSIBLE_HOST_KEY_CHECKING'] = str(merged_args['host_key_checking']).lower()
        self._env['ANSIBLE_SSH_ARGS'] = ' '.join(merged_args['raw_ssh_args'])
        self._env['ANSIBLE_CONFIG'] = merged_args['config_file']

        kwargs = {}
        args = []

        # pull in values passed to molecule CLI
        if '--tags' in self._args:
            merged_args['tags'] = self._args['--tags']

        # pass supported --arg=value args
        for arg, value in merged_args.iteritems():
            # don't pass False arguments to ansible-playbook
            if value and arg not in (env_args + special_args):
                kwargs[arg] = value

        # verbose is weird -vvvv
        if merged_args['verbose']:
            args.append('-' + merged_args['verbose'])

        kwargs['_env'] = self._env
        kwargs['_out'] = utilities.print_line
        kwargs['_err'] = utilities.print_line

        return merged_args['playbook'], args, kwargs

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
                print("ERROR: {0}".format(e))
                sys.exit(e.exit_code)
        try:
            output = sh.ansible_playbook(playbook, *args, **kwargs)
            return output.exit_code
        except sh.ErrorReturnCode as e:
            print("ERROR: {0}".format(e))
            sys.exit(e.exit_code)

    def verify(self):
        self._verify()

    def create(self):
        self._create_templates()
        self._create()

    def destroy(self):
        self._create_templates()
        self._destroy()
        self._remove_templates()

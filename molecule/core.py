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

import fcntl
import os
import re
import struct
import sys
import termios
from subprocess import CalledProcessError

import yaml
from colorama import Fore

import molecule.config as config
import molecule.utilities as utilities
import molecule.provisioners as provisioners


class Molecule(object):
    def __init__(self, args):
        self._provisioned = False
        self._env = os.environ.copy()
        self._args = args
        self._config = config.Config()
        self._provisioner = None

    def main(self):
        # load molecule defaults
        self._config.load_defaults_file()

        # merge in any molecule config files found (eg: ~/.configs/molecule/config.yml)
        self._config.merge_molecule_config_files()

        # init command doesn't need to load molecule.yml
        if self._args['init']:
            return  # exits program

        # merge in molecule.yml
        self._config.merge_molecule_file()

        # concatentate file names and paths within config so they're more convenient to use
        self._config.build_easy_paths()

        # get defaults for inventory/ansible.cfg from molecule if none are specified
        self._config.update_ansible_defaults()

        self._state = self._load_state_file()

        try:
            self._provisioner = provisioners.get_provisioner(self)
        except provisioners.InvalidProviderSpecified:
            print("\n{}Invalid provider '{}'\n".format(Fore.RED, self._args['--provider'], Fore.RESET))
            self._print_valid_providers()
            sys.exit(1)
        except provisioners.InvalidPlatformSpecified:
            print("\n{}Invalid platform '{}'\n".format(Fore.RED, self._args['--platform'], Fore.RESET))
            self._print_valid_platforms()
            sys.exit(1)

        if not os.path.exists(self._config.config['molecule']['molecule_dir']):
            os.makedirs(self._config.config['molecule']['molecule_dir'])

        if self._args['--tags']:
            self._env['MOLECULE_TAGS'] = self._args['--tags']

        # updates instances config with full machine names
        self._config.populate_instance_names(self._env['MOLECULE_PLATFORM'])
        if self._args['--debug']:
            utilities.debug('RUNNING CONFIG', yaml.dump(self._config.config, default_flow_style=False, indent=2))

        self._write_state_file()

    def _load_state_file(self):
        """
        Looks for a molecule state file and loads it.

        :return: Contents of state file as a dict if found, otherwise empty dict.
        """
        if not os.path.isfile(self._config.config['molecule']['state_file']):
            return {}

        with open(self._config.config['molecule']['state_file'], 'r') as env:
            return yaml.safe_load(env)

    def _write_state_file(self):
        utilities.write_file(self._config.config['molecule']['state_file'],
                             yaml.dump(self._state,
                                       default_flow_style=False))

    def _write_ssh_config(self):
        try:
            out = self._provisioner.conf(ssh_config=True)
            ssh_config = self._provisioner.ssh_config_file
        except CalledProcessError as e:
            print('ERROR: {}'.format(e))
            print("Does your vagrant VM exist?")
            sys.exit(e.returncode)
        utilities.write_file(ssh_config, out)

    def _print_valid_platforms(self, machine_readable=False):
        if not machine_readable:
            print(Fore.CYAN + "AVAILABLE PLATFORMS" + Fore.RESET)
        default_platform = self._provisioner.default_platform
        for platform in self._provisioner.valid_platforms:
            default = ' (default)' if platform['name'] == default_platform and not machine_readable else ''
            print(platform['name'] + default)

    def _print_valid_providers(self):
        print(Fore.CYAN + "AVAILABLE PROVIDERS" + Fore.RESET)
        default_provider = self._provisioner.default_provider
        for provider in self._provisioner.valid_providers:
            default = ' (default)' if provider['name'] == default_provider else ''
            print(provider['name'] + default)

    def _sigwinch_passthrough(self, sig, data):
        TIOCGWINSZ = 1074295912  # assume
        if 'TIOCGWINSZ' in dir(termios):
            TIOCGWINSZ = termios.TIOCGWINSZ
        s = struct.pack('HHHH', 0, 0, 0, 0)
        a = struct.unpack('HHHH', fcntl.ioctl(sys.stdout.fileno(), TIOCGWINSZ, s))
        self._pt.setwinsize(a[0], a[1])

    def _parse_provisioning_output(self, output):
        """
        Parses the output of the provisioning method.

        :param output:
        :return: True if the playbook is idempotent, otherwise False
        """

        # remove blank lines to make regex matches easier
        output = re.sub("\n\s*\n*", "\n", output)

        # look for any non-zero changed lines
        changed = re.search(r'(changed=[1-9][0-9]*)', output)

        # Look for the tasks that have changed.
        p = re.compile(ur'NI: (.*$)', re.MULTILINE | re.IGNORECASE)
        changed_tasks = re.findall(p, output)

        if changed:
            return False, changed_tasks

        return True, []

    def _remove_templates(self):
        """
        Removes the templates created by molecule.

        :return: None
        """
        os.remove(self._config.config['molecule']['rakefile_file'])
        os.remove(self._config.config['molecule']['config_file'])

    def _create_templates(self):
        """
        Creates the templates used by molecule.

        :return: None
        """
        # ansible.cfg
        utilities.write_template(self._config.config['molecule']['ansible_config_template'],
                                 self._config.config['molecule']['config_file'])

        # rakefile
        kwargs = {
            'molecule_file': self._config.config['molecule']['molecule_file'],
            'current_platform': self._env['MOLECULE_PLATFORM'],
            'serverspec_dir': self._config.config['molecule']['serverspec_dir']
        }
        utilities.write_template(self._config.config['molecule']['rakefile_template'],
                                 self._config.config['molecule']['rakefile_file'],
                                 kwargs=kwargs)

    def _create_inventory_file(self):
        """
        Creates the inventory file used by molecule and later passed to ansible-playbook.

        :return: None
        """
        inventory = ''
        # TODO: for Ansiblev2, the following line must have s/ssh_//
        host_template = \
            '{} ansible_ssh_host={} ansible_ssh_port={} ansible_ssh_private_key_file={} ansible_ssh_user={}\n'
        for instance in self._provisioner.instances:
            ssh = self._provisioner.conf(vm_name=utilities.format_instance_name(instance['name'], self._env[
                'MOLECULE_PLATFORM'], self._provisioner.instances))
            inventory += host_template.format(ssh['Host'], ssh['HostName'], ssh['Port'], ssh['IdentityFile'],
                                              ssh['User'])

        # get a list of all groups and hosts in those groups
        groups = {}
        for instance in self._provisioner.instances:
            if 'ansible_groups' in instance:
                for group in instance['ansible_groups']:
                    if group not in groups:
                        groups[group] = []
                    groups[group].append(instance['name'])

        for group, instances in groups.iteritems():
            inventory += '\n[{}]\n'.format(group)
            for instance in instances:
                inventory += '{}\n'.format(utilities.format_instance_name(instance, self._env['MOLECULE_PLATFORM'],
                                                                          self._provisioner.instances))

        inventory_file = self._config.config['molecule']['inventory_file']
        try:
            utilities.write_file(inventory_file, inventory)
        except IOError:
            print('{}WARNING: could not write inventory file {}{}'.format(Fore.YELLOW, inventory_file, Fore.RESET))

    def _create_playbook_args(self):
        """
        Builds up CLI and ENV arguments from various config files to be passed to ansible-playbook.

        :return: None
        """
        # don't pass these to molecule-playbook CLI
        env_args = ['raw_ssh_args', 'host_key_checking', 'config_file', 'raw_env_vars']

        # args that molecule-playbook doesn't accept as --arg=value
        special_args = ['playbook', 'verbose']

        # set raw environment variables if any are found
        if 'raw_env_vars' in self._config.config['ansible']:
            for key, value in self._config.config['ansible']['raw_env_vars'].iteritems():
                self._env[key] = value

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

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

import fcntl
import os
import re
import struct
import sys
import termios
import subprocess

import tabulate
import yaml

from molecule import config
from molecule import state
from molecule import utilities
from molecule.provisioners import baseprovisioner
from molecule.provisioners import dockerprovisioner
from molecule.provisioners import openstackprovisioner
from molecule.provisioners import proxmoxprovisioner
from molecule.provisioners import vagrantprovisioner


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
        if self._args.get('<command>') == 'init':
            return  # exits program

        # merge in molecule.yml
        self._config.merge_molecule_file()

        # ensure the .molecule directory exists
        if not os.path.isdir(os.path.join(os.curdir, self._config.config[
                'molecule']['molecule_dir'])):
            os.mkdir(os.path.join(os.curdir, self._config.config['molecule'][
                'molecule_dir']))

        # concatentate file names and paths within config so they're more convenient to use
        self._config.build_easy_paths()

        # get defaults for inventory/ansible.cfg from molecule if none are specified
        self._config.update_ansible_defaults()

        self._state = state.State(
            state_file=self._config.config.get('molecule').get('state_file'))

        try:
            self._provisioner = self.get_provisioner()
        except baseprovisioner.InvalidProviderSpecified:
            utilities.logger.error("\nInvalid provider '{}'\n".format(
                self._args['--provider']))
            self._args['--provider'] = None
            self._args['--platform'] = None
            self._provisioner = self.get_provisioner()
            self._print_valid_providers()
            sys.exit(1)
        except baseprovisioner.InvalidPlatformSpecified:
            utilities.logger.error("\nInvalid platform '{}'\n".format(
                self._args['--platform']))
            self._args['--provider'] = None
            self._args['--platform'] = None
            self._provisioner = self.get_provisioner()
            self._print_valid_platforms()
            sys.exit(1)

        if not os.path.exists(self._config.config['molecule']['molecule_dir']):
            os.makedirs(self._config.config['molecule']['molecule_dir'])

        # updates instances config with full machine names
        self._config.populate_instance_names(self._env['MOLECULE_PLATFORM'])

        if self._args.get('--debug'):
            utilities.debug('RUNNING CONFIG',
                            yaml.dump(self._config.config,
                                      default_flow_style=False,
                                      indent=2))

    def get_provisioner(self):
        if 'vagrant' in self._config.config:
            return vagrantprovisioner.VagrantProvisioner(self)
        elif 'proxmox' in self._config.config:
            return proxmoxprovisioner.ProxmoxProvisioner(self)
        elif 'docker' in self._config.config:
            return dockerprovisioner.DockerProvisioner(self)
        elif 'openstack' in self._config.config:
            return openstackprovisioner.OpenstackProvisioner(self)
        else:
            return None

    def _write_ssh_config(self):
        try:
            out = self._provisioner.conf(ssh_config=True)
            ssh_config = self._provisioner.ssh_config_file
            if ssh_config is None:
                return
        except subprocess.CalledProcessError as e:
            utilities.logger.error('ERROR: {}'.format(e))
            utilities.logger.error("Does your vagrant VM exist?")
            sys.exit(e.returncode)
        utilities.write_file(ssh_config, out)

    def _print_valid_platforms(self, porcelain=False):
        if not porcelain:
            utilities.logger.info("AVAILABLE PLATFORMS")

        data = []
        default_platform = self._provisioner.default_platform
        for platform in self._provisioner.valid_platforms:
            if porcelain:
                default = 'd' if platform['name'] == default_platform else ''
            else:
                default = ' (default)' if platform[
                    'name'] == default_platform else ''
            data.append([platform['name'], default])

        self._display_tabulate_data(data)

    def _print_valid_providers(self, porcelain=False):
        if not porcelain:
            utilities.logger.info("AVAILABLE PROVIDERS")

        data = []
        default_provider = self._provisioner.default_provider
        for provider in self._provisioner.valid_providers:
            if porcelain:
                default = 'd' if provider['name'] == default_provider else ''
            else:
                default = ' (default)' if provider[
                    'name'] == default_provider else ''

            data.append([provider['name'], default])

        self._display_tabulate_data(data)

    def _sigwinch_passthrough(self, sig, data):
        TIOCGWINSZ = 1074295912  # assume
        if 'TIOCGWINSZ' in dir(termios):
            TIOCGWINSZ = termios.TIOCGWINSZ
        s = struct.pack('HHHH', 0, 0, 0, 0)
        a = struct.unpack('HHHH', fcntl.ioctl(sys.stdout.fileno(), TIOCGWINSZ,
                                              s))
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
        kwargs = {'molecule_dir':
                  self._config.config['molecule']['molecule_dir']}
        utilities.write_template(
            self._config.config['molecule']['ansible_config_template'],
            self._config.config['molecule']['config_file'], kwargs=kwargs)

        # rakefile
        kwargs = {
            'molecule_file': self._config.config['molecule']['molecule_file'],
            'current_platform': self._env['MOLECULE_PLATFORM'],
            'serverspec_dir': self._config.config['molecule']['serverspec_dir']
        }
        utilities.write_template(
            self._config.config['molecule']['rakefile_template'],
            self._config.config['molecule']['rakefile_file'], kwargs=kwargs)

    def _create_inventory_file(self):
        """
        Creates the inventory file used by molecule and later passed to ansible-playbook.

        :return: None
        """

        inventory = ''

        for instance in self._provisioner.instances:
            inventory += self._provisioner.inventory_entry(instance)

        # get a list of all groups and hosts in those groups
        groups = {}
        for instance in self._provisioner.instances:
            if 'ansible_groups' in instance:
                for group in instance['ansible_groups']:
                    if group not in groups:
                        groups[group] = []
                    groups[group].append(instance['name'])

        if self._args.get('--platform') == 'all':
            self._env['MOLECULE_PLATFORM'] = 'all'

        for group, instances in groups.iteritems():
            inventory += '\n[{}]\n'.format(group)
            for instance in instances:
                inventory += '{}\n'.format(utilities.format_instance_name(
                    instance, self._env['MOLECULE_PLATFORM'],
                    self._provisioner.instances))

        inventory_file = self._config.config['molecule']['inventory_file']
        try:
            utilities.write_file(inventory_file, inventory)
        except IOError:
            utilities.logger.warning(
                'WARNING: could not write inventory file {}'.format(
                    inventory_file))

    def _add_or_update_vars(self, target):
        """Creates or updates to host/group variables if needed."""

        if target in self._config.config['ansible']:
            vars_target = self._config.config['ansible'][target]
        else:
            return

        molecule_dir = self._config.config['molecule']['molecule_dir']
        target_vars_path = os.path.join(molecule_dir, target)

        if not os.path.exists(os.path.abspath(target_vars_path)):
            os.mkdir(os.path.abspath(target_vars_path))

        for target in vars_target.keys():
            target_var_content = vars_target[target][0]

            utilities.write_file(
                os.path.join(
                    os.path.abspath(target_vars_path), target),
                "---\n" + yaml.dump(target_var_content,
                                    default_flow_style=False))

    def _symlink_vars(self):
        """Creates or updates the symlink to group_vars if needed."""
        SYMLINK_NAME = 'group_vars'
        group_vars_target = self._config.config.get('molecule',
                                                    {}).get('group_vars')
        molecule_dir = self._config.config['molecule']['molecule_dir']
        group_vars_link_path = os.path.join(molecule_dir, SYMLINK_NAME)

        # Remove any previous symlink.
        if os.path.lexists(group_vars_link_path):
            try:
                os.unlink(group_vars_link_path)
            except:
                pass

        # Do not create the symlink if nothing is specified in the config.
        if not group_vars_target:
            return

        # Otherwise create the new symlink.
        symlink = os.path.join(
            os.path.abspath(molecule_dir), group_vars_target)
        if not os.path.exists(symlink):
            utilities.logger.error(
                'ERROR: the group_vars path {} does not exist. Check your configuration file'.format(
                    group_vars_target))

            sys.exit(1)
        os.symlink(group_vars_target, group_vars_link_path)

    def _display_tabulate_data(self, data, headers=None):
        """
        Shows the tabulate data on the screen.

        If not header is defined, only the data is displayed, otherwise, the results will be shown in a table.
        """
        # Nothing to display if there is no data.
        if not data:
            return

        # Initialize empty headers if none are provided.
        if not headers:
            headers = []

        # Define the table format based on the headers content.
        table_format = "fancy_grid" if headers else "plain"

        # Print the results.
        print(tabulate.tabulate(data, headers, tablefmt=table_format))

    def _remove_inventory_file(self):
        if os._exists(self._config.config['molecule']['inventory_file']):
            os.remove(self._config.config['molecule']['inventory_file'])

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
import fcntl
import os
import re
import struct
import sys
import termios

import tabulate
import yaml

from molecule import config
from molecule import state
from molecule import util
from molecule.driver import basedriver
from molecule.driver import dockerdriver
from molecule.driver import openstackdriver
from molecule.driver import proxmoxdriver
from molecule.driver import vagrantdriver

LOG = util.get_logger(__name__)


class Molecule(object):
    def __init__(self, args):
        self.env = os.environ.copy()
        self.args = args
        self.config = config.Config()

    def main(self):
        if not os.path.exists(self.config.config['molecule']['molecule_dir']):
            os.makedirs(self.config.config['molecule']['molecule_dir'])

        self._state = state.State(
            state_file=self.config.config.get('molecule').get('state_file'))

        try:
            self.driver = self._get_driver()
        except basedriver.InvalidDriverSpecified:
            LOG.error("Invalid provider '{}'".format(self.args['--provider']))
            self.args['--provider'] = None
            self.args['--platform'] = None
            self.driver = self._get_driver()
            self._print_valid_providers()
            util.sysexit()
        except basedriver.InvalidDriverSpecified:
            LOG.error("Invalid platform '{}'".format(self.args['--platform']))
            self.args['--provider'] = None
            self.args['--platform'] = None
            self.driver = self._get_driver()
            self._print_valid_platforms()
            util.sysexit()

        # updates instances config with full machine names
        self.config.populate_instance_names(self.driver.platform)

        if self.args.get('--debug'):
            util.debug('RUNNING CONFIG',
                       yaml.dump(self.config.config,
                                 default_flow_style=False,
                                 indent=2))

        self._add_or_update_vars('group_vars')
        self._add_or_update_vars('host_vars')

    @property
    def driver(self):
        return self._driver

    @driver.setter
    def driver(self, val):
        self._driver = val

    def _get_driver(self):
        if 'vagrant' in self.config.config:
            return vagrantdriver.VagrantDriver(self)
        elif 'proxmox' in self.config.config:
            return proxmoxdriver.ProxmoxDriver(self)
        elif 'docker' in self.config.config:
            return dockerdriver.DockerDriver(self)
        elif 'openstack' in self.config.config:
            return openstackdriver.OpenstackDriver(self)
        else:
            return None

    def _get_ssh_config(self):
        return self.driver.ssh_config_file

    def _write_ssh_config(self):
        ssh_config = self._get_ssh_config()
        if ssh_config is None:
            return
        out = self.driver.conf(ssh_config=True)
        util.write_file(ssh_config, out)

    def _print_valid_platforms(self, porcelain=False):
        if not porcelain:
            # NOTE(retr0h): Should we log here, when ``_display_tabulate_data``
            # prints?
            LOG.info("AVAILABLE PLATFORMS")

        data = []
        default_platform = self.driver.default_platform
        for platform in self.driver.valid_platforms:
            if porcelain:
                default = 'd' if platform['name'] == default_platform else ''
            else:
                default = ' (default)' if platform[
                    'name'] == default_platform else ''
            data.append([platform['name'], default])

        self._display_tabulate_data(data)

    def _print_valid_providers(self, porcelain=False):
        if not porcelain:
            # NOTE(retr0h): Should we log here, when ``_display_tabulate_data``
            # prints?
            LOG.info("AVAILABLE PROVIDERS")

        data = []
        default_provider = self.driver.default_provider
        for provider in self.driver.valid_providers:
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
        os.remove(self.config.config['molecule']['rakefile_file'])
        if self._state.customconf is False:
            os.remove(self.config.config['ansible']['config_file'])

    def _create_templates(self):
        """
        Creates the templates used by molecule.

        :return: None
        """
        # ansible.cfg
        kwargs = {'molecule_dir':
                  self.config.config['molecule']['molecule_dir']}
        if not os.path.isfile(self.config.config['ansible']['config_file']):
            util.write_template(
                self.config.config['molecule']['ansible_config_template'],
                self.config.config['ansible']['config_file'], kwargs=kwargs)
            self._state.change_state('customconf', False)
        else:
            self._state.change_state('customconf', True)

        # rakefile
        kwargs = {
            'state_file': self.config.config['molecule']['state_file'],
            'serverspec_dir': self.config.config['molecule']['serverspec_dir']
        }
        util.write_template(
            self.config.config['molecule']['rakefile_template'],
            self.config.config['molecule']['rakefile_file'], kwargs=kwargs)

    def _instances_state(self):
        """
        Creates a dict of formatted instances names and the group(s) they're
        part of to be added to state.

        :return: Dict containing state information about current instances
        """

        instances = collections.defaultdict(dict)
        for instance in self.driver.instances:
            instance_name = util.format_instance_name(
                instance['name'], self.driver._platform, self.driver.instances)

            if 'ansible_groups' in instance:
                instances[instance_name][
                    'groups'] = [x for x in instance['ansible_groups']]
            else:
                instances[instance_name]['groups'] = []

        return dict(instances)

    def _write_instances_state(self):
        self._state.change_state('hosts', self._instances_state())

    def _create_inventory_file(self):
        """
        Creates the inventory file used by molecule and later passed to
        ansible-playbook.

        :return: None
        """

        inventory = ''
        for instance in self.driver.instances:
            inventory += self.driver.inventory_entry(instance)

        # get a list of all groups and hosts in those groups
        groups = {}
        for instance in self.driver.instances:
            if 'ansible_groups' in instance:
                for group in instance['ansible_groups']:
                    if group not in groups:
                        groups[group] = []
                    groups[group].append(instance['name'])

        if self.args.get('--platform') == 'all':
            self.driver.platform = 'all'

        for group, instances in groups.iteritems():
            inventory += '\n[{}]\n'.format(group)
            for instance in instances:
                inventory += '{}\n'.format(util.format_instance_name(
                    instance, self.driver.platform, self.driver.instances))

        inventory_file = self.config.config['ansible']['inventory_file']
        try:
            util.write_file(inventory_file, inventory)
        except IOError:
            LOG.warning('WARNING: could not write inventory file {}'.format(
                inventory_file))

    def _remove_inventory_file(self):
        if os._exists(self.config.config['ansible']['inventory_file']):
            os.remove(self.config.config['ansible']['inventory_file'])

    def _add_or_update_vars(self, target):
        """Creates or updates to host/group variables if needed."""

        if target in self.config.config['ansible']:
            vars_target = self.config.config['ansible'][target]
        else:
            return

        molecule_dir = self.config.config['molecule']['molecule_dir']
        target_vars_path = os.path.join(molecule_dir, target)

        if not os.path.exists(os.path.abspath(target_vars_path)):
            os.mkdir(os.path.abspath(target_vars_path))

        for target in vars_target.keys():
            target_var_content = vars_target[target][0]

            util.write_file(
                os.path.join(
                    os.path.abspath(target_vars_path), target),
                "---\n" + yaml.dump(target_var_content,
                                    default_flow_style=False))

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

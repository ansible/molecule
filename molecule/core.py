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
import os

import tabulate
import yaml

from molecule import state
from molecule import util
from molecule.driver import basedriver

LOG = util.get_logger(__name__)


class Molecule(object):
    def __init__(self, config, args):
        """
        Initialize a new molecule class and returns None.

        :param config: A molecule config object.
        :param args: A dict of options, arguments and commands from the CLI.
        :returns: None
        """
        self.env = os.environ.copy()
        self.config = config
        self.args = args
        self._verifier = self._get_verifier()
        self._verifier_options = self._get_verifier_options()
        self._disabled = self._get_disabled()

    def main(self):
        if not os.path.exists(self.config.config['molecule']['molecule_dir']):
            os.makedirs(self.config.config['molecule']['molecule_dir'])

        self.state = state.State(
            state_file=self.config.config.get('molecule').get('state_file'))

        try:
            self.driver = self._get_driver()
        except basedriver.InvalidDriverSpecified:
            LOG.error("Invalid driver '{}'".format(self._get_driver_name()))
            # TODO(retr0h): Print valid drivers.
            util.sysexit()
        except basedriver.InvalidProviderSpecified:
            LOG.error("Invalid provider '{}'".format(self.args['provider']))
            self.args['provider'] = None
            self.args['platform'] = None
            self.driver = self._get_driver()
            self.print_valid_providers()
            util.sysexit()
        except basedriver.InvalidPlatformSpecified:
            LOG.error("Invalid platform '{}'".format(self.args['platform']))
            self.args['provider'] = None
            self.args['platform'] = None
            self.driver = self._get_driver()
            self.print_valid_platforms()
            util.sysexit()

        # updates instances config with full machine names
        self.config.populate_instance_names(self.driver.platform)

        if self.args.get('debug'):
            util.print_debug(
                'RUNNING CONFIG',
                yaml.dump(
                    self.config.config, default_flow_style=False, indent=2))

        self._add_or_update_vars('group_vars')
        self._add_or_update_vars('host_vars')

    @property
    def driver(self):
        return self._driver

    @driver.setter
    def driver(self, val):
        self._driver = val

    @property
    def verifier(self):
        return self._verifier

    @verifier.setter
    def verifier(self, val):
        self._verifier = val

    @property
    def verifier_options(self):
        return self._verifier_options

    @verifier_options.setter
    def verifier_options(self, val):
        self._verifier_options = val

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, val):
        self._disabled = val

    def write_ssh_config(self):
        ssh_config = self._get_ssh_config()
        if ssh_config is None:
            return
        out = self.driver.conf(ssh_config=True)
        util.write_file(ssh_config, out)

    def print_valid_platforms(self, porcelain=False):
        if not porcelain:
            # NOTE(retr0h): Should we log here, when ``display_tabulate_data``
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

        self.display_tabulate_data(data)

    def print_valid_providers(self, porcelain=False):
        if not porcelain:
            # NOTE(retr0h): Should we log here, when ``display_tabulate_data``
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

        self.display_tabulate_data(data)

    def remove_templates(self):
        """
        Removes the templates created by molecule and returns None.

        :return: None
        """
        if os.path.exists(self.config.config['molecule']['rakefile_file']):
            os.remove(self.config.config['molecule']['rakefile_file'])

        config = self.config.config['ansible']['config_file']
        if os.path.exists(config):
            with open(config, 'r') as stream:
                data = stream.read().splitlines()
                if '# Molecule managed' in data:
                    os.remove(config)

    def create_templates(self):
        """
        Creates the templates used by molecule and returns None.

        :return: None
        """
        molecule_dir = self.config.config['molecule']['molecule_dir']
        role_path = os.getcwd()
        extra_context = self._get_cookiecutter_context(molecule_dir)
        util.process_templates('molecule', extra_context, role_path)

    def write_instances_state(self):
        self.state.change_state('hosts', self._instances_state())

    def create_inventory_file(self):
        """
        Creates the inventory file used by molecule and returns None.

        :return: None
        """

        inventory = ''
        for instance in self.driver.instances:
            inventory += self.driver.inventory_entry(instance)

        groups = {}
        for instance in self.driver.instances:
            ansible_groups = instance.get('ansible_groups')
            if ansible_groups:
                for group in ansible_groups:
                    if isinstance(group, str):
                        if group not in groups:
                            groups[group] = []
                        groups[group].append(instance['name'])
                    elif isinstance(group, dict):
                        for group_name, group_list in group.iteritems():
                            for g in group_list:
                                if group_name not in groups:
                                    groups[group_name] = []
                                groups[group_name].append(g)

        if self.args.get('platform') == 'all':
            self.driver.platform = 'all'

        for group, subgroups in groups.iteritems():
            inventory += '\n[{}]\n'.format(group)
            for subgroup in subgroups:
                instance_name = util.format_instance_name(
                    subgroup, self.driver.platform, self.driver.instances)
                if instance_name:
                    inventory += '{}\n'.format(instance_name)
                else:
                    inventory += '{}\n'.format(subgroup)

        inventory_file = self.config.config['ansible']['inventory_file']
        try:
            util.write_file(inventory_file, inventory)
        except IOError:
            LOG.warning('WARNING: could not write inventory file {}'.format(
                inventory_file))

    def remove_inventory_file(self):
        if os._exists(self.config.config['ansible']['inventory_file']):
            os.remove(self.config.config['ansible']['inventory_file'])

    def display_tabulate_data(self, data, headers=None):
        """
        Shows the tabulate data on the screen and returns None.

        If not header is defined, only the data is displayed, otherwise, the
        results will be shown in a table.

        :param data:
        :param headers:
        :returns: None

        .. todo:: Document this method.
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

    def _get_driver_name(self):
        driver = self.args.get('driver')
        if driver:
            return driver
        elif self.config.config.get('driver'):
            return self.config.config['driver'].get('name')
        elif 'vagrant' in self.config.config:
            return 'vagrant'
        elif 'docker' in self.config.config:
            return 'docker'
        elif 'openstack' in self.config.config:
            return 'openstack'

    def _get_driver(self):
        """
        Return an instance of the driver as returned by `_get_driver_name()`.

        .. todo:: Implement a pluggable solution vs inline imports.
        """
        driver = self._get_driver_name()

        if (self.state.driver is not None) and (self.state.driver != driver):
            msg = ("ERROR: Instance(s) were converged with the '{}' driver, "
                   "but the subcommand is using '{}' driver.")
            LOG.error(msg.format(self.state.driver, driver))
            util.sysexit()

        if driver == 'vagrant':
            from molecule.driver import vagrantdriver
            return vagrantdriver.VagrantDriver(self)
        elif driver == 'docker':
            from molecule.driver import dockerdriver
            return dockerdriver.DockerDriver(self)
        elif driver == 'openstack':
            from molecule.driver import openstackdriver
            return openstackdriver.OpenstackDriver(self)
        raise basedriver.InvalidDriverSpecified()

    def _get_ssh_config(self):
        return self.driver.ssh_config_file

    def _add_or_update_vars(self, target):
        """
        Creates or updates to host/group variables if needed.

        :param target:
        :returns:

        .. todo:: Document this method.
        """

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
            path = os.path.join(os.path.abspath(target_vars_path), target)

            util.write_file(
                path,
                yaml.dump(
                    target_var_content,
                    default_flow_style=False,
                    explicit_start=True))

    def _instances_state(self):
        """
        Creates a dict of formatted instances names and the group(s) they're
        part of to be added to state and returns dict containing state
        information about current instances.

        :return: dict
        """

        instances = collections.defaultdict(dict)
        for instance in self.driver.instances:
            instance_name = util.format_instance_name(
                instance['name'], self.driver._platform, self.driver.instances)

            groups = set()
            ansible_groups = instance.get('ansible_groups')
            if ansible_groups:
                for group in ansible_groups:
                    if isinstance(group, str):
                        groups.add(group)
                    elif isinstance(group, dict):
                        for group_name, _ in group.iteritems():
                            groups.add(group_name.split(':')[0])

            instances[instance_name]['groups'] = sorted(list(groups))

        return dict(instances)

    def _get_verifier(self):
        if self.config.config.get('testinfra'):
            return 'testinfra'
        return self.config.config['verifier']['name']

    def _get_verifier_options(self):
        # Preserve backward compatibility with old testinfra override
        # syntax.
        return self.config.config.get(
            'testinfra', self.config.config['verifier'].get('options', {}))

    def _get_disabled(self):
        # Ability to turn off features until we roll them out.
        return self.config.config.get('_disabled', [])

    def _get_cookiecutter_context(self, molecule_dir):
        state_file = self.config.config['molecule']['state_file']
        serverspec_dir = self.config.config['molecule']['serverspec_dir']

        return {
            'repo_name': molecule_dir,
            'ansiblecfg_molecule_dir': molecule_dir,
            'ansiblecfg_ansible_library_path': 'library',
            'rakefile_state_file': state_file,
            'rakefile_serverspec_dir': serverspec_dir,
        }

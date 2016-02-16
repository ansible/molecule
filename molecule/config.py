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

import anyconfig

import molecule.utilities as utilities


class Config(object):
    CONFIG_PATHS = [os.environ.get('MOLECULE_CONFIG'), os.path.expanduser('~/.config/molecule/config.yml'),
                    '/etc/molecule/config.yml']
    DEFAULTS_FILE = os.path.join(os.path.dirname(__file__), 'conf/defaults.yml')

    def __init__(self, configs=CONFIG_PATHS):
        self.config = self._get_config(configs)
        self._build_easy_paths()
        self._update_ansible_defaults()

    def _get_first_config(self, configs):
        l = [f for f in configs if f and os.path.isfile(f)]
        if l:
            return l.pop(0)
        return l

    def _get_config(self, configs):
        """
        Loads a config from a file, and returns a dict.

        Only the first file that's found will be merged ontop of the next.

        :param configs: A list containing configs to load.
        :return: `type: dict`
        """
        c = self._get_first_config(configs)

        return anyconfig.load([c, self.DEFAULTS_FILE], ignore_missing=True)

    def _build_easy_paths(self):
        """
        Build paths from our config.

        :return: None
        """
        values_to_update = ['state_file', 'vagrantfile_file', 'rakefile_file', 'config_file', 'inventory_file']

        for item in values_to_update:
            self.config['molecule'][item] = os.path.join(self.config['molecule']['molecule_dir'],
                                                         self.config['molecule'][item])

    def _update_ansible_defaults(self):
        """
        Copies certain default values from molecule to ansible if none are specified in molecule.yml.

        :return: None
        """
        # grab inventory_file default from molecule if it's not set in the user-supplied ansible options
        if 'inventory_file' not in self.config['ansible']:
            self.config['ansible']['inventory_file'] = self.config['molecule']['inventory_file']

        # grab config_file default from molecule if it's not set in the user-supplied ansible options
        if 'config_file' not in self.config['ansible']:
            self.config['ansible']['config_file'] = self.config['molecule']['config_file']

    def _populate_instance_names(self, platform):
        """
        Updates instances section of config with an additional key containing the full instance name.

        :param platform: platform name to pass to underlying format_instance_name call.
        :return: None
        """
        # assume static inventory if there's no vagrant section
        if self.config.get('vagrant') is None:
            return

        # assume static inventory if no instances are listed
        if self.config['vagrant'].get('instances') is None:
            return

        for instance in self.config['vagrant']['instances']:
            instance['vm_name'] = utilities.format_instance_name(instance['name'], platform,
                                                                 self.config['vagrant']['instances'])

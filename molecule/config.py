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

import os
import os.path

import anyconfig

from molecule import utilities

DEFAULT_CONFIG = os.path.join(os.path.dirname(__file__), 'conf/defaults.yml')
PROJECT_CONFIG = 'molecule.yml'
LOCAL_CONFIG = '~/.config/molecule/config.yml'


class Config(object):
    def __init__(self, configs=[DEFAULT_CONFIG, PROJECT_CONFIG, LOCAL_CONFIG]):
        self.config = self._get_config(configs)

    @property
    def molecule_file(self):
        return PROJECT_CONFIG

    def build_easy_paths(self):
        """
        Convenience function to build up paths from our config values

        :return: None
        """
        values_to_update = ['state_file', 'vagrantfile_file', 'rakefile_file',
                            'config_file', 'inventory_file']

        for item in values_to_update:
            self.config['molecule'][item] = os.path.join(
                self.config['molecule']['molecule_dir'],
                self.config['molecule'][item])

    def update_ansible_defaults(self):
        """
        Copies certain default values from molecule to ansible if none are specified in molecule.yml

        :return: None
        """
        # grab inventory_file default from molecule if it's not set in the user-supplied ansible options
        if 'inventory_file' not in self.config['ansible']:
            self.config['ansible']['inventory_file'] = self.config['molecule'][
                'inventory_file']

        # grab config_file default from molecule if it's not set in the user-supplied ansible options
        if 'config_file' not in self.config['ansible']:
            self.config['ansible']['config_file'] = self.config['molecule'][
                'config_file']

    def populate_instance_names(self, platform):
        """
        Updates instances section of config with an additional key containing the full instance name

        :param platform: platform name to pass to underlying format_instance_name call
        :return: None
        """
        for instance in self.config['vagrant']['instances']:
            instance['vm_name'] = utilities.format_instance_name(
                instance['name'], platform,
                self.config['vagrant']['instances'])

    def molecule_file_exists(self):
        return os.path.isfile(self.molecule_file)

    def _get_config(self, configs):
        return self._combine(configs)

    def _combine(self, configs):
        """ Perform a prioritized recursive merge of serveral source files,
        and return a new dict.

        The merge order is based on the index of the list, meaning that elements
        at the end of the list will be merged last, and have greater precedence
        than elements at the beginning.

        :param configs: A list containing the yaml files to load.
        :return: dict
        """

        return anyconfig.load(configs,
                              ignore_missing=True,
                              ac_merge=anyconfig.MS_DICTS_AND_LISTS)

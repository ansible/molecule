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

from __future__ import print_function

import os
import sys

import colorama
import yaml

import molecule.utilities as utilities


class Config(object):
    # locations to look for molecule config files
    CONFIG_PATHS = [os.environ.get('MOLECULE_CONFIG'),
                    os.path.expanduser('~/.config/molecule/config.yml'),
                    '/etc/molecule/config.yml']

    def load_defaults_file(self, defaults_file=None):
        """
        Loads config from a file

        :param defaults_file: optional YAML file to open and read defaults from
        :return: None
        """
        # load defaults from provided file
        if defaults_file is None:
            defaults_file = os.path.join(
                os.path.dirname(__file__), 'conf/defaults.yml')

        with open(defaults_file, 'r') as stream:
            self.config = yaml.safe_load(stream)

    def merge_molecule_config_files(self, paths=CONFIG_PATHS):
        """
        Looks for a molecule config file in paths and merges it with current config if found

        Only the first file that's found will be merged in.
        :param paths: list of places to look for config files
        :return: Path of file that was merged into config, if found, otherwise None
        """
        # merge defaults with a config file if found
        for path in paths:
            if path and os.path.isfile(path):
                with open(path, 'r') as stream:
                    self.config = utilities.merge_dicts(self.config,
                                                        yaml.safe_load(stream))
                    return path
        return

    def merge_molecule_file(self, molecule_file=None):
        """
        Looks for a molecule file in the local path and merges it into our config

        :param molecule_file: path and name of molecule file to look for
        :return: None
        """
        if molecule_file is None:
            molecule_file = self.config['molecule']['molecule_file']

        if not os.path.isfile(molecule_file):
            error = '\n{}Unable to find {}. Exiting.{}'
            print(error.format(colorama.Fore.RED, self.config['molecule'][
                'molecule_file'], colorama.Fore.RESET))
            sys.exit(1)

        with open(molecule_file, 'r') as env:
            try:
                molecule_yml = yaml.safe_load(env)
            except Exception as e:
                error = "\n{}{} isn't properly formatted: {}{}"
                print(error.format(colorama.Fore.RED, molecule_file, e,
                                   colorama.Fore.RESET))
                sys.exit(1)

            interim = utilities.merge_dicts(self.config, molecule_yml)
            self.config = interim

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
        # assume static inventory if there's no vagrant section
        if self.config.get('vagrant') is None:
            return

        # assume static inventory if no instances are listed
        if self.config['vagrant'].get('instances') is None:
            return

        for instance in self.config['vagrant']['instances']:
            instance['vm_name'] = utilities.format_instance_name(
                instance['name'], platform,
                self.config['vagrant']['instances'])

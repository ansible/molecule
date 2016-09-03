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

import os
import os.path

import anyconfig

from molecule import util

DEFAULT_CONFIG = os.path.join(os.path.dirname(__file__), 'conf/defaults.yml')
PROJECT_CONFIG = 'molecule.yml'
LOCAL_CONFIG = '~/.config/molecule/config.yml'


class Config(object):
    def __init__(self, configs=[DEFAULT_CONFIG, LOCAL_CONFIG, PROJECT_CONFIG]):
        """
        Initialize a new config class, and returns None.

        :param command_args: A list configs files to merge.
        :returns: None
        """
        self.config = self._get_config(configs)
        self._build_config_paths()

    @property
    def molecule_file(self):
        return PROJECT_CONFIG

    def populate_instance_names(self, platform):
        """
        Updates instances section of config with an additional key containing
        the full instance name

        :param platform: platform name to pass to ``format_instance_name`` call
        :return: None
        """

        if 'vagrant' in self.config:
            for instance in self.config['vagrant']['instances']:
                instance['vm_name'] = util.format_instance_name(
                    instance['name'], platform,
                    self.config['vagrant']['instances'])

    def molecule_file_exists(self):
        return os.path.isfile(self.molecule_file)

    def _get_config(self, configs):
        return self._combine(configs)

    def _combine(self, configs):
        """ Perform a prioritized recursive merge of serveral source files,
        and returns a new dict.

        The merge order is based on the index of the list, meaning that
        elements at the end of the list will be merged last, and have greater
        precedence than elements at the beginning.

        :param configs: A list containing the yaml files to load.
        :return: dict
        """

        return anyconfig.load(
            configs, ignore_missing=True, ac_merge=anyconfig.MS_DICTS)

    def _build_config_paths(self):
        """
        Convenience function to build up paths from our config values.  Path
        will not be relative to ``molecule_dir``, when a full path was provided
        in the config.

        :return: None
        """
        md = self.config.get('molecule')
        ad = self.config.get('ansible')
        for item in ['state_file', 'vagrantfile_file', 'rakefile_file']:
            if md and not self._is_path(md[item]):
                md[item] = os.path.join(md['molecule_dir'], md[item])

        for item in ['config_file', 'inventory_file']:
            if ad and not self._is_path(ad[item]):
                ad[item] = os.path.join(md['molecule_dir'], ad[item])

    def _is_path(self, pathname):
        return os.path.sep in pathname

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

import abc
import os
import os.path

import anyconfig
import m9dicts

from molecule import util

PROJECT_CONFIG = 'molecule.yml'
LOCAL_CONFIG = '~/.config/molecule/config.yml'
MERGE_STRATEGY = anyconfig.MS_DICTS


class Config(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, configs=[LOCAL_CONFIG, PROJECT_CONFIG]):
        """
        Base initializer for all Config classes.

        :param command_args: A list configs files to merge.
        :returns: None
        """
        self.config = self._get_config(configs)

    @property
    def molecule_file(self):
        return PROJECT_CONFIG

    @abc.abstractmethod
    def _get_config(self, configs):
        pass  # pragma: no cover


class ConfigV1(Config):
    def __init__(self, configs=[LOCAL_CONFIG, PROJECT_CONFIG]):
        """
        Initialize a new config version one class and returns None.
        """
        super(ConfigV1, self).__init__(configs)
        self._build_config_paths()

    def molecule_file_exists(self):
        return os.path.isfile(self.molecule_file)

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

    def _get_config(self, configs):
        return self._combine(configs)

    def _combine(self, configs):
        """ Perform a prioritized recursive merge of serveral source files
        and returns a new dict.

        The merge order is based on the index of the list, meaning that
        elements at the end of the list will be merged last, and have greater
        precedence than elements at the beginning.  The result is then merged
        ontop of the defaults.

        :param configs: A list containing the yaml files to load.
        :return: dict
        """

        default = self._get_defaults()
        conf = anyconfig.to_container(default, ac_merge=MERGE_STRATEGY)
        conf.update(
            anyconfig.load(
                configs, ignore_missing=True, ac_merge=MERGE_STRATEGY))

        return m9dicts.convert_to(conf)

    def _get_defaults(self):
        return {
            'ansible': {
                'ask_sudo_pass': False,
                'ask_vault_pass': False,
                'config_file': 'ansible.cfg',
                'ansiblecfg_defaults': {},
                'diff': True,
                'host_key_checking': False,
                'inventory_file': 'ansible_inventory',
                'limit': 'all',
                'playbook': 'playbook.yml',
                'raw_ssh_args': [
                    '-o UserKnownHostsFile=/dev/null', '-o IdentitiesOnly=yes',
                    '-o ControlMaster=auto', '-o ControlPersist=60s'
                ],
                'sudo': True,
                'sudo_user': False,
                'tags': False,
                'timeout': 30,
                'vault_password_file': False,
                'verbose': False
            },
            'molecule': {
                'goss_dir': 'tests',
                'goss_playbook': 'test_default.yml',
                'ignore_paths': ['.git', '.vagrant', '.molecule'],
                'init': {
                    'platform': {
                        'box': 'trusty64',
                        'box_url':
                        ('https://vagrantcloud.com/ubuntu/boxes/trusty64/'
                         'versions/14.04/providers/virtualbox.box'),
                        'box_version': '0.1.0',
                        'name': 'trusty64'
                    },
                    'provider': {
                        'name': 'virtualbox',
                        'type': 'virtualbox'
                    }
                },
                'molecule_dir': '.molecule',
                'rakefile_file': 'rakefile',
                'raw_ssh_args': [
                    '-o StrictHostKeyChecking=no',
                    '-o UserKnownHostsFile=/dev/null'
                ],
                'serverspec_dir': 'spec',
                'state_file': 'state.yml',
                'test': {
                    'sequence': [
                        'destroy', 'dependency', 'syntax', 'create',
                        'converge', 'idempotence', 'verify'
                    ]
                },
                'testinfra_dir': 'tests',
                'vagrantfile_file': 'vagrantfile',
                'vagrantfile_template': 'vagrantfile.j2'
            },
            'verifier': {
                'name': 'testinfra',
                'options': {}
            },
            'dependency': {
                'name': 'galaxy',
                'options': {}
            },
            '_disabled': [],
        }

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


def merge_dicts(a, b):
    """
    Merges the values of B into A and returns a new dict.  Uses the same merge
    strategy as ``config._combine``.

    ::

        dict a

        b:
           - c: 0
           - c: 2
        d:
           e: "aaa"
           f: 3

        dict b

        a: 1
        b:
           - c: 3
        d:
           e: "bbb"

    Will give an object such as::

        {'a': 1, 'b': [{'c': 3}], 'd': {'e': "bbb", 'f': 3}}


    :param a: the target dictionary
    :param b: the dictionary to import
    :return: dict
    """
    conf = anyconfig.to_container(a, ac_merge=MERGE_STRATEGY)
    conf.update(b)

    return conf

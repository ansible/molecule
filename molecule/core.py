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

import sh
import vagrant
import yaml
from colorama import Fore

import molecule.config as config
import molecule.utilities as utilities


class Molecule(object):
    def __init__(self, args):
        self._created = False
        self._provisioned = False
        self._provider = None
        self._env = os.environ.copy()
        self._args = args
        self._config = config.Config()

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

        if not os.path.exists(self._config.config['molecule']['molecule_dir']):
            os.makedirs(self._config.config['molecule']['molecule_dir'])

        self._vagrant = vagrant.Vagrant(quiet_stdout=False, quiet_stderr=False)

        self._env['VAGRANT_VAGRANTFILE'] = self._config.config['molecule']['vagrantfile_file']

        if self._args['--tags']:
            self._env['MOLECULE_TAGS'] = self._args['--tags']

        if self._args['--provider']:
            if not [item
                    for item in self._config.config['vagrant']['providers']
                    if item['name'] == self._args['--provider']]:
                print("\n{}Invalid provider '{}'\n".format(Fore.RED, self._args['--provider'], Fore.RESET))
                self._print_valid_providers()
                sys.exit(1)
            self._set_default_provider(provider=self._args['--provider'])
            self._env['VAGRANT_DEFAULT_PROVIDER'] = self._args['--provider']
            self._provider = self._env['VAGRANT_DEFAULT_PROVIDER']
        else:
            self._env['VAGRANT_DEFAULT_PROVIDER'] = self._get_default_provider()
            self._provider = self._env['VAGRANT_DEFAULT_PROVIDER']

        if self._args['--platform']:
            if not [item
                    for item in self._config.config['vagrant']['platforms']
                    if item['name'] == self._args['--platform']]:
                print("\n{}Invalid platform '{}'\n".format(Fore.RED, self._args['--platform'], Fore.RESET))
                self._print_valid_platforms()
                sys.exit(1)
            self._set_default_platform(platform=self._args['--platform'])
            self._env['MOLECULE_PLATFORM'] = self._args['--platform']
        else:
            self._env['MOLECULE_PLATFORM'] = self._get_default_platform()

        self._vagrant.env = self._env

        # updates instances config with full machine names
        self._config.populate_instance_names(self._env['MOLECULE_PLATFORM'])
        if self._args['--debug']:
            print yaml.dump(self._config.config, indent=4)

    def _rubocop(self):
        try:
            pattern = self._config.config['molecule']['serverspec_dir'] + '/**/*.rb'
            output = sh.rubocop(pattern, _env=self._env, _out=utilities.print_stdout, _err=utilities.print_stderr)
            return output.exit_code
        except sh.ErrorReturnCode as e:
            print('ERROR: {}'.format(e))
            sys.exit(e.exit_code)

    def _load_state_file(self):
        if not os.path.isfile(self._config.config['molecule']['state_file']):
            return False

        with open(self._config.config['molecule']['state_file'], 'r') as env:
            self._state = yaml.safe_load(env)
            return True

    def _write_state_file(self):
        utilities.write_file(self._config.config['molecule']['state_file'],
                             yaml.dump(self._state,
                                       default_flow_style=False))

    def _write_ssh_config(self):
        try:
            out = self._vagrant.ssh_config()
            ssh_config = self._get_vagrant_ssh_config()
        except CalledProcessError as e:
            print('ERROR: {}'.format(e))
            print("Does your vagrant VM exist?")
            sys.exit(e.returncode)
        utilities.write_file(ssh_config, out)

    def _get_vagrant_ssh_config(self):
        return '.vagrant/ssh-config'

    def _get_default_platform(self):
        default_platform = self._config.config['vagrant']['platforms'][0]['name']

        if not (self._load_state_file()):
            return default_platform

        # default to first entry if no entry for platform exists
        if 'default_platform' not in self._state:
            return default_platform

        # key exists but is falsy
        if not self._state['default_platform']:
            return default_platform

        return self._state['default_platform']

    def _set_default_platform(self, platform=False):
        if not hasattr(self, '_state'):
            if not self._load_state_file():
                self._state = {}

        self._state['default_platform'] = platform
        self._write_state_file()

    def _print_valid_platforms(self):
        print(Fore.CYAN + "AVAILABLE PLATFORMS" + Fore.RESET)
        default_platform = self._get_default_platform()
        for platform in self._config.config['vagrant']['platforms']:
            default = ' (default)' if platform['name'] == default_platform else ''
            print(platform['name'] + default)

    def _get_default_provider(self):
        default_provider = self._config.config['vagrant']['providers'][0]['name']

        if not (self._load_state_file()):
            return default_provider

        # default to first entry if no entry for provider exists
        if 'default_provider' not in self._state:
            return default_provider

        # key exists but is falsy
        if not self._state['default_provider']:
            return default_provider

        return self._state['default_provider']

    def _set_default_provider(self, provider=False):
        if not hasattr(self, '_state'):
            if not self._load_state_file():
                self._state = {}

        self._state['default_provider'] = provider
        self._write_state_file()

    def _print_valid_providers(self):
        print(Fore.CYAN + "AVAILABLE PROVIDERS" + Fore.RESET)
        default_provider = self._get_default_provider()
        for provider in self._config.config['vagrant']['providers']:
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

        if changed:
            return False

        return True

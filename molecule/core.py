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
import pexpect
import re
import signal
import struct
import sys
import termios
from subprocess import CalledProcessError

import prettytable
import sh
import vagrant
import yaml
from colorama import Fore
from jinja2 import Environment
from jinja2 import PackageLoader

import molecule.utilities as utilities
import molecule.validators as validators
import molecule.config as config


class Molecule(object):
    def __init__(self, args):
        self._created = False
        self._provisioned = False
        self._env = os.environ.copy()
        self._args = args
        self._config = config.Config()
        self._main()

    def _main(self):
        # load molecule defaults
        self._config.load_defaults_file()

        # merge in any molecule config files found (eg: ~/.configs/molecule/config.yml)
        self._config.merge_molecule_config_files()

        # init command doesn't need to load molecule.yml
        if self._args['init']:
            self.init()  # exits program

        # merge in molecule.yml
        self._config.merge_molecule_file()

        # concatentate file names and paths within config so they're more convenient to use
        self._config.build_easy_paths()

        if not os.path.exists(self._config.config['molecule']['molecule_dir']):
            os.makedirs(self._config.config['molecule']['molecule_dir'])

        self._vagrant = vagrant.Vagrant(quiet_stdout=False, quiet_stderr=False)

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
        else:
            self._env['VAGRANT_DEFAULT_PROVIDER'] = self._get_default_provider()

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
            self._state = yaml.load(env)
            return True

    def _write_state_file(self):
        utilities.write_file(self._config.config['molecule']['state_file'], yaml.dump(self._state, default_flow_style=False))

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
        print(Fore.CYAN + "AVAILABLE PLATFORMS" + Fore.RESET)
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

    def _destroy(self):
        try:
            self._vagrant.halt()
            self._vagrant.destroy()
            self._set_default_platform(platform=False)
        except CalledProcessError as e:
            print('ERROR: {}'.format(e))
            sys.exit(e.returncode)

    def _create(self):
        if not self._created:
            try:
                self._vagrant.up(no_provision=True)
                self._created = True
            except CalledProcessError as e:
                print('ERROR: {}'.format(e))
                sys.exit(e.returncode)

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

    def _verify(self):
        validators.check_trailing_cruft(ignore_paths=self._config.config['molecule']['ignore_paths'])

        # no tests found
        if not os.path.isdir(self._config.config['molecule']['serverspec_dir']) and not os.path.isdir(self._config.config['molecule'][
                'testinfra_dir']):
            msg = '{}Skipping tests, could not find {}/ or {}/.{}'
            print(msg.format(Fore.YELLOW, self._config.config['molecule']['serverspec_dir'], self._config.config['molecule']['testinfra_dir'],
                             Fore.RESET))
            return

        self._write_ssh_config()
        kwargs = {'_env': self._env, '_out': utilities.print_stdout, '_err': utilities.print_stderr}
        args = []

        # testinfra
        if os.path.isdir(self._config.config['molecule']['testinfra_dir']):
            ssh_config = '--ssh-config={}'.format(self._get_vagrant_ssh_config())
            try:
                output = sh.testinfra(ssh_config, '--sudo', self._config.config['molecule']['testinfra_dir'], **kwargs)
                return output.exit_code
            except sh.ErrorReturnCode as e:
                print('ERROR: {}'.format(e))
                sys.exit(e.exit_code)

        # serverspec
        if os.path.isdir(self._config.config['molecule']['serverspec_dir']):
            self._rubocop()
            if 'rakefile_file' in self._config.config['molecule']:
                kwargs['rakefile'] = self._config.config['molecule']['rakefile_file']
            if self._args['--debug']:
                args.append('--trace')
            try:
                rakecmd = sh.Command("rake")
                output = rakecmd(*args, **kwargs)
                return output.exit_code
            except sh.ErrorReturnCode as e:
                print('ERROR: {}'.format(e))
                sys.exit(e.exit_code)

    def test(self):
        for task in self._config.config['molecule']['test']['sequence']:
            m = getattr(self, task)
            m()

    def list(self):
        print
        self._print_valid_platforms()

    def status(self):
        try:
            status = self._vagrant.status()
        except CalledProcessError as e:
            print('ERROR: {}'.format(e))
            return e.returncode

        x = prettytable.PrettyTable(['Name', 'State', 'Provider'])
        x.align = 'l'

        for item in status:
            if item.state != 'not_created':
                state = Fore.GREEN + item.state + Fore.RESET
            else:
                state = item.state

            x.add_row([item.name, state, item.provider])

        print(x)
        print
        self._print_valid_platforms()

    def login(self):
        # make sure host argument is specified
        host_format = [Fore.RED, self._args['<host>'], Fore.RESET, Fore.YELLOW, Fore.RESET]
        host_errmsg = '\nTry molecule {}molecule status{} to see available hosts.\n'.format(*host_format)
        if not self._args['<host>']:
            print('You must specify a host when using login')
            print(host_errmsg)
            sys.exit(1)

        # make sure vagrant knows about this host
        try:
            conf = self._vagrant.conf(vm_name=self._args['<host>'])
            ssh_args = [conf['HostName'], conf['User'], conf['Port'], conf['IdentityFile'],
                        ' '.join(self._config.config['molecule']['raw_ssh_args'])]
            ssh_cmd = 'ssh {} -l {} -p {} -i {} {}'
        except CalledProcessError:
            # gets appended to python-vagrant's error message
            conf_format = [Fore.RED, self._args['<host>'], Fore.RESET, Fore.YELLOW, Fore.RESET]
            print('\nTry molecule {}molecule status{} to see available hosts.\n'.format(*conf_format))
            sys.exit(1)

        lines, columns = os.popen('stty size', 'r').read().split()
        dimensions = (int(lines), int(columns))
        self._pt = pexpect.spawn('/usr/bin/env ' + ssh_cmd.format(*ssh_args), dimensions=dimensions)
        signal.signal(signal.SIGWINCH, self._sigwinch_passthrough)
        self._pt.interact()

    def init(self):
        role = self._args['<role>']
        role_path = './' + role + '/'

        if not role:
            msg = '{}The init command requires a role name. Try:\n\n{}{} init <role>{}'
            print(msg.format(Fore.RED, Fore.YELLOW, os.path.basename(sys.argv[0]), Fore.RESET))
            sys.exit(1)

        if os.path.isdir(role):
            msg = '{}The directory {} already exists. Cannot create new role.{}'
            print(msg.format(Fore.RED, role_path, Fore.RESET))
            sys.exit(1)

        try:
            sh.ansible_galaxy('init', role)
        except (CalledProcessError, sh.ErrorReturnCode_1) as e:
            print('ERROR: {}'.format(e))
            sys.exit(e.returncode)

        env = Environment(loader=PackageLoader('molecule', 'templates'), keep_trailing_newline=True)

        t_molecule = env.get_template(self._config.config['molecule']['init']['templates']['molecule'])
        t_playbook = env.get_template(self._config.config['molecule']['init']['templates']['playbook'])
        t_default_spec = env.get_template(self._config.config['molecule']['init']['templates']['default_spec'])
        t_spec_helper = env.get_template(self._config.config['molecule']['init']['templates']['spec_helper'])

        with open(role_path + self._config.config['molecule']['molecule_file'], 'w') as f:
            f.write(t_molecule.render(config=self._config.config))

        with open(role_path + self._config.config['ansible']['playbook'], 'w') as f:
            f.write(t_playbook.render(role=role))

        serverspec_path = role_path + self._config.config['molecule']['serverspec_dir'] + '/'
        os.makedirs(serverspec_path)
        os.makedirs(serverspec_path + 'hosts')
        os.makedirs(serverspec_path + 'groups')

        with open(serverspec_path + 'default_spec.rb', 'w') as f:
            f.write(t_default_spec.render())

        with open(serverspec_path + 'spec_helper.rb', 'w') as f:
            f.write(t_spec_helper.render())

        msg = '{}Successfully initialized new role in {}{}'
        print(msg.format(Fore.GREEN, role_path, Fore.RESET))
        sys.exit(0)

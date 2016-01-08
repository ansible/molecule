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
import pexpect
import re
import signal
import sys
from subprocess import CalledProcessError

import prettytable
import sh
import yaml
from colorama import Fore
from jinja2 import Environment
from jinja2 import PackageLoader

import molecule.utilities as utilities
import molecule.validators as validators
from molecule.core import Molecule


class AbstractCommand:
    def __init__(self, args, molecule=False):
        """
        Initialize commands

        :param args: arguments from the CLI
        :param molecule: molecule instance
        """
        self.args = args
        self.static = False

        # only create a molecule instance if one doesn't exist
        if not molecule:
            self.molecule = Molecule(self.args)
            self.molecule.main()
        else:
            self.molecule = molecule

        # assume static inventory if no vagrant config block is defined
        if self.molecule._provisioner is None:
            self.static = True

        # assume static inventory if no instances are defined in vagrant config block
        if self.molecule._provisioner.instances is None:
            self.static = True

    def disabled(self, cmd):
        """
        Prints 'command disabled' message and exits program.

        :param cmd: Name of the disabled command to print.
        :return: None
        """
        fmt = [Fore.RED, cmd, Fore.RESET]
        errmsg = "{}The `{}` command isn't supported with static inventory.{}"
        print(errmsg.format(*fmt))
        sys.exit(1)

    def execute(self):
        raise NotImplementedError


class Create(AbstractCommand):
    def execute(self):
        """
        Creates all instances defined in molecule.yml.
        Creates all template files used by molecule, vagrant, ansible-playbook.

        :return: None
        """
        if self.static:
            self.disabled('create')

        self.molecule._create_templates()
        try:
            self.molecule._provisioner.up(no_provision=True)
            self.molecule._state['created'] = True
            self.molecule._write_state_file()
        except CalledProcessError as e:
            print('ERROR: {}'.format(e))
            sys.exit(e.returncode)


class Destroy(AbstractCommand):
    def execute(self):
        """
        Halts and destroys all instances created by molecule.
        Removes template files.
        Clears state file of all info (default platform).

        :return: None
        """
        if self.static:
            self.disabled('destroy')

        self.molecule._create_templates()
        try:
            self.molecule._provisioner.halt()
            self.molecule._provisioner.destroy()
            self.molecule._state['default_platform'] = False
            self.molecule._state['default_provider'] = False
            self.molecule._state['created'] = False
            self.molecule._state['converged'] = False
            self.molecule._write_state_file()
        except CalledProcessError as e:
            print('ERROR: {}'.format(e))
            sys.exit(e.returncode)
        self.molecule._remove_templates()


class Converge(AbstractCommand):
    def execute(self, idempotent=False, create_instances=True, create_inventory=True):
        """
        Provisions all instances using ansible-playbook.

        :param idempotent: Optionally provision servers quietly so output can be parsed for idempotence
        :param create_inventory: Toggle inventory creation
        :param create_instances: Toggle instance creation
        :return: Provisioning output
        """

        if self.molecule._state.get('created'):
            create_instances = False

        if self.molecule._state.get('converged'):
            create_inventory = False

        if self.static:
            create_instances = False
            create_inventory = False

        if create_instances and not idempotent:
            c = Create(self.args, self.molecule)
            c.execute()

        if create_inventory:
            self.molecule._create_inventory_file()

        playbook, args, kwargs = self.molecule._create_playbook_args()

        if idempotent:
            kwargs.pop('_out', None)
            kwargs.pop('_err', None)
            kwargs['_env']['ANSIBLE_NOCOLOR'] = 'true'
            kwargs['_env']['ANSIBLE_FORCE_COLOR'] = 'false'

            # Save the previous callback plugin if any.
            callback_plugin = kwargs.get('_env', {}).get('ANSIBLE_CALLBACK_PLUGINS', '')

            # Set the idempotence plugin.
            if callback_plugin:
                kwargs['_env']['ANSIBLE_CALLBACK_PLUGINS'] = callback_plugin + ':' + os.path.join(
                    sys.prefix, 'share/molecule/ansible/plugins/callback/idempotence')
            else:
                kwargs['_env']['ANSIBLE_CALLBACK_PLUGINS'] = os.path.join(
                    sys.prefix, 'share/molecule/ansible/plugins/callback/idempotence')

        try:
            ansible = sh.ansible_playbook.bake(playbook, *args, **kwargs)
            if self.molecule._args['--debug']:
                ansible_env = {k: v for (k, v) in kwargs['_env'].items() if 'ANSIBLE' in k}
                other_env = {k: v for (k, v) in kwargs['_env'].items() if 'ANSIBLE' not in k}
                utilities.debug('OTHER ENVIRONMENT', yaml.dump(other_env, default_flow_style=False, indent=2))
                utilities.debug('ANSIBLE ENVIRONMENT', yaml.dump(ansible_env, default_flow_style=False, indent=2))
                utilities.debug('ANSIBLE PLAYBOOK', str(ansible))

            output = ansible()

            if not self.molecule._state.get('converged'):
                self.molecule._state['converged'] = True
                self.molecule._write_state_file()

            if idempotent:
                # Reset the callback plugin to the previous value.
                kwargs['_env']['ANSIBLE_CALLBACK_PLUGINS'] = callback_plugin

            return output
        except sh.ErrorReturnCode as e:
            print('ERROR: {}'.format(e))
            sys.exit(e.exit_code)


class Idempotence(AbstractCommand):
    def execute(self):
        """
        Provisions instances and parses output to determine idempotence

        :return: None
        """
        if self.static:
            self.disabled('idempotence')

        print('{}Idempotence test in progress (can take a few minutes)...{}'.format(Fore.CYAN, Fore.RESET))

        c = Converge(self.args, self.molecule)
        output = c.execute(idempotent=True)
        idempotent, changed_tasks = self.molecule._parse_provisioning_output(output.stdout)

        if idempotent:
            print('{}Idempotence test passed.{}'.format(Fore.GREEN, Fore.RESET))
            return

        # Display the details of the idempotence test.
        if changed_tasks:
            print('{}Idempotence test failed because of the following tasks:{}'.format(Fore.RED, Fore.RESET))
            print('{}{}{}'.format(Fore.RED, '\n'.join(changed_tasks), Fore.RESET))
        else:
            # But in case the idempotence callback plugin was not found, we just display an error message.
            print('{}Idempotence test failed.{}'.format(Fore.RED, Fore.RESET))
            warning_msg = "The idempotence plugin was not found or did not provide the required information. " \
                "Therefore the failure details cannot be displayed."

            print('{}{}{}'.format(Fore.YELLOW, warning_msg, Fore.RESET))
        sys.exit(1)


class Verify(AbstractCommand):
    def execute(self):
        """
        Performs verification steps on running instances.
        Checks files for trailing whitespace and newlines.
        Runs testinfra against instances.
        Runs serverspec against instances (also calls rubocop on spec files).

        :return: None if no tests are found, otherwise return code of underlying command
        """
        if self.static:
            self.disabled('verify')

        validators.check_trailing_cruft(ignore_paths=self.molecule._config.config['molecule']['ignore_paths'])

        # no tests found
        if not os.path.isdir(self.molecule._config.config['molecule']['serverspec_dir']) and not os.path.isdir(
                self.molecule._config.config['molecule'][
                    'testinfra_dir']):
            msg = '{}Skipping tests, could not find {}/ or {}/.{}'
            print(msg.format(Fore.YELLOW, self.molecule._config.config['molecule']['serverspec_dir'],
                             self.molecule._config.config[
                                 'molecule']['testinfra_dir'], Fore.RESET))
            return

        self.molecule._write_ssh_config()
        kwargs = {'_env': self.molecule._env, '_out': utilities.print_stdout, '_err': utilities.print_stderr}
        kwargs['_env']['PYTHONDONTWRITEBYTECODE'] = '1'
        args = []

        # testinfra
        if os.path.isdir(self.molecule._config.config['molecule']['testinfra_dir']):
            try:
                ti_args = [
                    '--sudo', '--connection=ansible',
                    '--ansible-inventory=' + self.molecule._config.config['ansible']['inventory_file']
                ]
                output = sh.testinfra(*ti_args, **kwargs)
                return output.exit_code
            except sh.ErrorReturnCode as e:
                print('ERROR: {}'.format(e))
                sys.exit(e.exit_code)

        # serverspec
        if os.path.isdir(self.molecule._config.config['molecule']['serverspec_dir']):
            validators.rubocop(self.molecule._config.config['molecule']['serverspec_dir'], self.molecule._env)
            if 'rakefile_file' in self.molecule._config.config['molecule']:
                kwargs['rakefile'] = self.molecule._config.config['molecule']['rakefile_file']
            if self.molecule._args['--debug']:
                args.append('--trace')
            try:
                rakecmd = sh.Command("rake")
                output = rakecmd(*args, **kwargs)
                return output.exit_code
            except sh.ErrorReturnCode as e:
                print('ERROR: {}'.format(e))
                sys.exit(e.exit_code)


class Test(AbstractCommand):
    def execute(self):
        """
        Runs a series of commands (defined in config) against instances for a full test/verify run

        :return: None
        """
        if self.static:
            self.disabled('test')

        for task in self.molecule._config.config['molecule']['test']['sequence']:
            command = getattr(sys.modules[__name__], task.capitalize())
            c = command(self.args, self.molecule)
            c.execute()


class List(AbstractCommand):
    def execute(self):
        """
        Prints a list of currently available platforms

        :return: None
        """
        if self.static:
            self.disabled('list')

        is_machine_readable = self.molecule._args['-m']
        self.molecule._print_valid_platforms(machine_readable=is_machine_readable)


class Status(AbstractCommand):
    def execute(self):
        """
        Prints status of currently converged instances, similar to `vagrant status`

        :return: Return code of underlying command if there's an exception, otherwise None
        """
        if self.static:
            self.disabled('status')

        if not self.molecule._state.get('created'):
            errmsg = '{}ERROR: No instances created. Try `{} create` first.{}'
            print(errmsg.format(Fore.RED, os.path.basename(sys.argv[0]), Fore.RESET))
            sys.exit(1)

        try:
            status = self.molecule._provisioner.status()
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
        self.molecule._print_valid_platforms()
        self.molecule._print_valid_providers()


class Login(AbstractCommand):
    def execute(self):
        """
        Initiates an interactive ssh session with a given instance name.

        :return: None
        """
        if self.static:
            self.disabled('login')

        # make sure vagrant knows about this host
        try:
            conf = self.molecule._provisioner.conf(vm_name=self.molecule._args['<host>'])
            ssh_args = [conf['HostName'], conf['User'], conf['Port'], conf['IdentityFile'],
                        ' '.join(self.molecule._config.config['molecule']['raw_ssh_args'])]
            ssh_cmd = 'ssh {} -l {} -p {} -i {} {}'
        except CalledProcessError:
            # gets appended to python-vagrant's error message
            conf_format = [Fore.RED, self.molecule._args['<host>'], Fore.YELLOW, Fore.RESET]
            conf_errmsg = '\n{0}Unknown host {1}. Try {2}molecule status{0} to see available hosts.{3}'
            print(conf_errmsg.format(*conf_format))
            sys.exit(1)

        lines, columns = os.popen('stty size', 'r').read().split()
        dimensions = (int(lines), int(columns))
        self.molecule._pt = pexpect.spawn('/usr/bin/env ' + ssh_cmd.format(*ssh_args), dimensions=dimensions)
        signal.signal(signal.SIGWINCH, self.molecule._sigwinch_passthrough)
        self.molecule._pt.interact()


class Init(AbstractCommand):
    def execute(self):
        """
        Creates the scaffolding for a new role intended for use with molecule

        :return: None
        """
        role = self.molecule._args['<role>']
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

        t_molecule = env.get_template(self.molecule._config.config['molecule']['init']['templates']['molecule'])
        t_playbook = env.get_template(self.molecule._config.config['molecule']['init']['templates']['playbook'])
        t_default_spec = env.get_template(self.molecule._config.config['molecule']['init']['templates']['default_spec'])
        t_spec_helper = env.get_template(self.molecule._config.config['molecule']['init']['templates']['spec_helper'])

        sanitized_role = re.sub('[._]', '-', role)
        with open(role_path + self.molecule._config.config['molecule']['molecule_file'], 'w') as f:
            f.write(t_molecule.render(config=self.molecule._config.config, role=sanitized_role))

        with open(role_path + self.molecule._config.config['ansible']['playbook'], 'w') as f:
            f.write(t_playbook.render(role=role))

        serverspec_path = role_path + self.molecule._config.config['molecule']['serverspec_dir'] + '/'
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

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
import pexpect
import re
import signal
import sys
from subprocess import CalledProcessError

import prettytable
import sh
import yaml
from colorama import Fore
from docopt import docopt
from jinja2 import Environment
from jinja2 import PackageLoader

import molecule.utilities as utilities
import molecule.validators as validators
from molecule.ansible_galaxy_install import AnsibleGalaxyInstall
from molecule.ansible_playbook import AnsiblePlaybook
from molecule.core import Molecule


class InvalidHost(Exception):
    pass


class AbstractCommand:
    def __init__(self, command_args, global_args, molecule=False):
        """
        Initialize commands

        :param command_args: arguments of the command
        :param global_args: arguments from the CLI
        :param molecule: molecule instance
        """
        self.args = docopt(self.__doc__, argv=command_args)
        self.args['<command>'] = self.__class__.__name__.lower()
        self.command_args = command_args

        self.static = False

        # give us the option to reuse an existing molecule instance
        if not molecule:
            self.molecule = Molecule(self.args)
            self.molecule.main()
        else:
            self.molecule = molecule

        # init doesn't need to load molecule files
        if self.__class__.__name__ == 'Init':
            return

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
    """
    Creates all instances defined in molecule.yml.

    Usage:
        create [--platform=<platform>] [--provider=<provider>] [--debug]

    Options:
        --platform=<platform>  specify a platform
        --provider=<provider>  specify a provider
        --debug                get more detail
    """

    def execute(self, exit=True):
        if self.static:
            self.disabled('create')

        self.molecule._create_templates()
        try:
            self.molecule._provisioner.up(no_provision=True)
            self.molecule._state['created'] = True
            self.molecule._write_state_file()
        except CalledProcessError as e:
            print('ERROR: {}'.format(e))
            if exit:
                sys.exit(e.exit_code)
            return e.exit_code, None
        return None, None


class Destroy(AbstractCommand):
    """
    Destroys all instances created by molecule.

    Usage:
        destroy [--platform=<platform>] [--provider=<provider>] [--debug]

    Options:
        --platform=<platform>  specify a platform
        --provider=<provider>  specify a provider
        --debug                get more detail
    """

    def execute(self, exit=True):
        """
        Removes template files.
        Clears state file of all info (default platform).

        :return: None
        """
        if self.static:
            self.disabled('destroy')

        self.molecule._create_templates()
        try:
            self.molecule._provisioner.destroy()
            self.molecule._state['default_platform'] = False
            self.molecule._state['default_provider'] = False
            self.molecule._state['created'] = False
            self.molecule._state['converged'] = False
            self.molecule._write_state_file()
        except CalledProcessError as e:
            print('ERROR: {}'.format(e))
            if exit:
                sys.exit(e.exit_code)
            return e.exit_code, None
        self.molecule._remove_templates()
        return None, None


class Converge(AbstractCommand):
    """
    Provisions all instances defined in molecule.yml.

    Usage:
        converge [--platform=<platform>] [--provider=<provider>] [--tags=<tag1,tag2>...] [--debug]

    Options:
        --platform=<platform>  specify a platform
        --provider=<provider>  specify a provider
        --tags=<tag1,tag2>     comma separated list of ansible tags to target
        --debug                get more detail
    """

    def execute(self, idempotent=False, create_instances=True, create_inventory=True, exit=True, hide_errors=True):
        """
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
            command_args, args = utilities.remove_args(self.command_args, self.args, ['--tags'])
            c = Create(command_args, args, self.molecule)
            c.execute()

        if create_inventory:
            self.molecule._create_inventory_file()

        # install role dependencies only during `molecule converge`
        if not idempotent and 'requirements_file' in self.molecule._config.config['ansible']:
            print('{}Installing role dependencies ...{}'.format(Fore.CYAN, Fore.RESET))
            galaxy_install = AnsibleGalaxyInstall(self.molecule._config.config['ansible']['requirements_file'])
            galaxy_install.add_env_arg('ANSIBLE_CONFIG', self.molecule._config.config['ansible']['config_file'])
            galaxy_install.bake()
            output = galaxy_install.execute()

        ansible = AnsiblePlaybook(self.molecule._config.config['ansible'])

        # target tags passed in via CLI
        if self.molecule._args.get('--tags'):
            ansible.add_cli_arg('tags', self.molecule._args['--tags'].pop(0))

        if idempotent:
            ansible.remove_cli_arg('_out')
            ansible.remove_cli_arg('_err')
            ansible.add_env_arg('ANSIBLE_NOCOLOR', 'true')
            ansible.add_env_arg('ANSIBLE_FORCE_COLOR', 'false')

            # Save the previous callback plugin if any.
            callback_plugin = ansible.env.get('ANSIBLE_CALLBACK_PLUGINS', '')

            # Set the idempotence plugin.
            if callback_plugin:
                ansible.add_env_arg('ANSIBLE_CALLBACK_PLUGINS', callback_plugin + ':' + os.path.join(
                    sys.prefix, 'share/molecule/ansible/plugins/callback/idempotence'))
            else:
                ansible.add_env_arg('ANSIBLE_CALLBACK_PLUGINS',
                                    os.path.join(sys.prefix, 'share/molecule/ansible/plugins/callback/idempotence'))

        ansible.bake()
        if self.molecule._args.get('--debug'):
            ansible_env = {k: v for (k, v) in ansible.env.items() if 'ANSIBLE' in k}
            other_env = {k: v for (k, v) in ansible.env.items() if 'ANSIBLE' not in k}
            utilities.debug('OTHER ENVIRONMENT', yaml.dump(other_env, default_flow_style=False, indent=2))
            utilities.debug('ANSIBLE ENVIRONMENT', yaml.dump(ansible_env, default_flow_style=False, indent=2))
            utilities.debug('ANSIBLE PLAYBOOK', str(ansible.ansible))

        status, output = ansible.execute(hide_errors=hide_errors)
        if status is not None:
            if exit:
                sys.exit(status)
            return status, None

        if not self.molecule._state.get('converged'):
            self.molecule._state['converged'] = True
            self.molecule._write_state_file()

        return None, output


class Idempotence(AbstractCommand):
    """
    Provisions instances and parses output to determine idempotence.

    Usage:
        idempotence [--platform=<platform>] [--provider=<provider>] [--debug]

    Options:
        --platform=<platform>  specify a platform
        --provider=<provider>  specify a provide
        --debug                get more detail
    """

    def execute(self, exit=True):
        if self.static:
            self.disabled('idempotence')

        print('{}Idempotence test in progress (can take a few minutes)...{}'.format(Fore.MAGENTA, Fore.RESET))

        c = Converge(self.command_args, self.args, self.molecule)
        status, output = c.execute(idempotent=True, exit=False, hide_errors=True)
        if status is not None:
            msg = '{}Skipping due to errors during converge.\n{}'
            print(msg.format(Fore.YELLOW, Fore.RESET))
            return status, None

        idempotent, changed_tasks = self.molecule._parse_provisioning_output(output)

        if idempotent:
            print('{}Idempotence test passed.{}'.format(Fore.GREEN, Fore.RESET))
            print()
            return None, None

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
        if exit:
            sys.exit(1)
        return 1, None


class Verify(AbstractCommand):
    """
    Performs verification steps on running instances.

    Usage:
        verify [--platform=<platform>] [--provider=<provider>] [--debug]

    Options:
        --platform=<platform>  specify a platform
        --provider=<provider>  specify a provider
        --debug                get more detail
    """

    def execute(self, exit=True):
        if self.static:
            self.disabled('verify')

        serverspec_dir = self.molecule._config.config['molecule']['serverspec_dir']
        testinfra_dir = self.molecule._config.config['molecule']['testinfra_dir']
        inventory_file = self.molecule._config.config['ansible']['inventory_file']
        rakefile = self.molecule._config.config['molecule']['rakefile_file']
        ignore_paths = self.molecule._config.config['molecule']['ignore_paths']

        # whitespace & trailing newline check
        validators.check_trailing_cruft(ignore_paths=ignore_paths, exit=exit)

        # no serverspec or testinfra
        if not os.path.isdir(serverspec_dir) and not os.path.isdir(testinfra_dir):
            msg = '{}Skipping tests, could not find {}/ or {}/.{}'
            print(msg.format(Fore.YELLOW, serverspec_dir, testinfra_dir, Fore.RESET))
            return None, None

        self.molecule._write_ssh_config()
        kwargs = {'env': self.molecule._env}
        kwargs['env']['PYTHONDONTWRITEBYTECODE'] = '1'
        kwargs['debug'] = True if self.molecule._args.get('--debug') else False

        try:
            # testinfra
            if os.path.isdir(testinfra_dir):
                msg = '\n{}Executing testinfra tests found in {}/.{}'
                print(msg.format(Fore.MAGENTA, testinfra_dir, Fore.RESET))
                validators.testinfra(inventory_file, **kwargs)
                print()
            else:
                msg = '{}No testinfra tests found in {}/.\n{}'
                print(msg.format(Fore.YELLOW, testinfra_dir, Fore.RESET))

            # serverspec / rubocop
            if os.path.isdir(serverspec_dir):
                msg = '{}Executing rubocop on *.rb files found in {}/.{}'
                print(msg.format(Fore.MAGENTA, serverspec_dir, Fore.RESET))
                validators.rubocop(serverspec_dir, **kwargs)
                print()

                msg = '{}Executing serverspec tests found in {}/.{}'
                print(msg.format(Fore.MAGENTA, serverspec_dir, Fore.RESET))
                validators.rake(rakefile, **kwargs)
                print()
            else:
                msg = '{}No serverspec tests found in {}/.\n{}'
                print(msg.format(Fore.YELLOW, serverspec_dir, Fore.RESET))
        except sh.ErrorReturnCode as e:
            print('ERROR: {}'.format(e))
            if exit:
                sys.exit(e.exit_code)
            return e.exit_code, None

        return None, None


class Test(AbstractCommand):
    """
    Runs a series of commands (defined in config) against instances for a full test/verify run.

    Usage:
        test [--platform=<platform>] [--provider=<provider>] [--destroy=<destroy>] [--debug]

    Options:
        --platform=<platform>  specify a platform
        --provider=<provider>  specify a provider
        --destroy=<destroy>    destroy behavior (passing, always, never)
        --debug                get more detail
    """

    def execute(self):
        if self.static:
            self.disabled('test')

        command_args, args = utilities.remove_args(self.command_args, self.args, ['--destroy'])

        for task in self.molecule._config.config['molecule']['test']['sequence']:
            command = getattr(sys.modules[__name__], task.capitalize())
            c = command(command_args, args)
            status, output = c.execute(exit=False)

        if self.args.get('--destroy') == 'always':
            c = Destroy(command_args, args)
            c.execute()
            return None, None

        if self.args.get('--destroy') == 'never':
            return None, None

        # passing (default)
        if status is None:
            c = Destroy(command_args, args)
            c.execute()
            return None, None

        # error encountered during test
        sys.exit(status)


class List(AbstractCommand):
    """
    Prints a list of currently available platforms

    Usage:
        list [--debug] [-m]

    Options:
        --debug  get more detail
        -m       machine readable output
    """

    def execute(self):
        if self.static:
            self.disabled('list')

        is_machine_readable = self.molecule._args['-m']
        self.molecule._print_valid_platforms(machine_readable=is_machine_readable)
        return None, None


class Status(AbstractCommand):
    """
    Prints status of configured instances.

    Usage:
        status [--debug]

    Options:
        --debug  get more detail
    """

    def execute(self):
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
            return e.exit_code, None

        x = prettytable.PrettyTable(['Name', 'State', 'Provider'])
        x.align = 'l'

        for item in status:
            if item.state != 'not_created':
                state = Fore.GREEN + item.state + Fore.RESET
            else:
                state = item.state

            x.add_row([item.name, state, item.provider])

        print(x)
        print()
        self.molecule._print_valid_platforms()
        print()
        self.molecule._print_valid_providers()
        return None, None


class Login(AbstractCommand):
    """
    Initiates an interactive ssh session with the given host.

    Usage:
        login [<host>]
    """

    def execute(self):
        if self.static:
            self.disabled('login')

        # make sure vagrant knows about this host
        try:

            # Check whether a host was specified.
            if self.molecule._args['<host>'] is None:

                # If not, collect the list of running hosts.
                try:
                    status = self.molecule._provisioner.status()
                except Exception as e:
                    status = []

                # Nowhere to log into if there is no running host.
                if len(status) == 0:
                    raise InvalidHost("There is no running host.")

                # One running host is perfect. Log into it.
                elif len(status) == 1:
                    hostname = status[0].name

                # But too many hosts is trouble as well.
                else:
                    raise InvalidHost("There are {} running hosts. You can only log into one at a time.".format(len(
                        status)))

            else:

                # If the host was specified, try to use it.
                hostname = self.molecule._args['<host>']

            # Try to retrieve the SSH configuration of the host.
            conf = self.molecule._provisioner.conf(vm_name=hostname)

            # Prepare the command to SSH into the host.
            ssh_args = [conf['HostName'], conf['User'], conf['Port'], conf['IdentityFile'],
                        ' '.join(self.molecule._config.config['molecule']['raw_ssh_args'])]
            ssh_cmd = 'ssh {} -l {} -p {} -i {} {}'
        except CalledProcessError:
            # gets appended to python-vagrant's error message
            conf_format = [Fore.RED, self.molecule._args['<host>'], Fore.YELLOW, Fore.RESET]
            conf_errmsg = '\n{0}Unknown host {1}. Try {2}molecule status{0} to see available hosts.{3}'
            print(conf_errmsg.format(*conf_format))
            sys.exit(1)
        except InvalidHost as e:
            conf_format = [Fore.RED, e.message, Fore.RESET]
            conf_errmsg = '{}{}{}'
            print(conf_errmsg.format(*conf_format))
            sys.exit(1)

        lines, columns = os.popen('stty size', 'r').read().split()
        dimensions = (int(lines), int(columns))
        self.molecule._pt = pexpect.spawn('/usr/bin/env ' + ssh_cmd.format(*ssh_args), dimensions=dimensions)
        signal.signal(signal.SIGWINCH, self.molecule._sigwinch_passthrough)
        self.molecule._pt.interact()
        return None, None


class Init(AbstractCommand):
    """
    Creates the scaffolding for a new role intended for use with molecule.

    Usage:
        init <role>
    """

    def clean_meta_main(self, role_path):
        main_path = os.path.join(role_path, 'meta', 'main.yml')
        temp_path = os.path.join(role_path, 'meta', 'main.yml.tmp')
        with open(temp_path, 'w') as temp:
            for line in file(main_path):
                line = re.sub(r'[ \t]*$', '', line)
                if line != '\n':
                    temp.write(line)
        os.rename(temp_path, main_path)

    def execute(self):
        role = self.molecule._args['<role>']
        role_path = os.path.join(os.curdir, role)
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
            sys.exit(e.exit_code)

        self.clean_meta_main(role_path)

        env = Environment(loader=PackageLoader('molecule', 'templates'), keep_trailing_newline=True)

        t_molecule = env.get_template(self.molecule._config.config['molecule']['init']['templates']['molecule'])
        t_playbook = env.get_template(self.molecule._config.config['molecule']['init']['templates']['playbook'])
        t_default_spec = env.get_template(self.molecule._config.config['molecule']['init']['templates']['default_spec'])
        t_spec_helper = env.get_template(self.molecule._config.config['molecule']['init']['templates']['spec_helper'])

        sanitized_role = re.sub('[._]', '-', role)
        with open(os.path.join(role_path, self.molecule._config.config['molecule']['molecule_file']), 'w') as f:
            f.write(t_molecule.render(config=self.molecule._config.config, role=sanitized_role))

        with open(os.path.join(role_path, self.molecule._config.config['ansible']['playbook']), 'w') as f:
            f.write(t_playbook.render(role=role))

        serverspec_path = os.path.join(role_path, self.molecule._config.config['molecule']['serverspec_dir'])
        os.makedirs(serverspec_path)
        os.makedirs(os.path.join(serverspec_path, 'hosts'))
        os.makedirs(os.path.join(serverspec_path, 'groups'))

        with open(os.path.join(serverspec_path, 'default_spec.rb'), 'w') as f:
            f.write(t_default_spec.render())

        with open(os.path.join(serverspec_path, 'spec_helper.rb'), 'w') as f:
            f.write(t_spec_helper.render())

        msg = '{}Successfully initialized new role in {}{}'
        print(msg.format(Fore.GREEN, role_path, Fore.RESET))
        sys.exit(0)

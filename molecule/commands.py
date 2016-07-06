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

import glob
import os
import pexpect
import re
import signal
import sys
from subprocess import CalledProcessError

import colorama
from docopt import docopt
import jinja2
import sh
import yaml

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

        # Add or update the group_vars if needed.
        self.molecule._add_or_update_group_vars()

    def disabled(self, cmd):
        """
        Prints 'command disabled' message and exits program.

        :param cmd: Name of the disabled command to print.
        :return: None
        """
        fmt = [colorama.Fore.RED, cmd, colorama.Fore.RESET]
        errmsg = "{}The `{}` command isn't supported with static inventory.{}"
        utilities.logger.error(errmsg.format(*fmt))
        sys.exit(1)

    def execute(self):
        raise NotImplementedError


class Check(AbstractCommand):
    """
    Performs a syntax check on the current role.

    Usage:
        check
    """

    def execute(self, exit=True):

        self.molecule._create_templates()

        ansible = AnsiblePlaybook(self.molecule._config.config['ansible'])
        ansible.add_cli_arg('syntax-check', True)
        ansible.add_cli_arg('inventory-file', 'localhost,')

        return ansible.execute(hide_errors=True)


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
            utilities.logger.error('ERROR: {}'.format(e))
            if exit:
                sys.exit(e.returncode)
            return e.returncode, e.message
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
            utilities.logger.error('ERROR: {}'.format(e))
            if exit:
                sys.exit(e.returncode)
            return e.returncode, e.message
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

    def execute(self,
                idempotent=False,
                create_instances=True,
                create_inventory=True,
                exit=True,
                hide_errors=True):
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
            command_args, args = utilities.remove_args(self.command_args,
                                                       self.args, ['--tags'])
            c = Create(command_args, args, self.molecule)
            c.execute()

        if create_inventory:
            self.molecule._create_inventory_file()

        # install role dependencies only during `molecule converge`
        if not idempotent and 'requirements_file' in self.molecule._config.config[
                'ansible']:
            print('{}Installing role dependencies ...{}'.format(
                colorama.Fore.CYAN, colorama.Fore.RESET))
            galaxy_install = AnsibleGalaxyInstall(self.molecule._config.config[
                'ansible']['requirements_file'])
            galaxy_install.add_env_arg(
                'ANSIBLE_CONFIG',
                self.molecule._config.config['ansible']['config_file'])
            galaxy_install.bake()
            output = galaxy_install.execute()

        ansible = AnsiblePlaybook(self.molecule._config.config['ansible'])

        # params to work with provisioner
        for k, v in self.molecule._provisioner.ansible_connection_params.items(
        ):
            ansible.add_cli_arg(k, v)

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
                ansible.add_env_arg(
                    'ANSIBLE_CALLBACK_PLUGINS',
                    callback_plugin + ':' + os.path.join(
                        sys.prefix,
                        'share/molecule/ansible/plugins/callback/idempotence'))
            else:
                ansible.add_env_arg('ANSIBLE_CALLBACK_PLUGINS', os.path.join(
                    sys.prefix,
                    'share/molecule/ansible/plugins/callback/idempotence'))

        ansible.bake()
        if self.molecule._args.get('--debug'):
            ansible_env = {k: v
                           for (k, v) in ansible.env.items() if 'ANSIBLE' in k}
            other_env = {k: v
                         for (k, v) in ansible.env.items()
                         if 'ANSIBLE' not in k}
            utilities.debug('OTHER ENVIRONMENT',
                            yaml.dump(other_env,
                                      default_flow_style=False,
                                      indent=2))
            utilities.debug('ANSIBLE ENVIRONMENT',
                            yaml.dump(ansible_env,
                                      default_flow_style=False,
                                      indent=2))
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

        print(
            '{}Idempotence test in progress (can take a few minutes)...{}'.format(
                colorama.Fore.MAGENTA, colorama.Fore.RESET))

        c = Converge(self.command_args, self.args, self.molecule)
        status, output = c.execute(idempotent=True,
                                   exit=False,
                                   hide_errors=True)
        if status is not None:
            msg = '{}Skipping due to errors during converge.\n{}'
            print(msg.format(colorama.Fore.YELLOW, colorama.Fore.RESET))
            return status, None

        idempotent, changed_tasks = self.molecule._parse_provisioning_output(
            output)

        if idempotent:
            print('{}Idempotence test passed.{}'.format(colorama.Fore.GREEN,
                                                        colorama.Fore.RESET))
            print()
            return None, None

        # Display the details of the idempotence test.
        if changed_tasks:
            utilities.logger.error(
                '{}Idempotence test failed because of the following tasks:{}'.format(
                    colorama.Fore.RED, colorama.Fore.RESET))
            utilities.logger.error('{}{}{}'.format(colorama.Fore.RED,
                                                   '\n'.join(changed_tasks),
                                                   colorama.Fore.RESET))
        else:
            # But in case the idempotence callback plugin was not found, we just display an error message.
            utilities.logger.error('{}Idempotence test failed.{}'.format(
                colorama.Fore.RED, colorama.Fore.RESET))
            warning_msg = "The idempotence plugin was not found or did not provide the required information. " \
                          "Therefore the failure details cannot be displayed."

            utilities.logger.warning('{}{}{}'.format(
                colorama.Fore.YELLOW, warning_msg, colorama.Fore.RESET))
        if exit:
            sys.exit(1)
        return 1, None


class Verify(AbstractCommand):
    """
    Performs verification steps on running instances.

    Usage:
        verify [--platform=<platform>] [--provider=<provider>] [--debug] [--sudo]

    Options:
        --platform=<platform>  specify a platform
        --provider=<provider>  specify a provider
        --debug                get more detail
        --sudo                 runs tests with sudo
    """

    def execute(self, exit=True):
        if self.static:
            self.disabled('verify')

        serverspec_dir = self.molecule._config.config['molecule'][
            'serverspec_dir']
        testinfra_dir = self.molecule._config.config['molecule'][
            'testinfra_dir']
        rakefile = self.molecule._config.config['molecule']['rakefile_file']
        ignore_paths = self.molecule._config.config['molecule']['ignore_paths']

        # whitespace & trailing newline check
        validators.check_trailing_cruft(ignore_paths=ignore_paths, exit=exit)

        # no serverspec or testinfra
        if not os.path.isdir(serverspec_dir) and not os.path.isdir(
                testinfra_dir):
            msg = '{}Skipping tests, could not find {}/ or {}/.{}'
            utilities.logger.warning(msg.format(colorama.Fore.YELLOW,
                                                serverspec_dir, testinfra_dir,
                                                colorama.Fore.RESET))
            return None, None

        self.molecule._write_ssh_config()

        # testinfra's Ansible calls get same env vars as ansible-playbook
        ansible = AnsiblePlaybook(self.molecule._config.config['ansible'],
                                  _env=self.molecule._env)

        testinfra_kwargs = utilities.merge_dicts(
            self.molecule._provisioner.testinfra_args,
            self.molecule._config.config['testinfra'])
        serverspec_kwargs = self.molecule._provisioner.serverspec_args
        testinfra_kwargs['env'] = ansible.env
        testinfra_kwargs['env']['PYTHONDONTWRITEBYTECODE'] = '1'
        if self.molecule._args.get('--debug'):
            testinfra_kwargs['debug'] = True
        if self.molecule._args.get('--sudo'):
            testinfra_kwargs['sudo'] = True
        serverspec_kwargs['env'] = testinfra_kwargs['env']
        serverspec_kwargs['debug'] = testinfra_kwargs.get('debug')

        try:
            # testinfra
            if len(glob.glob1(testinfra_dir, "test_*.py")) > 0:
                msg = '\n{}Executing testinfra tests found in {}/.{}'
                print(msg.format(colorama.Fore.MAGENTA, testinfra_dir,
                                 colorama.Fore.RESET))
                validators.testinfra(testinfra_dir, **testinfra_kwargs)
                print()
            else:
                msg = '{}No testinfra tests found in {}/.\n{}'
                utilities.logger.warning(msg.format(
                    colorama.Fore.YELLOW, testinfra_dir, colorama.Fore.RESET))

            # serverspec / rubocop
            if os.path.isdir(serverspec_dir):
                msg = '{}Executing rubocop on *.rb files found in {}/.{}'
                print(msg.format(colorama.Fore.MAGENTA, serverspec_dir,
                                 colorama.Fore.RESET))
                validators.rubocop(serverspec_dir, **serverspec_kwargs)
                print()

                msg = '{}Executing serverspec tests found in {}/.{}'
                print(msg.format(colorama.Fore.MAGENTA, serverspec_dir,
                                 colorama.Fore.RESET))
                validators.rake(rakefile, **serverspec_kwargs)
                print()
            else:
                msg = '{}No serverspec tests found in {}/.\n{}'
                utilities.logger.warning(msg.format(
                    colorama.Fore.YELLOW, serverspec_dir, colorama.Fore.RESET))
        except sh.ErrorReturnCode as e:
            utilities.logger.error('ERROR: {}'.format(e))
            if exit:
                sys.exit(e.exit_code)
            return e.exit_code, e.stdout

        return None, None


class Test(AbstractCommand):
    """
    Runs a series of commands (defined in config) against instances for a full test/verify run.

    Usage:
        test [--platform=<platform>] [--provider=<provider>] [--destroy=<destroy>] [--debug] [--sudo]

    Options:
        --platform=<platform>  specify a platform
        --provider=<provider>  specify a provider
        --destroy=<destroy>    destroy behavior (passing, always, never)
        --debug                get more detail
        --sudo                 run tests with sudo
    """

    def execute(self):
        if self.static:
            self.disabled('test')

        command_args, args = utilities.remove_args(
            self.command_args, self.args, self.command_args)

        for task in self.molecule._config.config['molecule']['test'][
                'sequence']:
            command = getattr(sys.modules[__name__], task.capitalize())
            c = command(command_args, args)

            for argument in self.command_args:
                if argument in c.args:
                    c.args[argument] = self.args[argument]

            status, output = c.execute(exit=False)

            # Fail fast
            if status is not 0 and status is not None:
                utilities.logger.error(output)
                sys.exit(status)

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
        list [--debug] ([-m]|[--porcelain])

    Options:
        --debug         get more detail
        -m              synonym for '--porcelain' (deprecated)
        --porcelain     machine readable output
    """

    def execute(self):
        if self.static:
            self.disabled('list')

        porcelain = self.molecule._args['-m'] or self.molecule._args[
            '--porcelain']
        self.molecule._print_valid_platforms(porcelain=porcelain)
        return None, None


class Status(AbstractCommand):
    """
    Prints status of configured instances.

    Usage:
        status [--debug][--porcelain] ([--hosts] [--platforms][--providers])

    Options:
        --debug         get more detail
        --porcelain     machine readable output
        --hosts         display the available hosts
        --platforms     display the available platforms
        --providers     display the available providers
    """

    def execute(self):
        if self.static:
            self.disabled('status')

        display_all = not any([self.args['--hosts'], self.args['--platforms'],
                               self.args['--providers']])

        # Check that an instance is created.
        if not self.molecule._state.get('created'):
            errmsg = '{}ERROR: No instances created. Try `{} create` first.{}'
            utilities.logger.error(errmsg.format(colorama.Fore.RED,
                                                 os.path.basename(sys.argv[0]),
                                                 colorama.Fore.RESET))
            sys.exit(1)

        # Retrieve the status.
        try:
            status = self.molecule._provisioner.status()
        except CalledProcessError as e:
            utilities.logger.error(e.message)
            return e.returncode, e.message

        # Display the results in procelain mode.
        porcelain = self.molecule._args['--porcelain']

        # Display hosts information.
        if display_all or self.molecule._args['--hosts']:

            # Prepare the table for the results.
            headers = [] if porcelain else ['Name', 'State', 'Provider']
            data = []

            for item in status:
                if item.state != 'not_created':
                    state = colorama.Fore.GREEN + item.state + colorama.Fore.RESET
                else:
                    state = item.state

                data.append([item.name, state, item.provider])

            self.molecule._display_tabulate_data(data, headers=headers)
            print()

        # Display the platforms.
        if display_all or self.molecule._args['--platforms']:
            self.molecule._print_valid_platforms(porcelain=porcelain)
            print()

        # Display the providers.
        if display_all or self.molecule._args['--providers']:
            self.molecule._print_valid_providers(porcelain=porcelain)

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

        # Collect the list of running hosts.
        try:
            status = self.molecule._provisioner.status()
        except Exception as e:
            status = []

        # make sure vagrant knows about this host
        try:
            # Nowhere to log into if there is no running host.
            if len(status) == 0:
                raise InvalidHost("There is no running host.")

            # Check whether a host was specified.
            if self.molecule._args['<host>'] is None:

                # One running host is perfect. Log into it.
                if len(status) == 1:
                    hostname = status[0].name

                # But too many hosts is trouble as well.
                else:
                    raise InvalidHost(
                        "There are {} running hosts. You can only log into one at a time.".format(
                            len(status)))

            else:

                # If the host was specified, try to use it.
                hostname = self.molecule._args['<host>']
                match = [x.name for x in status if x.name.startswith(hostname)]
                if len(match) == 0:
                    raise CalledProcessError(1, None)
                elif len(match) != 1:
                    raise InvalidHost(
                        "There are {} hosts that match '{}'.  You can only log into one at a time.\n"
                        "Try {}molecule status{} to see available hosts.".format(
                            len(match), hostname, colorama.Fore.YELLOW,
                            colorama.Fore.RED))
                hostname = match[0]

            login_cmd = self.molecule._provisioner.login_cmd(hostname)
            login_args = self.molecule._provisioner.login_args(hostname)

        except CalledProcessError:
            # gets appended to python-vagrant's error message
            conf_format = [colorama.Fore.RED, self.molecule._args['<host>'],
                           colorama.Fore.YELLOW, colorama.Fore.RESET]
            conf_errmsg = '\n{0}Unknown host {1}. Try {2}molecule status{0} to see available hosts.{3}'
            utilities.logger.error(conf_errmsg.format(*conf_format))
            sys.exit(1)
        except InvalidHost as e:
            conf_format = [colorama.Fore.RED, e.message, colorama.Fore.RESET]
            conf_errmsg = '{}{}{}'
            utilities.logger.error(conf_errmsg.format(*conf_format))
            sys.exit(1)

        lines, columns = os.popen('stty size', 'r').read().split()
        dimensions = (int(lines), int(columns))
        self.molecule._pt = pexpect.spawn(
            '/usr/bin/env ' + login_cmd.format(*login_args),
            dimensions=dimensions)
        signal.signal(signal.SIGWINCH, self.molecule._sigwinch_passthrough)
        self.molecule._pt.interact()
        return None, None


class Init(AbstractCommand):
    """
    Creates the scaffolding for a new role intended for use with molecule.

    Usage:
        init <role> [--docker] [--offline]
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
            utilities.logger.error(msg.format(
                colorama.Fore.RED, colorama.Fore.YELLOW, os.path.basename(
                    sys.argv[0]), colorama.Fore.RESET))
            sys.exit(1)

        if os.path.isdir(role):
            msg = '{}The directory {} already exists. Cannot create new role.{}'
            utilities.logger.error(msg.format(colorama.Fore.RED, role_path,
                                              colorama.Fore.RESET))
            sys.exit(1)

        try:
            if self.molecule._args['--offline']:
                sh.ansible_galaxy('init', '--offline', role)
            else:
                sh.ansible_galaxy('init', role)
        except (CalledProcessError, sh.ErrorReturnCode_1) as e:
            utilities.logger.error('ERROR: {}'.format(e))
            sys.exit(e.returncode)

        self.clean_meta_main(role_path)

        env = jinja2.Environment(
            loader=jinja2.PackageLoader('molecule', 'templates'),
            keep_trailing_newline=True)

        t_molecule = env.get_template(self.molecule._config.config['molecule'][
            'init']['templates']['molecule'])
        t_playbook = env.get_template(self.molecule._config.config['molecule'][
            'init']['templates']['playbook'])
        t_test_default = env.get_template(self.molecule._config.config[
            'molecule']['init']['templates']['test_default'])

        if (self.molecule._args['--docker']):
            t_molecule = env.get_template(self.molecule._config.config[
                'molecule']['init']['templates']['molecule_docker'])

        sanitized_role = re.sub('[._]', '-', role)
        with open(
                os.path.join(
                    role_path,
                    self.molecule._config.config['molecule']['molecule_file']),
                'w') as f:
            f.write(t_molecule.render(config=self.molecule._config.config,
                                      role=sanitized_role))

        with open(
                os.path.join(
                    role_path,
                    self.molecule._config.config['ansible']['playbook']),
                'w') as f:
            f.write(t_playbook.render(role=role))

        testinfra_path = os.path.join(
            role_path,
            self.molecule._config.config['molecule']['testinfra_dir'])

        with open(os.path.join(testinfra_path, 'test_default.py'), 'w') as f:
            f.write(t_test_default.render())

        msg = '{}Successfully initialized new role in {}{}'
        print(msg.format(colorama.Fore.GREEN, role_path, colorama.Fore.RESET))
        sys.exit(0)

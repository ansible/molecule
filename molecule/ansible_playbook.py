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
import sh

from molecule import utilities


class AnsiblePlaybook:
    def __init__(self,
                 args,
                 _env=None,
                 _out=utilities.logger.info,
                 _err=utilities.logger.error):
        """
        Sets up requirements for ansible-playbook

        :param args: Dictionary arguments to pass to ansible-playbook
        :param _env: Environment dictionary to use. os.environ.copy() is used by default
        :param _out: Function passed to sh for STDOUT
        :param _err: Function passed to sh for STDERR
        :return: None
        """
        self.cli = {}
        self.cli_pos = []
        self.env = _env if _env else os.environ.copy()
        self.playbook = None
        self.ansible = None

        # process arguments passed in (typically from molecule.yml's ansible block)
        for k, v in args.iteritems():
            self.parse_arg(k, v)

        # defaults can be redefined with call to add_env_arg() before baking
        self.add_env_arg('PYTHONUNBUFFERED', '1')
        self.add_env_arg('ANSIBLE_FORCE_COLOR', 'true')

        # passed through to sh, not ansible-playbook
        self.add_cli_arg('_out', _out)
        self.add_cli_arg('_err', _err)

    def bake(self):
        """
        Bake ansible-playbook command so it's ready to execute.

        :return: None
        """
        self.ansible = sh.ansible_playbook.bake(self.playbook,
                                                *self.cli_pos,
                                                _env=self.env,
                                                **self.cli)

    def parse_arg(self, name, value):
        """
        Parses argument and adds to CLI or environment

        :param name: Name of argument to be added
        :param value: Value of argument to be added
        :return: None
        """

        # skip `requirements_file` since it used by ansible-galaxy only
        if name == 'requirements_file':
            return

        if name == 'raw_env_vars':
            for k, v in value.iteritems():
                self.add_env_arg(k, v)
            return

        if name == 'host_key_checking':
            self.add_env_arg('ANSIBLE_HOST_KEY_CHECKING', str(value).lower())
            return

        if name == 'raw_ssh_args':
            self.add_env_arg('ANSIBLE_SSH_ARGS', ' '.join(value))
            return

        if name == 'config_file':
            self.add_env_arg('ANSIBLE_CONFIG', value)
            return

        if name == 'playbook':
            self.playbook = value
            return

        if name == 'host_vars' or name == 'group_vars':
            return

        # verbose is weird, must be -vvvv not verbose=vvvv
        if name == 'verbose' and value:
            # for cases where someone passes in verbose: True
            if value is True:
                value = 'vvvv'
            self.cli_pos.append('-' + value)
            return

        self.add_cli_arg(name, value)

    def add_cli_arg(self, name, value):
        """
        Adds argument to CLI passed to ansible-playbook

        :param name: Name of argument to be added
        :param value: Value of argument to be added
        :return: None
        """
        if value:
            self.cli[name] = value

    def remove_cli_arg(self, name):
        """
        Removes CLI argument

        :param name: Key name of CLI argument to remove
        :return: None
        """
        self.cli.pop(name, None)

    def add_env_arg(self, name, value):
        """
        Adds argument to environment passed to ansible-playbook

        :param name: Name of argument to be added
        :param value: Value of argument to be added
        :return: None
        """
        self.env[name] = value

    def remove_env_arg(self, name):
        """
        Removes environment argument

        :param name: Key name of environment argument to remove
        :return: None
        """
        self.env.pop(name, None)

    def execute(self, hide_errors=False):
        """
        Executes ansible-playbook

        :returns: exit code if any, output of command as string
        """
        if self.ansible is None:
            self.bake()

        try:
            return None, self.ansible().stdout
        except (sh.ErrorReturnCode, sh.ErrorReturnCode_2) as e:
            if not hide_errors:
                utilities.logger.error('ERROR: {}'.format(e))

            return e.exit_code, None

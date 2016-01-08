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

import sh

import molecule.utilities as utilities


class AnsiblePlaybook:
    def __init__(self, args={}, _env=None, _out=utilities.print_stdout, _err=utilities.print_stderr):
        """
        Sets up requirements for ansible-playbook

        :param args: Dictionary arguments to pass to ansible-playbook
        :param _env: Environment dictionary to use. os.environ.copy() is used by default
        :param _out: Function passed to sh for STDOUT
        :param _err: Function passed to sh for STDERR

        :return: None
        """

        self.cli = {}
        self.env = _env if _env else os.environ.copy()
        self.playbook = None
        self.ansible = None

        for k, v in args.iteritems():
            self.parse_arg(k, v)

        # these can be overridden with calls to add_env_arg()
        self.add_env_arg('PYTHONUNBUFFERED', '1')
        self.add_env_arg('ANSIBLE_FORCE_COLOR', 'true')

        # these get passed through to sh, not ansible-playbook
        self.add_cli_arg('_out', _out)
        self.add_cli_arg('_err', _err)

    def bake(self):
        """
        Bake ansible-playbook command so it's ready to execute.

        :return: None
        """
        self.ansible = sh.ansible_playbook.bake(self.playbook, _env=self.env, **self.cli)

    def parse_arg(self, name, value):
        """
        Sanitizes and adds CLI arguments to be passed to ansible-playbook

        :param name: Name of CLI argument to be added
        :param value: Value of CLI argument to be added
        :return: None
        """

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

        # don't pass False values to ansible-playbook
        if not value:
            return

        self.add_cli_arg(name, value)

        ### make sure verbose: vvvv works as --verbose ###
        # verbose is weird -vvvv
        # if self._config.config['ansible']['verbose']:
        #     args.append('-' + self._config.config['ansible']['verbose'])

    def add_cli_arg(self, name, value):
        self.cli[name] = value

    def add_env_arg(self, name, value):
        self.env[name] = value

    def execute(self):
        if self.ansible is None:
            self.bake()

        self.ansible()

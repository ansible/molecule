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

import os
import sh

from molecule import util


class AnsiblePlaybook(object):
    def __init__(self,
                 args,
                 connection_params,
                 raw_ansible_args=None,
                 _env=None,
                 _out=util.callback_info,
                 _err=util.callback_error,
                 debug=False):
        """
        Sets up requirements for ansible-playbook and returns None.

        :param args: A dict containing arguments to pass to ansible-playbook.
        :param connection_params: A dict containing driver specific connection
         params to pass to ansible-playbook.
        :param _env: An optional environment to pass to underlying :func:`sh`
         call.
        :param _out: An optional function to process STDOUT for underlying
         :func:`sh` call.
        :param _err: An optional function to process STDERR for underlying
         :func:`sh` call.
        :param debug: An optional bool to toggle debug output.
        :return: None
        """
        self._playbook = None
        self._ansible = None
        self._cli = {}
        self._cli_pos = []
        self._raw_ansible_args = raw_ansible_args
        self._env = _env if _env else os.environ.copy()
        self._debug = debug

        for k, v in args.iteritems():
            self.parse_arg(k, v)

        for k, v in connection_params.items():
            self.add_cli_arg(k, v)

        self.add_env_arg('PYTHONUNBUFFERED', '1')
        self.add_env_arg('ANSIBLE_FORCE_COLOR', 'true')

        self.add_cli_arg('_out', _out)
        self.add_cli_arg('_err', _err)

    @property
    def env(self):
        return self._env

    def bake(self):
        """
        Bake ansible-playbook command so it's ready to execute and returns
        None.

        :return: None
        """
        self._ansible = sh.ansible_playbook.bake(
            self._playbook, *self._cli_pos, _env=self._env, **self._cli)
        if self._raw_ansible_args:
            self._ansible = self._ansible.bake(self._raw_ansible_args)

    def parse_arg(self, name, value):
        """
        Adds argument to CLI or environment and returns None.

        :param name: A string containing the name of argument to be added.
        :param value: The value of argument to be added.
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
            self._playbook = value
            return

        if name in ['host_vars', 'group_vars', 'ansiblecfg_defaults']:
            return

        # verbose is weird, must be -vvvv not verbose=vvvv
        if name == 'verbose' and value:
            # for cases where someone passes in verbose: True
            if value is True:
                value = 'vvvv'
            self._cli_pos.append('-' + value)
            return

        self.add_cli_arg(name, value)

    def add_cli_arg(self, name, value):
        """
        Adds argument to CLI passed to ansible-playbook and returns None.

        :param name: A string containing the name of argument to be added.
        :param value: The value of argument to be added.
        :return: None
        """
        if value:
            self._cli[name] = value

    def remove_cli_arg(self, name):
        """
        Removes CLI argument and returns None.

        :param name: A string containing the name of argument to be removed.
        :return: None
        """
        self._cli.pop(name, None)

    def add_env_arg(self, name, value):
        """
        Adds argument to environment passed to ansible-playbook and returns
        None.

        :param name: A string containing the name of argument to be added.
        :param value: The value of argument to be added.
        :return: None
        """
        self._env[name] = value

    def remove_env_arg(self, name):
        """
        Removes environment argument and returns None.

        :param name: A string containing the name of argument to be removed.
        :return: None
        """
        self._env.pop(name, None)

    def execute(self, hide_errors=False):
        """
        Executes ansible-playbook and returns command's stdout.

        :param hide_errors: An optional bool to toggle output of errors.
        :return: The command's output, otherwise sys.exit on command failure.
        """
        if self._ansible is None:
            self.bake()

        try:
            return None, util.run_command(
                self._ansible, debug=self._debug).stdout
        except sh.ErrorReturnCode as e:
            if not hide_errors:
                util.print_error(str(e))

            return e.exit_code, None

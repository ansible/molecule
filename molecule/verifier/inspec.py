#  Copyright (c) 2015-2017 Cisco Systems, Inc.
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

from molecule import logger
from molecule import util
from molecule.verifier import base

LOG = logger.get_logger(__name__)


class Inspec(base.Base):
    """
    `Inspec`_ is an EXPERIMENTAL test runner.

    Additional options can be passed to `inspec` through the options
    dict.  Any option set in this section will override the defaults.

    Caveats: Only used with vagrant.


      driver:
        name: vagrant
        provider:
          name: vmware_desktop
      lint:
        name: yamllint
      platforms:
        - name: win1
          box: windows-2016
      provisioner:
        name: ansible
        connection_options:
          ansible_user: vagrant
          ansible_password: vagrant
          ansible_port: 55985
          ansible_connection: winrm
          ansible_winrm_scheme: http
          ansible_winrm_server_cert_validation: ignore

    Getting started with inspec
    1. gem install inspec
    2. create simple file:

       a. Windows: (first_win.rb)

          describe file('c:\windows\system.ini') do
            it { should exist }
          end

       b. Linux: (first_linux.rb)

          describe package('telnetd') do
            it { should_not be_installed }
          end

    3. run it against windows
       
       a. Windows:

       inspec exec first_win.rb -t winrm://vagrant@192.168.222.136 --password 'vagrant'

       b. Linux:

       inspec exec first_linux.rb -t ssh://vagrant@192.168.222.137 -i <location_to>/private_key

    .. code-block:: yaml

        verifier:
          name: inspec
          options:
            password: vagrant
            target: winrm://vagrant@192.0.2.133

    Environment variables can be passed to the verifier.

    .. code-block:: yaml

        verifier:
          name: inspec
          env:
            no_proxy: 192.0.2.133

    Change path to the test directory.

    .. code-block:: yaml

        verifier:
          name: inspec
          directory: /foo/bar/

    Additional tests from another file or directory relative to the scenario
    directory.

    .. code-block:: yaml

        verifier:
          name: inspec
          additional_files_or_dirs:
            - ../path/to/test_1
            - ../path/to/test_2
            - ../path/to/directory/

    .. _`Inspec`: https://www.inspec.io/docs/
    """

    def __init__(self, config):
        """
        Sets up the requirements to execute `inspec` and returns None.

        :param config: An instance of a Molecule config.
        :return: None
        """
        super(Inspec, self).__init__(config)
        self._inspec_command = None
        if config:
            self._tests = self._get_tests()

    @property
    def name(self):
        return 'inspec'

    @property
    def default_options(self):
        d = self._config.driver.inspec_options
        d['target'] = self._config.args.get('target')
        d['password'] = self._config.args.get('password')

        return d

    @property
    def default_env(self):
        env = self._config.merge_dicts(os.environ.copy(), self._config.env)
        env = self._config.merge_dicts(env, self._config.provisioner.env)

        return env

    @property
    def additional_files_or_dirs(self):
        return self._config.config['verifier']['additional_files_or_dirs']

    def bake(self):
        """
        Bake a `inspec` command so it's ready to execute and returns None.

        :return: None
        """
        options = self.options
        verbose_flag = util.verbose_flag(options)
        args = verbose_flag + self.additional_files_or_dirs

        # we do not want to pass connection nor ansible-inventory to the inspec command
        options.pop('connection')
        options.pop('ansible-inventory')

        self._inspec_command = sh.Command('inspec').bake(
            'exec',
            self._tests,
            options,
            _cwd=self._config.scenario.directory,
            _env=self.env,
            _out=LOG.out,
            _err=LOG.error)

    def execute(self):
        if not self.enabled:
            msg = 'Skipping, verifier is disabled.'
            LOG.warn(msg)
            return

        if not len(self._tests) > 0:
            msg = 'Skipping, no tests found.'
            LOG.warn(msg)
            return

        if self._inspec_command is None:
            self.bake()

        msg = 'Executing Inspec tests found in {}/...'.format(
            self.directory)
        LOG.info(msg)

        try:
            util.run_command(self._inspec_command, debug=self._config.debug)
            msg = 'Verifier completed successfully.'
            LOG.success(msg)

        except sh.ErrorReturnCode as e:
            util.sysexit(e.exit_code)

    def _get_tests(self):
        """
        Walk the verifier's directory for tests and returns a list.

        :return: list
        """
        return [
            filename for filename in util.os_walk(self.directory, '*.rb')
        ]

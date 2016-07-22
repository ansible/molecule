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


class AnsibleGalaxyInstall:
    def __init__(self,
                 requirements_file,
                 _env=None,
                 _out=utilities.logger.warning,
                 _err=utilities.logger.error):
        """
        Sets up requirements for ansible-galaxy

        :param requirements_file: Path to requirements file for ansible-galaxy
        :param _env: Environment dictionary to use. os.environ.copy() is used by default
        :param _out: Function passed to sh for STDOUT
        :param _err: Function passed to sh for STDERR
        :return: None
        """
        self.env = _env if _env else os.environ.copy()
        self.out = _out
        self.err = _err
        self.requirements_file = requirements_file
        self.galaxy = None

        # defaults can be redefined with call to add_env_arg() before baking
        self.add_env_arg('PYTHONUNBUFFERED', '1')
        self.add_env_arg('ANSIBLE_FORCE_COLOR', 'true')

    def bake(self):
        """
        Bake ansible-galaxy command so it's ready to execute.

        :return: None
        """
        self.galaxy = sh.ansible_galaxy.bake('install',
                                             '-f',
                                             '-r',
                                             self.requirements_file,
                                             _env=self.env,
                                             _out=self.out,
                                             _err=self.err)

    def add_env_arg(self, name, value):
        """
        Adds argument to environment passed to ansible-galaxy

        :param name: Name of argument to be added
        :param value: Value of argument to be added
        :return: None
        """
        self.env[name] = value

    def execute(self):
        """
        Executes ansible-galaxy install

        :return: sh.stdout on success, else None
        :return: None
        """
        if self.galaxy is None:
            self.bake()

        try:
            return self.galaxy().stdout
        except sh.ErrorReturnCode as e:
            utilities.logger.error('ERROR: {}'.format(e))
            utilities.sysexit(e.exit_code)

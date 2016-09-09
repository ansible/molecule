#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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

from molecule import config
from molecule import util

LOG = util.get_logger(__name__)


class AnsibleGalaxy(object):
    def __init__(self, config, _env=None, _out=LOG.info, _err=LOG.error):
        """
        Sets up requirements for ansible-galaxy, and returns None.

        :param config: A molecule config object.
        :param _env: An optional environment to pass to underlying :func:`sh`
         call.
        :param _out: An optional function to process STDOUT for underlying
         :func:`sh` call.
        :param _err: An optional function to process STDERR for underlying
         :func:`sh` call.
        :return: None
        """
        self._config = config
        self._galaxy = None
        self.env = _env if _env else os.environ.copy()
        self.out = _out
        self.err = _err

        # defaults can be redefined with call to add_env_arg() before baking
        self.add_env_arg('PYTHONUNBUFFERED', '1')
        self.add_env_arg('ANSIBLE_FORCE_COLOR', 'true')

    def bake(self):
        """
        Bake ansible-galaxy command so it's ready to execute, and returns None.

        :return: None
        """
        requirements_file = self._config['ansible']['requirements_file']
        roles_path = os.path.join(self._config['molecule']['molecule_dir'],
                                  'roles')
        galaxy_default_options = {
            'force': True,
            'role-file': requirements_file,
            'roles-path': roles_path
        }
        galaxy_options = config.merge_dicts(galaxy_default_options,
                                            self._config['ansible']['galaxy'])

        self._galaxy = sh.ansible_galaxy.bake(
            'install',
            _env=self.env,
            _out=self.out,
            _err=self.err,
            **galaxy_options)

    def add_env_arg(self, name, value):
        """
        Adds argument to environment passed to ansible-galaxy, and returns None.

        :param name: Name of argument to be added
        :param value: Value of argument to be added
        :return: None
        """
        self.env[name] = value

    def execute(self):
        """
        Executes ansible-galaxy install, and returns command's stdout.
,
        :return: The command's output, otherwise sys.exit on command failure.
        """
        if self._galaxy is None:
            self.bake()

        try:
            return self._galaxy().stdout
        except sh.ErrorReturnCode as e:
            LOG.error('ERROR: {}'.format(e))
            util.sysexit(e.exit_code)

    def install(self):
        """
        A wrapper to :meth:`.AnsibleGalaxy.execute`.
,
        .. todo:: Remove in favor of simply using execute.
        """
        util.print_info('Installing role dependencies ...')
        self.bake()
        self.execute()

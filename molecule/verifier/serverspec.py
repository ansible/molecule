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

from molecule import util
from molecule.verifier import base

LOG = util.get_logger(__name__)


class Serverspec(base.Base):
    def __init__(self, molecule):
        super(Serverspec, self).__init__(molecule)
        self._serverspec_dir = molecule.config.config['molecule'][
            'serverspec_dir']
        self._rakefile = molecule.config.config['molecule']['rakefile_file']

    def execute(self):
        """
        Executes linting/integration tests, and returns None.

        Rubocop performs the code linting.
        Rake executes serverspec integration tests.

        :return: None
        """
        serverspec_options = self._molecule.driver.serverspec_args
        serverspec_options['debug'] = self._molecule.args.get('--debug', False)

        if self._get_tests():
            self._rubocop(self._serverspec_dir, **serverspec_options)
            self._rake(self._rakefile, **serverspec_options)

    def _rake(self,
              rakefile,
              debug=False,
              env=os.environ.copy(),
              out=LOG.info,
              err=LOG.error):
        """
        Executes rake against specified rakefile, and returns a :func:`sh`
        response object.

        :param rakefile: A string containing path to the rakefile.
        :param debug: An optional bool to toggle debug output.
        :param env: An optional environment to pass to underlying :func:`sh`
         call.
        :param out: An optional function to process STDOUT for underlying
         :func:`sh` call.
        :param err: An optional function to process STDERR for underlying
         :func:`sh` call.
        :return: :func:`sh` response object.
        """
        kwargs = {'_env': env,
                  '_out': out,
                  '_err': err,
                  'trace': debug,
                  'rakefile': rakefile}

        msg = 'Executing serverspec tests found in {}/.'.format(
            self._serverspec_dir)
        util.print_info(msg)

        return sh.rake(**kwargs)

    def _rubocop(self,
                 serverspec_dir,
                 debug=False,
                 env=os.environ.copy(),
                 pattern='/**/*.rb',
                 out=LOG.info,
                 err=LOG.error):
        """
        Executes rubocop against specified directory/pattern, and returns a
        :func:`sh` response object.

        :param serverspec_dir: A string containing the directory with files
        to lint.
        :param debug: An optional bool to toggle debug output.
        :param pattern: A string containing the pattern of files to lint.
        :param env: An optional environment to pass to underlying :func:`sh`
         call.
        :param out: An optional function to process STDOUT for underlying
         :func:`sh` call.
        :param err: An optional function to process STDERR for underlying
         :func:`sh` call.
        :return: :func:`sh` response object.
        """
        kwargs = {'_env': env, '_out': out, '_err': err, 'debug': debug}

        msg = 'Executing rubocop on *.rb files found in {}/.'.format(
            serverspec_dir)
        util.print_info(msg)
        match = serverspec_dir + pattern

        return sh.rubocop(match, **kwargs)

    def _get_tests(self):
        return os.path.isdir(self._serverspec_dir)

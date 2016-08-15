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
from molecule.verifier import base

LOG = utilities.get_logger(__name__)


class Serverspec(base.Base):
    def __init__(self, molecule):
        super(Serverspec, self).__init__(molecule)
        self._serverspec_dir = molecule.config.config['molecule'][
            'serverspec_dir']
        self._rakefile = molecule.config.config['molecule']['rakefile_file']

    def execute(self):
        serverspec_options = self._molecule._driver.serverspec_args
        serverspec_options['debug'] = self._molecule._args.get('--debug',
                                                               False)

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
        Runs rake with specified rakefile.

        :param rakefile: Path to rakefile
        :param debug: Pass trace flag to rake
        :param env: Environment to pass to underlying sh call
        :param out: Function to process STDOUT for underlying sh call
        :param err: Function to process STDERR for underlying sh call
        :return: sh response object
        """
        kwargs = {'_env': env,
                  '_out': out,
                  '_err': err,
                  'trace': debug,
                  'rakefile': rakefile}

        if 'HOME' not in kwargs['_env']:
            kwargs['_env']['HOME'] = os.path.expanduser('~')

        msg = 'Executing serverspec tests found in {}/.'.format(
            self._serverspec_dir)
        utilities.print_info(msg)

        return sh.rake(**kwargs)

    def _rubocop(self,
                 serverspec_dir,
                 debug=False,
                 env=os.environ.copy(),
                 pattern='/**/*.rb',
                 out=LOG.info,
                 err=LOG.error):
        """
        Runs rubocop against specified directory with specified pattern.

        :param serverspec_dir: Directory to search for files to lint
        :param debug: Pass debug flag to rubocop
        :param pattern: Search pattern to pass to rubocop
        :param env: Environment to pass to underlying sh call
        :param out: Function to process STDOUT for underlying sh call
        :param err: Function to process STDERR for underlying sh call
        :return: sh response object
        """
        kwargs = {'_env': env, '_out': out, '_err': err, 'debug': debug}

        if 'HOME' not in kwargs['_env']:
            kwargs['_env']['HOME'] = os.path.expanduser('~')

        msg = 'Executing rubocop on *.rb files found in {}/.'.format(
            serverspec_dir)
        utilities.print_info(msg)
        match = serverspec_dir + pattern

        return sh.rubocop(match, **kwargs)

    def _get_tests(self):
        return os.path.isdir(self._serverspec_dir)

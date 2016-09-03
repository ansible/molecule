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

import glob
import os

import sh

from molecule import ansible_playbook
from molecule import util
from molecule.verifier import base

LOG = util.get_logger(__name__)


class Testinfra(base.Base):
    def __init__(self, molecule):
        super(Testinfra, self).__init__(molecule)
        self._testinfra_dir = molecule.config.config['molecule'][
            'testinfra_dir']

    def execute(self):
        """
        Executes linting/integration tests, and returns None.

        Flake8 performs the code linting.
        Testinfra executes integration tests.

        :return: None
        """
        ansible = ansible_playbook.AnsiblePlaybook(
            self._molecule.config.config['ansible'], _env=self._molecule.env)

        testinfra_options = util.merge_dicts(
            self._molecule.driver.testinfra_args,
            self._molecule.config.config['testinfra'])
        testinfra_options['env'] = ansible.env
        testinfra_options['debug'] = self._molecule.args.get('--debug', False)
        testinfra_options['sudo'] = self._molecule.args.get('--sudo', False)

        tests_glob = self._get_tests()
        if len(tests_glob) > 0:
            self._flake8(tests_glob)
            self._testinfra(tests_glob, **testinfra_options)

    def _testinfra(self,
                   tests,
                   debug=False,
                   env=os.environ.copy(),
                   out=LOG.info,
                   err=LOG.error,
                   **kwargs):
        """
        Executes testinfra against specified tests, and returns a :func:`sh`
        response object.

        :param tests: A list of testinfra tests.
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
        kwargs['debug'] = debug
        kwargs['_env'] = env
        kwargs['_out'] = out
        kwargs['_err'] = err

        msg = 'Executing testinfra tests found in {}/.'.format(
            self._testinfra_dir)
        util.print_info(msg)

        return sh.testinfra(tests, **kwargs)

    def _flake8(self, tests, out=LOG.info, err=LOG.error):
        """
        Executes flake8 against specified tests, and returns a :func:`sh`
        response object.

        :param tests: A list of testinfra tests.
        :param out: An optional function to process STDOUT for underlying
         :func:`sh` call.
        :param err: An optional function to process STDERR for underlying
         :func:`sh` call.
        :return: :func:`sh` response object.
        """
        msg = 'Executing flake8 on *.py files found in {}/.'.format(
            self._testinfra_dir)
        util.print_info(msg)

        return sh.flake8(tests)

    def _get_tests(self):
        tests = '{}/test_*.py'.format(self._testinfra_dir)

        return glob.glob(tests)

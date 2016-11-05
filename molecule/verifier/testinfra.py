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

import fnmatch
import os

import sh

from molecule import ansible_playbook
from molecule import config
from molecule import util
from molecule.verifier import base

LOG = util.get_logger(__name__)


class Testinfra(base.Base):
    def __init__(self, molecule):
        super(Testinfra, self).__init__(molecule)
        self._testinfra_dir = molecule.config.config['molecule'][
            'testinfra_dir']
        self._debug = molecule.args.get('debug')

    def execute(self):
        """
        Executes linting/integration tests and returns None.

        Flake8 performs the code linting.
        Testinfra executes integration tests.

        :return: None
        """
        ansible = ansible_playbook.AnsiblePlaybook(
            self._molecule.config.config['ansible'], {},
            _env=self._molecule.env)

        testinfra_options = config.merge_dicts(
            self._molecule.driver.testinfra_args,
            self._molecule.verifier_options)

        testinfra_options['ansible_env'] = ansible.env
        if self._molecule.args.get('debug'):
            testinfra_options['debug'] = True
        if self._molecule.args.get('sudo'):
            testinfra_options['sudo'] = True

        tests = self._get_tests()
        if len(tests) > 0:
            if 'flake8' not in self._molecule.disabled:
                self._flake8(tests)
            self._testinfra(tests, **testinfra_options)

    def _testinfra(self,
                   tests,
                   debug=False,
                   ansible_env={},
                   out=LOG.info,
                   err=LOG.error,
                   **kwargs):
        """
        Executes testinfra against specified tests and returns a :func:`sh`
        response object.

        :param tests: A list of testinfra tests.
        :param debug: An optional bool to toggle debug output.
        :param pattern: A string containing the pattern of files to lint.
        :param ansible_env: An optional environment to pass to underlying
         :func:`sh` call.
        :param out: An optional function to process STDOUT for underlying
         :func:`sh` call.
        :param err: An optional function to process STDERR for underlying
         :func:`sh` call.
        :return: :func:`sh` response object.
        """
        kwargs['debug'] = debug
        kwargs['_env'] = ansible_env
        kwargs['_out'] = out
        kwargs['_err'] = err

        msg = 'Executing testinfra tests found in {}/.'.format(
            self._testinfra_dir)
        util.print_info(msg)

        cmd = sh.testinfra.bake(tests, **kwargs)
        return util.run_command(cmd, debug=self._debug)

    def _flake8(self, tests, out=LOG.info, err=LOG.error):
        """
        Executes flake8 against specified tests and returns a :func:`sh`
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

        cmd = sh.flake8.bake(tests)
        return util.run_command(cmd, debug=self._debug)

    def _get_tests(self):
        return [
            filename
            for filename in self._walk(self._testinfra_dir, 'test_*.py')
        ]

    def _walk(self, directory, pattern):
        # Python 3.5 supports a recursive glob without needing os.walk.
        for root, dirs, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)

                    yield filename

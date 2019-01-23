#  Copyright (c) 2015-2018 Cisco Systems, Inc.
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

from molecule import logger
from molecule import util
from molecule.verifier import base

LOG = logger.get_logger(__name__)


class Inspec(base.Base):
    """
    `Inspec`_ is not the default test runner.

    `InSpec`_ is Chef's open-source language for describing security &
    compliance rules that can be shared between software engineers, operations,
    and security engineers. Your compliance, security, and other policy
    requirements become automated tests throughout all stages of the software
    delivery process. `Inspec`_ is `not` the default verifier used in Molecule.

    Molecule executes a playbook (`verify.yml`) located in the role's
    `scenario.directory`.  This playbook will copy test files to the instances,
    and execute Inspec locally over Ansible.  Molecule executes Inspec over an
    Ansible transport, in an attempt to provide Inspec support across all
    Molecule drivers.

    Additional options can be passed to ``inspec exec`` by modifying the verify
    playbook.

    The testing can be disabled by setting ``enabled`` to False.

    .. code-block:: yaml

        verifier:
          name: inspec
          enabled: False

    Environment variables can be passed to the verifier.

    .. code-block:: yaml

        verifier:
          name: inspec
          env:
            FOO: bar

    Change path to the test directory.

    .. code-block:: yaml

        verifier:
          name: inspec
          directory: /foo/bar/

    .. important::

        Due to the nature of this verifier.  Molecule does not perform options
        handling in the same fashion as Testinfra.

    .. _`Inspec`: https://www.chef.io/inspec/
    """

    def __init__(self, config):
        """
        Sets up the requirements to execute ``inspec`` and returns None.

        :param config: An instance of a Molecule config.
        :return: None
        """
        super(Inspec, self).__init__(config)
        if config:
            self._tests = self._get_tests()

    @property
    def name(self):
        return 'inspec'

    @property
    def default_options(self):
        return {}

    @property
    def default_env(self):
        return util.merge_dicts(os.environ.copy(), self._config.env)

    def bake(self):
        pass

    def execute(self):
        if not self.enabled:
            msg = 'Skipping, verifier is disabled.'
            LOG.warn(msg)
            return

        if not len(self._tests) > 0:
            msg = 'Skipping, no tests found.'
            LOG.warn(msg)
            return

        msg = 'Executing Inspec tests found in {}/...'.format(self.directory)
        LOG.info(msg)

        self._config.provisioner.verify()

        msg = 'Verifier completed successfully.'
        LOG.success(msg)

    def _get_tests(self):
        """
        Walk the verifier's directory for tests and returns a list.

        :return: list
        """
        return [
            filename for filename in util.os_walk(self.directory, 'test_*.rb')
        ]

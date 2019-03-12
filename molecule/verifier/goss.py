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


class Goss(base.Base):
    """
    `Goss`_ is not the default test runner.

    `Goss`_ is a YAML based serverspec-like tool for validating a server's
    configuration.  `Goss`_ is `not` the default verifier used in Molecule.

    Molecule executes a playbook (`verify.yml`) located in the role's
    `scenario.directory`.  This playbook will copy YAML files to the instances,
    and execute Goss using a community written Goss Ansible module bundled with
    Molecule.

    Additional options can be passed to ``goss validate`` by modifying the
    verify playbook.

    .. code-block:: yaml

        verifier:
          name: goss
          lint:
            name: yamllint

    The testing can be disabled by setting ``enabled`` to False.

    .. code-block:: yaml

        verifier:
          name: goss
          enabled: False

    Environment variables can be passed to the verifier.

    .. code-block:: yaml

        verifier:
          name: goss
          env:
            FOO: bar

    Change path to the test directory.

    .. code-block:: yaml

        verifier:
          name: goss
          directory: /foo/bar/

    All files starting with test_* will be copied to all molecule hosts.
    Files matching the regular expression `test_host_$instance_name[-.\\w].yml`
    will only run on $instance_name. If you have 2 molecule instances,
    instance1 and instance2, your test files could look like this:

    .. code-block:: bash

        test_default.yml (will run on all hosts)
        test_host_instance1.yml (will run only on instance1)
        test_host_instance2.yml (will run only on instance2)

    .. important::

        Due to the nature of this verifier.  Molecule does not perform options
        handling in the same fashion as Testinfra.

    .. _`Goss`: https://github.com/aelsabbahy/goss
    """

    def __init__(self, config):
        """
        Sets up the requirements to execute ``goss`` and returns None.

        :param config: An instance of a Molecule config.
        :return: None
        """
        super(Goss, self).__init__(config)
        if config:
            self._tests = self._get_tests()

    @property
    def name(self):
        return 'goss'

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

        msg = 'Executing Goss tests found in {}/...'.format(self.directory)
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
            filename for filename in util.os_walk(self.directory, 'test_*.yml')
        ]

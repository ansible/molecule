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
"""Testinfra Verifier Module."""

import glob
import logging
import os

from molecule import util
from molecule.api import Verifier

LOG = logging.getLogger(__name__)


class Testinfra(Verifier):
    """
    `Testinfra`_ is no longer the default test verifier since version 3.0.

    Additional options can be passed to ``testinfra`` through the options
    dict.  Any option set in this section will override the defaults.

    .. note::

        Molecule will remove any options matching '^[v]+$', and pass ``-vvv``
        to the underlying ``pytest`` command when executing ``molecule
        --debug``.

    .. code-block:: yaml

        verifier:
          name: testinfra
          options:
            n: 1

    The testing can be disabled by setting ``enabled`` to False.

    .. code-block:: yaml

        verifier:
          name: testinfra
          enabled: False

    Environment variables can be passed to the verifier.

    .. code-block:: yaml

        verifier:
          name: testinfra
          env:
            FOO: bar

    Change path to the test directory.

    .. code-block:: yaml

        verifier:
          name: testinfra
          directory: /foo/bar/

    Additional tests from another file or directory relative to the scenario's
    tests directory (supports regexp).

    .. code-block:: yaml

        verifier:
          name: testinfra
          additional_files_or_dirs:
            - ../path/to/test_1.py
            - ../path/to/test_2.py
            - ../path/to/directory/*

    .. _`Testinfra`: https://testinfra.readthedocs.io
    """

    def __init__(self, config=None):
        """
        Set up the requirements to execute ``testinfra`` and returns None.

        :param config: An instance of a Molecule config.
        :return: None
        """
        super(Testinfra, self).__init__(config)
        self._testinfra_command = None
        if config:
            self._tests = self._get_tests()

    @property
    def name(self):
        return "testinfra"

    @property
    def default_options(self):
        d = self._config.driver.testinfra_options
        d["p"] = "no:cacheprovider"
        if self._config.debug:
            d["debug"] = True
            d["vvv"] = True
        if self._config.args.get("sudo"):
            d["sudo"] = True

        return d

    # NOTE(retr0h): Override the base classes' options() to handle
    # ``ansible-galaxy`` one-off.
    @property
    def options(self):
        o = self._config.config["verifier"]["options"]
        # NOTE(retr0h): Remove verbose options added by the user while in
        # debug.
        if self._config.debug:
            o = util.filter_verbose_permutation(o)

        return util.merge_dicts(self.default_options, o)

    @property
    def default_env(self):
        env = util.merge_dicts(os.environ, self._config.env)
        env = util.merge_dicts(env, self._config.provisioner.env)

        return env

    @property
    def additional_files_or_dirs(self):
        files_list = []
        c = self._config.config
        for f in c["verifier"]["additional_files_or_dirs"]:
            glob_path = os.path.join(self._config.verifier.directory, f)
            glob_list = glob.glob(glob_path)
            if glob_list:
                files_list.extend(glob_list)

        return files_list

    def bake(self):
        """
        Bake a ``testinfra`` command so it's ready to execute and returns None.

        :return: None
        """
        options = self.options
        verbose_flag = util.verbose_flag(options)
        args = verbose_flag + self.additional_files_or_dirs

        self._testinfra_command = util.BakedCommand(
            cmd=["pytest", *util.dict2args(options), *self._tests, *args],
            cwd=self._config.scenario.directory,
            env=self.env,
        )
        # print(self._testinfra_command.cmd)

    def execute(self):
        if not self.enabled:
            msg = "Skipping, verifier is disabled."
            LOG.warning(msg)
            return

        if not len(self._tests) > 0:
            msg = "Skipping, no tests found."
            LOG.warning(msg)
            return

        if self._testinfra_command is None:
            self.bake()

        msg = "Executing Testinfra tests found in {}/...".format(self.directory)
        LOG.info(msg)

        result = util.run_command(self._testinfra_command, debug=self._config.debug)
        if result.returncode == 0:
            msg = "Verifier completed successfully."
            LOG.info(msg)
        else:
            util.sysexit(result.returncode)

    def _get_tests(self):
        """
        Walk the verifier's directory for tests and returns a list.

        :return: list
        """
        return sorted(
            [
                filename
                for filename in util.os_walk(
                    self.directory, "test_*.py", followlinks=True
                )
            ]
        )

    def schema(self):
        return {
            "verifier": {
                "type": "dict",
                "schema": {"name": {"type": "string", "allowed": ["testinfra"]}},
            }
        }
